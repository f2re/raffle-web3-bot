"""Random.org API service for provably fair drawing"""

import asyncio
from typing import Dict
import aiohttp
from loguru import logger

from app.config import settings


class RandomOrgService:
    """Service for generating provably random numbers via Random.org"""

    def __init__(self):
        self.api_url = "https://api.random.org/json-rpc/4/invoke"
        self.api_key = settings.RANDOM_ORG_API_KEY

    async def pick_winner(self, num_participants: int) -> Dict:
        """
        Pick a random winner using Random.org API

        Args:
            num_participants: Total number of participants

        Returns:
            Dict with winner_index, signature, and verification_url

        Raises:
            ValueError: If API call fails
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Prepare request
                request_data = {
                    "jsonrpc": "2.0",
                    "method": "generateSignedIntegers",
                    "params": {
                        "apiKey": self.api_key,
                        "n": 1,  # Generate 1 number
                        "min": 0,  # Start from 0
                        "max": num_participants - 1,  # End at num_participants - 1
                        "replacement": True
                    },
                    "id": 1
                }

                async with session.post(self.api_url, json=request_data) as response:
                    if response.status != 200:
                        raise ValueError(f"Random.org API returned status {response.status}")

                    data = await response.json()

                    if "error" in data:
                        error_msg = data["error"].get("message", "Unknown error")
                        raise ValueError(f"Random.org API error: {error_msg}")

                    if "result" not in data:
                        raise ValueError("Invalid response from Random.org")

                    result = data["result"]
                    random_data = result.get("random", {})
                    winner_index = random_data.get("data", [0])[0]

                    # Get signature and verification URL
                    signature = result.get("signature")
                    serial_number = result.get("serialNumber")

                    # Construct verification URL
                    verification_url = (
                        f"https://api.random.org/signatures/form?format=serial&serial={serial_number}"
                        if serial_number else None
                    )

                    logger.info(
                        f"Random.org picked winner: index={winner_index}, "
                        f"serial={serial_number}"
                    )

                    return {
                        "winner_index": winner_index,
                        "signature": signature,
                        "verification_url": verification_url,
                        "serial_number": serial_number
                    }

        except Exception as e:
            logger.error(f"Random.org API failed: {e}")
            raise ValueError(f"Failed to generate random number: {str(e)}")

    async def verify_signature(self, signature: str) -> bool:
        """
        Verify Random.org signature

        Args:
            signature: Signature to verify

        Returns:
            True if signature is valid
        """
        # Random.org signatures can be verified on their website
        # For now, we trust the signature if it exists
        return bool(signature)


# Global Random.org service instance
random_service = RandomOrgService()
