"""TON Blockchain service"""

import asyncio
from typing import Optional, Dict
import aiohttp
from loguru import logger

from app.config import settings


class TONService:
    """Service for interacting with TON blockchain"""

    def __init__(self):
        self.api_url = "https://toncenter.com/api/v2"
        self.api_key = settings.TON_CENTER_API_KEY
        self.raffle_wallet = settings.RAFFLE_WALLET_ADDRESS

    async def verify_transaction(
        self,
        tx_hash: str,
        expected_amount: float,
        sender_wallet: Optional[str] = None
    ) -> Dict:
        """
        Verify TON transaction

        Args:
            tx_hash: Transaction hash
            expected_amount: Expected amount in TON
            sender_wallet: Expected sender wallet address (optional)

        Returns:
            Transaction details if valid

        Raises:
            ValueError: If transaction is invalid
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Get transaction details
                url = f"{self.api_url}/getTransactions"
                params = {
                    "address": self.raffle_wallet,
                    "limit": 100,
                    "api_key": self.api_key
                }

                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        raise ValueError("Failed to fetch transactions")

                    data = await response.json()

                    if not data.get("ok"):
                        raise ValueError("API returned error")

                    transactions = data.get("result", [])

                    # Find matching transaction
                    for tx in transactions:
                        if tx.get("transaction_id", {}).get("hash") == tx_hash:
                            # Verify amount
                            in_msg = tx.get("in_msg", {})
                            amount_nano = int(in_msg.get("value", 0))
                            amount_ton = amount_nano / 1_000_000_000

                            if abs(amount_ton - expected_amount) > 0.01:
                                raise ValueError(
                                    f"Amount mismatch: expected {expected_amount}, got {amount_ton}"
                                )

                            # Verify destination
                            if in_msg.get("destination") != self.raffle_wallet:
                                raise ValueError("Wrong destination wallet")

                            # Verify sender (if provided)
                            if sender_wallet:
                                tx_sender = in_msg.get("source")
                                if tx_sender != sender_wallet:
                                    raise ValueError("Sender wallet mismatch")

                            return {
                                "hash": tx_hash,
                                "from": in_msg.get("source"),
                                "to": in_msg.get("destination"),
                                "amount": amount_ton,
                                "confirmed": True
                            }

                    raise ValueError("Transaction not found")

        except Exception as e:
            logger.error(f"Transaction verification failed: {e}")
            raise ValueError(f"Transaction verification failed: {str(e)}")

    async def send_prize(
        self,
        recipient_wallet: str,
        amount_ton: float
    ) -> str:
        """
        Send prize to winner

        Args:
            recipient_wallet: Winner's wallet address
            amount_ton: Amount to send in TON

        Returns:
            Transaction hash

        Note:
            This is a placeholder. In production, you would use
            pytoniq or tonsdk to sign and send transactions.
        """
        logger.info(f"Sending {amount_ton} TON to {recipient_wallet}")

        # TODO: Implement actual transaction sending
        # This requires:
        # 1. Load wallet from mnemonic
        # 2. Create and sign transaction
        # 3. Send to network
        # 4. Return transaction hash

        # Placeholder return
        return f"placeholder_tx_hash_{recipient_wallet}_{amount_ton}"

    async def get_wallet_balance(self, wallet_address: str) -> float:
        """
        Get wallet balance in TON

        Args:
            wallet_address: Wallet address

        Returns:
            Balance in TON
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}/getAddressBalance"
                params = {
                    "address": wallet_address,
                    "api_key": self.api_key
                }

                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        raise ValueError("Failed to fetch balance")

                    data = await response.json()

                    if not data.get("ok"):
                        raise ValueError("API returned error")

                    balance_nano = int(data.get("result", 0))
                    balance_ton = balance_nano / 1_000_000_000

                    return balance_ton

        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return 0.0


# Global TON service instance
ton_service = TONService()
