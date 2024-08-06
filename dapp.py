import json
import logging
import requests
from os import environ
from cartesi_nexus import (
    deposit,
    str2hex,
    hex2str,
    withdraw,
    transfer_token,
    output,
    FuncSel,
    get_token,
    get_all_tokens,
)

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

rollup_server = environ["ROLLUP_HTTP_SERVER_URL"]
logger.info(f"HTTP rollup server URL is {rollup_server}")

# Run the command cartesi address-book to get it
dapp_relay_address = "0xF5DE34d6BbC0446E2a45719E718efEbaaE179daE".strip()
ether_portal_address = "0xFfdbe43d4c855BF7e0f105c400A50857f53AB044".strip()
erc20_portal_address = "0x9C21AEb2093C32DDbC53eEF24B873BDCd1aDa1DB".strip()
erc721_portal_address = "0x237F8DD094C0e47f4236f12b4Fa01d6Dae89fb87".strip()

rollup_address = ""


def set_roll_up_address(msg_sender: str, payload: str):
    global rollup_address
    if msg_sender.lower() == dapp_relay_address.lower():
        logger.info("Received advance from dapp relay")
        rollup_address = payload
        notice = output('notice', {"payload": f"Set rollup address {rollup_address}"}).payload
        response = requests.post(f"{rollup_server}/notice", json=notice)
        return 'accept'


def asset_watch_deposit(msg_sender: str, payload: str):
    try:
        if msg_sender.lower() == ether_portal_address.lower():
            notice = deposit('eth', payload=payload)
        elif msg_sender.lower() == erc20_portal_address.lower():
            notice = deposit('erc20', payload=payload)
        elif msg_sender.lower() == erc721_portal_address.lower():
            notice = deposit('erc721', payload=payload)
        else:
            return "reject"

        response = requests.post(f"{rollup_server}/notice", json=notice.payload)
        logger.info(f"Received notice status {response.status_code} body {response.content}")
        return "accept"
    except Exception as error:
        error_msg = f"Failed to process deposit command '{payload}'. {error}"
        logger.error(error_msg, exc_info=True)
        requests.post(f"{rollup_server}/report", json=output("error", {"payload": error}))
        return "reject"


def asset_watch_transfer(payload: str):
    try:
        data = json.loads(bytes.fromhex(payload[2:]).decode("utf-8"))
        if data["method"] == "ether_transfer":
            response = transfer_token("eth", payload)
        elif data["method"] == "erc20_transfer":
            response = transfer_token("erc20", payload)
        elif data["method"] == "erc721_transfer":
            response = transfer_token("erc721", payload)
        else:
            return "reject"

        requests.post(f"{rollup_server}/notice", json=response)
        return "accept"
    except Exception as error:
        error_msg = f"Failed to process transfer command '{payload}'. {error}"
        logger.error(error_msg, exc_info=True)
        requests.post(f"{rollup_server}/report", json=output("report", {"payload": error}))
        return "reject"


def asset_watch_withdraw(payload: str):
    try:
        data = json.loads(bytes.fromhex(payload[2:]).decode("utf-8"))
        amount = int(data["amount"]) if isinstance(data["amount"], str) and data["amount"].isdigit() else data["amount"]

        if data["method"] == "ether_withdraw":
            voucher = withdraw(FuncSel.ETHER, rollup_address, amount)
        elif data["method"] == "erc20_withdraw":
            voucher = withdraw(FuncSel.ERC_20, rollup_address, amount)
        elif data["method"] == "erc721_withdraw":
            voucher = withdraw(FuncSel.ERC_721, rollup_address, amount)
        else:
            return "reject"

        requests.post(f"{rollup_server}/notice", json=voucher)
        return "accept"
    except Exception as error:
        error_msg = f"Failed to process withdraw command '{payload}'. {error}"
        logger.error(error_msg, exc_info=True)
        requests.post(f"{rollup_server}/report", json=output("report", {"payload": error}))
        return "reject"


def handle_advance(data):
    logger.info(f"Received advance request data {data}")
    msg_sender = data['metadata']['msg_sender']
    payload = data['payload']
    if set_roll_up_address(msg_sender, payload) == 'accept':
        return "accept"
    elif asset_watch_deposit(msg_sender, payload) == 'accept':
        return "accept"
    elif asset_watch_transfer(payload) == 'accept':
        return "accept"
    elif asset_watch_withdraw(payload) == 'accept':
        return "accept"
    return "reject"


def get_balance(method: str, account: str):
    if method.lower() == 'get_ether':
        amount = get_token(account)
    elif method.lower() == 'get_erc20':
        amount = get_token(account)
    elif method.lower() == 'get_erc721':
        amount = get_token(account)
    elif method.lower() == 'get_all':
        amount = get_all_tokens(account)
    else:
        return "reject"

    report = output("report", {"payload": {"method": method.lower(), "amount": amount}})
    response = requests.post(f"{rollup_server}/report", json=report)
    logger.info(f"Received report status {response.status_code} body {response.content}")
    return "accept"


def handle_inspect(data: str):
    try:
        data = hex2str(json.loads(data))
        method = data['method']
        account = data['payload']['account']
        if get_balance(method, account) == 'accept':
            return "accept"
        else:
            return 'reject'
    except Exception as error:
        error_msg = f"Failed to process inspect request. {error}"
        logger.error(error_msg, exc_info=True)
        return "reject"


handlers = {
    "advance_state": handle_advance,
    "inspect_state": handle_inspect,
}

finish = {"status": "accept"}

while True:
    logger.info("Sending finish")
    response = requests.post(f"{rollup_server}/finish", json=finish)
    logger.info(f"Received finish status {response.status_code}")
    if response.status_code == 202:
        logger.info("No pending rollup request, trying again")
    else:
        rollup_request = response.json()
        handler = handlers[rollup_request["request_type"]]
        finish["status"] = handler(rollup_request["data"])
