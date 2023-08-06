import statistics
from typing import Optional, Union

from eth_typing.encoding import HexStr
from eth_typing.evm import Address, ChecksumAddress
from tokens import ABI
from web3 import Web3
from web3.exceptions import InvalidAddress
from web3.middleware.signing import construct_sign_and_send_raw_middleware
from web3.providers.base import BaseProvider
from web3.types import TxParams, TxReceipt, Wei

from .types import TFeesByPriority, TPriority


class Wallet:
    def __init__(
        self, provider: BaseProvider, address: ChecksumAddress, private_key: HexStr
    ):
        """Initialize Wallet.

        Args:
            provider (BaseProvider): Provider instance to pass to Web3
            address (str): wallet address
            private_key (str): wallet private key
        """
        self.address = address
        self.web3 = Web3(provider)
        # Verify successfully connected
        if not self.web3.isConnected():
            raise ConnectionError("Could not connect to the network")
        # Verify if provided address is a valid eth address
        if not self.web3.isChecksumAddress(self.address):
            raise InvalidAddress(
                f"Provided {self.address} address is not valid. Please provide valid"
                " wallet address."
            )
        self.web3.middleware_onion.add(
            construct_sign_and_send_raw_middleware(private_key)
        )
        self.web3.eth.default_account = self.address

    def estimate_gas_fee(
        self, priority: Optional[TPriority] = None
    ) -> Union[Wei, TFeesByPriority]:
        """Estimate gas fee per gas.

        Args:
            priority (TPriority, optional):
              If specified return an amount of fees in Wei for given priority.
              If not specified return a dict where keys are of type TPriority and values
              are gas fees per gas in Wei. Defaults to None.
        """
        base_fee_percentage_multiplier = {
            "low": 1.10,  # 10% increase
            "medium": 1.20,  # 20% increase
            "high": 1.25,  # 25% increase
        }

        priority_fee_percentage_multiplier = {
            "low": 0.94,  # 6% decrease
            "medium": 0.97,  # 3% decrease
            "high": 0.98,  # 2% decrease
        }

        minimum_fee = {"low": 1000000000, "medium": 1500000000, "high": 2000000000}

        fee_by_priority = {"low": [], "medium": [], "high": []}
        # Number of  blocks - 5
        # newest block in the provided range -
        #    latest [or you can give the latest block number]
        # reward_percentiles - 10,20,30 [ based on metamask]
        fee_history = self.web3.eth.fee_history(5, "latest", [10, 20, 30])
        # Get the base fee of the latest block
        latest_base_fee_per_gas = fee_history["baseFeePerGas"][-1]
        # The reward parameter in feeHistory variable contains an array of arrays.
        # each of the inner arrays has priority gas values,
        # corresponding to the given percentiles [10,20,30]
        # the number of inner arrays =
        #     the number of blocks that we gave as the parameter[5]
        # here we take each of the inner arrays and
        # sort the values in the arrays as low, medium or high,
        # based on the array index
        for fee_list in fee_history["reward"]:
            # 10 percentile values - low fees
            fee_by_priority["low"].append(fee_list[0])
            # 20 percentile value - medium fees
            fee_by_priority["medium"].append(fee_list[1])
            # 30 percentile value - high fees
            fee_by_priority["high"].append(fee_list[2])
        # Take each of the sorted arrays in the feeByPriority dictionary and
        # calculate the gas estimate, based on the priority level
        # that is given as the key in the feeByPriority dictionary
        gas_fee_per_gas_by_priority: TFeesByPriority = {}  # type: ignore
        for key in fee_by_priority:
            # adjust the basefee,
            # use the multiplier value corresponding to the key
            adjusted_base_fee = (
                latest_base_fee_per_gas * base_fee_percentage_multiplier[key]
            )
            # get the median of the priority fee based on the key
            median_of_fee_list = statistics.median(fee_by_priority[key])
            # adjust the median value,
            # use the multiplier value corresponding to the key
            adjusted_fee_median = (
                median_of_fee_list * priority_fee_percentage_multiplier[key]
            )
            # if the adjustedFeeMedian falls below the minimum_fee,
            # use the minimum_fee value,
            adjusted_fee_median = (
                adjusted_fee_median
                if adjusted_fee_median > minimum_fee[key]
                else minimum_fee[key]
            )
            # calculate the Max fee per gas
            suggested_max_fee_per_gas = adjusted_base_fee + adjusted_fee_median
            # need to round in order for web3 not to throw error later
            gas_fee_per_gas_by_priority[key] = round(suggested_max_fee_per_gas)

        if priority:
            return gas_fee_per_gas_by_priority[priority]
        return gas_fee_per_gas_by_priority

    def send_token(
        self,
        token_address: Address,
        to_address: Address,
        amount: Wei,
        priority: TPriority = "low",
    ) -> TxReceipt:
        """Send token.

        Args:
            token_address (Address): Token address
            to_address (Address): Address of a reciever
            amount (Wei): amount of tokens to send in Wei
            priority (TPriority): transaction priority
              Possible values: low, medium, high

        Returns:
            TxReceipt: Transaction receipt.
        """
        checksumAddress = self.web3.toChecksumAddress(token_address)
        contract = self.web3.eth.contract(address=checksumAddress, abi=ABI)
        transaction = contract.functions.transfer(to_address, amount)
        gas_estimate: TxParams = {
            "gasPrice": self.estimate_gas_fee(priority),
            "gas": transaction.estimate_gas(),  # type: ignore
        }
        transaction = transaction.build_transaction(gas_estimate)
        tx_hash = self.web3.eth.send_transaction(transaction)
        tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt

    def send_eth(
        self, to_address: Address, amount: Wei, priority: TPriority = "low"
    ) -> TxReceipt:
        """Send ETH.

        Args:
            to_address (Address): Reciever address.
            amount (Wei): amount of eth in Wei
            priority (TPriority, optional): Transaction priority.
              Possible values: low, medium, high. Defaults to 'low'.

        Returns:
            TxReceipt: Transaction receipt.
        """
        transaction: TxParams = {
            "to": to_address,
            "value": amount,
        }
        transaction["gas"] = self.web3.eth.estimate_gas(transaction)
        transaction["gasPrice"] = round(self.estimate_gas_fee(priority))  # type: ignore

        tx_hash = self.web3.eth.send_transaction(transaction)
        tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt

    def send(
        self,
        to_address: Address,
        amount: Wei,
        priority: TPriority = "low",
        token_address: Optional[Address] = None,
    ) -> TxReceipt:
        """Send cryptocurrency.

        Args:
            to_address (Address): Address of a reciever
            amount (Wei): amount to send in Wei
            priority (TPriority): Transaction priority.
              Possible values: low, medium, high. Defaults to 'low'.
            token_address (Address, optional):
              If specified transaction will be treated as token transfer.
              If not specified transaction will be treated as ETH transfer.
              Defaults to None.

        Returns:
            TxReceipt: Transaction receipt.
        """
        if to_address:
            return self.send_token(
                token_address, to_address, amount, priority  # type: ignore
            )
        return self.send_eth(to_address, amount, priority)  # type: ignore

    def get_eth_balance(self) -> Wei:
        """Get ETH balance.

        Returns:
            Wei: balance in Wei
        """
        balance = self.web3.eth.get_balance(self.address)
        return balance

    def get_token_balance(self, token_address: Address) -> Wei:
        """Get balance on ERC20 token

        Args:
            token_address (Address): Address of a token

        Returns:
           Wei: balance in Wei
        """
        checksumAddress = self.web3.toChecksumAddress(token_address)
        contract = self.web3.eth.contract(address=checksumAddress, abi=ABI)
        balance = contract.functions.balanceOf(self.address).call()
        return balance

    def get_balance(self, token_address: Optional[Address] = None) -> Wei:
        """Get balance.

        Args:
            token_address (Optional[Address], optional):
              If specified will return balance for a provided token address.
              If not specified will return ETH balance.
              Defaults to None.

        Returns:
            Wei: balance in Wei.
        """
        if token_address:
            return self.get_token_balance(token_address)
        return self.get_eth_balance()


__all__ = ["Wallet"]
