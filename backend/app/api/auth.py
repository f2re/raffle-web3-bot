"""Telegram Mini App authentication"""

import hmac
import hashlib
import json
from typing import Dict, Optional
from urllib.parse import parse_qs

from fastapi import HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database.crud import UserCRUD


def verify_telegram_webapp_data(init_data: str) -> Dict:
    """
    Verify Telegram Mini App init data authenticity

    Args:
        init_data: Telegram init data string

    Returns:
        Parsed user data

    Raises:
        ValueError: If authentication failed
    """
    try:
        # Parse init data
        parsed = parse_qs(init_data)

        # Extract hash
        if 'hash' not in parsed:
            raise ValueError("Hash not found in init data")

        hash_value = parsed.pop('hash')[0]

        # Create data check string
        data_check_string = '\n'.join(
            f'{k}={v[0]}' for k, v in sorted(parsed.items())
        )

        # Create secret key
        secret_key = hmac.new(
            "WebAppData".encode(),
            settings.TELEGRAM_BOT_TOKEN.encode(),
            hashlib.sha256
        ).digest()

        # Calculate hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()

        # Verify hash
        if calculated_hash != hash_value:
            raise ValueError("Invalid hash")

        # Parse user data
        if 'user' not in parsed:
            raise ValueError("User data not found")

        user_data = json.loads(parsed['user'][0])
        return user_data

    except Exception as e:
        raise ValueError(f"Authentication failed: {str(e)}")


async def verify_telegram_auth(
    x_telegram_init_data: Optional[str] = Header(None),
    db: AsyncSession = None
):
    """
    FastAPI dependency for verifying Telegram authentication

    Args:
        x_telegram_init_data: Telegram init data from header
        db: Database session

    Returns:
        Authenticated user

    Raises:
        HTTPException: If authentication failed
    """
    if not x_telegram_init_data:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        # Verify init data
        user_data = verify_telegram_webapp_data(x_telegram_init_data)

        # Get or create user
        user = await UserCRUD.get_or_create(
            db,
            telegram_id=user_data['id'],
            username=user_data.get('username')
        )

        return user

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
