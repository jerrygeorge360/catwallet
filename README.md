
# CatWallet
CatWallet is a decentralized application (DApp) developed for a hackathon, designed to manage blockchain assets and transactions within the Cartesi ecosystem. It utilizes the CartesiNexus library to handle various operations, including asset management, ABI encoding/decoding, and token transactions.

# Purpose
CatWallet aims to showcase the practical application of the [CartesiNexus library](https://github.com/jerrygeorge360/cartesi-nexus)by integrating it into a functional DApp. The project demonstrates the ability to manage assets, handle token transactions, and perform ABI encoding/decoding, providing a comprehensive example of working within the Cartesi ecosystem.

# Features
- Asset Management: Manage Ether, ERC20, and ERC721 tokens.
- Transaction Handling: Perform deposits, transfers, and withdrawals of assets.
- ABI Encoding/Decoding: Encode and decode ABI payloads for smart contract interactions.
- Integration with CartesiNexus: Leverage the CartesiNexus library for blockchain operations.

```bash
Copy code
git clone https://github.com/jerrygeorge360/catwallet
pip install requirements.txt
cartesi build
cartesi run
```
### Dependencies
- CartesiNexus Library: Ensure that the CartesiNexus library is installed.
- Requests Library: For making HTTP requests.
- Other dependencies: Listed in requirements.txt.
### Usage
To use CatWallet, follow these steps:

Set Up CartesiNexus

Ensure the CartesiNexus library is installed and properly configured. The library provides functions for managing blockchain assets and transactions.

Import Necessary Methods

Import the required methods from CartesiNexus and use them within CatWallet:


contributing
Contributions to CatWallet are welcome. If you have suggestions, improvements, or bug fixes, please submit a pull request or open an issue on GitHub.

[link to the cartesi-nexus library](https://github.com/jerrygeorge360/cartesi-nexus)