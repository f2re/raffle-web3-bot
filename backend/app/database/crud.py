"""CRUD operations for database models"""

from typing import Optional, List
from datetime import datetime

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import User, Raffle, Participant, Transaction, RaffleType, RaffleStatus


class UserCRUD:
    """CRUD operations for User model"""

    @staticmethod
    async def get_by_telegram_id(db: AsyncSession, telegram_id: int) -> Optional[User]:
        """Get user by telegram ID"""
        result = await db.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, telegram_id: int, username: Optional[str] = None) -> User:
        """Create new user"""
        user = User(
            telegram_id=telegram_id,
            username=username,
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow(),
        )
        db.add(user)
        await db.flush()
        return user

    @staticmethod
    async def get_or_create(db: AsyncSession, telegram_id: int, username: Optional[str] = None) -> User:
        """Get existing user or create new one"""
        user = await UserCRUD.get_by_telegram_id(db, telegram_id)
        if not user:
            user = await UserCRUD.create(db, telegram_id, username)
        else:
            # Update last active
            user.last_active = datetime.utcnow()
            if username:
                user.username = username
        return user


class RaffleCRUD:
    """CRUD operations for Raffle model"""

    @staticmethod
    async def get_by_id(db: AsyncSession, raffle_id: int) -> Optional[Raffle]:
        """Get raffle by ID with participants"""
        result = await db.execute(
            select(Raffle)
            .options(selectinload(Raffle.participants))
            .where(Raffle.id == raffle_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_active_by_type(db: AsyncSession, raffle_type: RaffleType) -> Optional[Raffle]:
        """Get active raffle by type"""
        result = await db.execute(
            select(Raffle)
            .options(selectinload(Raffle.participants))
            .where(Raffle.type == raffle_type)
            .where(Raffle.status.in_([RaffleStatus.ACTIVE, RaffleStatus.WAITING]))
            .order_by(Raffle.created_at.desc())
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_active(db: AsyncSession) -> List[Raffle]:
        """Get all active raffles"""
        result = await db.execute(
            select(Raffle)
            .options(selectinload(Raffle.participants))
            .where(Raffle.status.in_([RaffleStatus.ACTIVE, RaffleStatus.WAITING]))
            .order_by(Raffle.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def create(
        db: AsyncSession,
        raffle_type: RaffleType,
        min_participants: int,
        entry_fee_ton: float,
        prize_pool_ton: float,
        commission_percent: float = 10.0,
    ) -> Raffle:
        """Create new raffle"""
        raffle = Raffle(
            type=raffle_type,
            status=RaffleStatus.ACTIVE,
            min_participants=min_participants,
            entry_fee_ton=entry_fee_ton,
            prize_pool_ton=prize_pool_ton,
            commission_percent=commission_percent,
            created_at=datetime.utcnow(),
        )
        db.add(raffle)
        await db.flush()
        return raffle


class ParticipantCRUD:
    """CRUD operations for Participant model"""

    @staticmethod
    async def create(
        db: AsyncSession,
        raffle_id: int,
        user_id: int,
        transaction_hash: Optional[str] = None,
    ) -> Participant:
        """Create new participant"""
        participant = Participant(
            raffle_id=raffle_id,
            user_id=user_id,
            transaction_hash=transaction_hash,
            joined_at=datetime.utcnow(),
        )
        db.add(participant)
        await db.flush()
        return participant

    @staticmethod
    async def get_by_raffle_and_user(
        db: AsyncSession, raffle_id: int, user_id: int
    ) -> Optional[Participant]:
        """Check if user is already participant"""
        result = await db.execute(
            select(Participant)
            .where(Participant.raffle_id == raffle_id)
            .where(Participant.user_id == user_id)
        )
        return result.scalar_one_or_none()


class TransactionCRUD:
    """CRUD operations for Transaction model"""

    @staticmethod
    async def create(
        db: AsyncSession,
        user_id: int,
        tx_hash: str,
        from_wallet: str,
        to_wallet: str,
        amount_ton: float,
        tx_type: str,
        raffle_id: Optional[int] = None,
    ) -> Transaction:
        """Create new transaction"""
        transaction = Transaction(
            user_id=user_id,
            raffle_id=raffle_id,
            tx_hash=tx_hash,
            from_wallet=from_wallet,
            to_wallet=to_wallet,
            amount_ton=amount_ton,
            type=tx_type,
            created_at=datetime.utcnow(),
        )
        db.add(transaction)
        await db.flush()
        return transaction

    @staticmethod
    async def get_by_hash(db: AsyncSession, tx_hash: str) -> Optional[Transaction]:
        """Get transaction by hash"""
        result = await db.execute(
            select(Transaction).where(Transaction.tx_hash == tx_hash)
        )
        return result.scalar_one_or_none()
