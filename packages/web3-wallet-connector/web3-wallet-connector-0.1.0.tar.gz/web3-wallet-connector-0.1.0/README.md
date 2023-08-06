# Web3 Token Connector

Python library that facilitates interaction with ethereum wallet address.

## Usage

### Create an instance of a ```Wallet``` class
Instantiate with any web3 provider accepted by Web3 class:
```python
from web3.providers.websocket import WebsocketProvider
from web3_wallet_connector import Wallet

provider = WebsocketProvider("wss://<node_address_here>")
wallet_checksum_address = "<your_address_here>"
wallet_private_key = "<your_private_key>"

wallet = Wallet(provider, wallet_checksum_address, wallet_private_key)
```
### Send ETH or ERC20 tokens
Send ETH:

```python
to_address = "<recipient_address_here>"
# Amount in Wei
amount = 10000000
# Transaction priority (low, medium or high)
priority = "medium"

# Returns transaction receipt
tx_receipt = wallet.send(to_address, amount, priority)
```
Send ERC20 token:
```python
to_address = "<recipient_address_here>"
# Amount in Wei
amount = 10000000
# Transaction priority (low, medium or high)
priority = "medium"
# Example: MANA token eth address
token_address = "0x0f5d2fb29fb7d3cfee444a200298f468908cc942"

# Returns transaction receipt
tx_receipt = wallet.send(to_address, amount, priority, token_address)
```
### Get ETH or ERC20 token balance
Get ETH balance:
```python
balance = wallet.get_balance()
```
Get ERC20 token balance:
```python
# Example: MANA token eth address
token_address = "0x0f5d2fb29fb7d3cfee444a200298f468908cc942"

balance = wallet.get_balance(token_address)
```
