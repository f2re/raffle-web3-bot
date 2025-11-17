"""Raffle business logic service"""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.database.models import Raffle, RaffleType, RaffleStatus, Participant
from app.database.crud import RaffleCRUD, UserCRUD, ParticipantCRUD, TransactionCRUD
from app.services.ton_service import ton_service
from app.services.random_service import random_service
from app.config import settings


class RaffleService:
    """Service for raffle operations"""

    @staticmethod
    def get_raffle_config(raffle_type: RaffleType) -> dict:
        """Get configuration for raffle type"""
        configs = {
            RaffleType.EXPRESS: {
                "min_participants": settings.EXPRESS_MIN_PARTICIPANTS,
                "entry_fee": settings.EXPRESS_ENTRY_FEE,
                "timer_minutes": settings.EXPRESS_TIMER_MINUTES,
            },
            RaffleType.STANDARD: {
                "min_participants": settings.STANDARD_MIN_PARTICIPANTS,
                "entry_fee": settings.STANDARD_ENTRY_FEE,
                "timer_minutes": settings.STANDARD_TIMER_MINUTES,
            },
            RaffleType.PREMIUM: {
                "min_participants": settings.PREMIUM_MIN_PARTICIPANTS,
                "entry_fee": settings.PREMIUM_ENTRY_FEE,
                "timer_minutes": settings.PREMIUM_TIMER_MINUTES,
            },
        }
        return configs[raffle_type]

    @staticmethod
    async def create_raffle(db: AsyncSession, raffle_type: RaffleType) -> Raffle:
        """Create a new raffle"""
        config = RaffleService.get_raffle_config(raffle_type)

        # Calculate prize pool (entry_fee * min_participants * (1 - commission))
        total_pool = config["entry_fee"] * config["min_participants"]
        prize_pool = total_pool * (1 - settings.COMMISSION_PERCENT / 100)

        raffle = await RaffleCRUD.create(
            db,
            raffle_type=raffle_type,
            min_participants=config["min_participants"],
            entry_fee_ton=config["entry_fee"],
            prize_pool_ton=prize_pool,
            commission_percent=settings.COMMISSION_PERCENT,
        )

        await db.commit()

        logger.info(f"Created {raffle_type.value} raffle #{raffle.id}")
        return raffle

    @staticmethod
    async def join_raffle(
        db: AsyncSession,
        raffle_id: int,
        user_id: int,
        tx_hash: str
    ) -> Participant:
        """
        Join a raffle after payment verification

        Args:
            db: Database session
            raffle_id: Raffle ID
            user_id: User ID
            tx_hash: TON transaction hash

        Returns:
            Participant record

        Raises:
            ValueError: If validation fails
        """
        # Get raffle
        raffle = await RaffleCRUD.get_by_id(db, raffle_id)
        if not raffle:
            raise ValueError("Raffle not found")

        if raffle.status not in [RaffleStatus.ACTIVE, RaffleStatus.WAITING]:
            raise ValueError("Raffle is not accepting participants")

        # Check if user already joined
        existing = await ParticipantCRUD.get_by_raffle_and_user(db, raffle_id, user_id)
        if existing:
            raise ValueError("Already joined this raffle")

        # Check if transaction already used
        existing_tx = await TransactionCRUD.get_by_hash(db, tx_hash)
        if existing_tx:
            raise ValueError("Transaction already used")

        # Verify transaction
        user = await UserCRUD.get_by_id(db, user_id)
        tx_details = await ton_service.verify_transaction(
            tx_hash=tx_hash,
            expected_amount=raffle.entry_fee_ton,
            sender_wallet=user.ton_wallet
        )

        # Create transaction record
        await TransactionCRUD.create(
            db,
            user_id=user_id,
            raffle_id=raffle_id,
            tx_hash=tx_hash,
            from_wallet=tx_details["from"],
            to_wallet=tx_details["to"],
            amount_ton=tx_details["amount"],
            tx_type="entry"
        )

        # Create participant
        participant = await ParticipantCRUD.create(
            db,
            raffle_id=raffle_id,
            user_id=user_id,
            transaction_hash=tx_hash
        )

        # Update user stats
        user.total_participations += 1
        user.total_spent_ton += raffle.entry_fee_ton

        await db.commit()

        # Check if minimum participants reached
        await RaffleService.check_raffle_ready(db, raffle)

        logger.info(f"User {user_id} joined raffle #{raffle_id}")
        return participant

    @staticmethod
    async def check_raffle_ready(db: AsyncSession, raffle: Raffle):
        """Check if raffle has minimum participants and start timer"""
        if raffle.status != RaffleStatus.ACTIVE:
            return

        if raffle.current_participants >= raffle.min_participants:
            # Start timer
            config = RaffleService.get_raffle_config(raffle.type)
            raffle.status = RaffleStatus.WAITING
            raffle.waiting_until = datetime.utcnow() + timedelta(
                minutes=config["timer_minutes"]
            )

            await db.commit()

            logger.info(
                f"Raffle #{raffle.id} reached minimum participants. "
                f"Drawing at {raffle.waiting_until}"
            )

    @staticmethod
    async def draw_raffle(db: AsyncSession, raffle_id: int):
        """Execute raffle drawing"""
        raffle = await RaffleCRUD.get_by_id(db, raffle_id)
        if not raffle:
            raise ValueError("Raffle not found")

        if raffle.status != RaffleStatus.WAITING:
            raise ValueError("Raffle is not ready for drawing")

        if datetime.utcnow() < raffle.waiting_until:
            raise ValueError("Timer not expired yet")

        # Update status
        raffle.status = RaffleStatus.DRAWING
        await db.commit()

        try:
            # Pick winner using Random.org
            num_participants = len(raffle.participants)
            random_result = await random_service.pick_winner(num_participants)

            winner_index = random_result["winner_index"]
            winner_participant = raffle.participants[winner_index]

            # Update raffle
            raffle.winner_id = winner_participant.user_id
            raffle.random_org_signature = random_result["signature"]
            raffle.random_org_url = random_result["verification_url"]
            raffle.drawn_at = datetime.utcnow()
            raffle.status = RaffleStatus.COMPLETED

            # Update participant
            winner_participant.is_winner = True

            # Update winner stats
            winner = await UserCRUD.get_by_id(db, winner_participant.user_id)
            winner.total_wins += 1
            winner.total_won_ton += raffle.prize_pool_ton

            await db.commit()

            logger.info(
                f"Raffle #{raffle_id} drawn. Winner: user {winner.id} "
                f"(index {winner_index})"
            )

            # Send prize (async task)
            if winner.ton_wallet:
                await RaffleService.send_prize(db, raffle, winner_participant)

            # Create new raffle of same type
            await RaffleService.create_raffle(db, raffle.type)

        except Exception as e:
            raffle.status = RaffleStatus.WAITING
            await db.commit()
            logger.error(f"Failed to draw raffle #{raffle_id}: {e}")
            raise

    @staticmethod
    async def send_prize(
        db: AsyncSession,
        raffle: Raffle,
        winner_participant: Participant
    ):
        """Send prize to winner"""
        try:
            winner = await UserCRUD.get_by_id(db, winner_participant.user_id)

            if not winner.ton_wallet:
                logger.error(f"Winner {winner.id} has no wallet connected")
                return

            # Send prize
            tx_hash = await ton_service.send_prize(
                recipient_wallet=winner.ton_wallet,
                amount_ton=raffle.prize_pool_ton
            )

            # Update participant
            winner_participant.prize_sent = True
            winner_participant.prize_tx_hash = tx_hash

            # Create transaction record
            await TransactionCRUD.create(
                db,
                user_id=winner.id,
                raffle_id=raffle.id,
                tx_hash=tx_hash,
                from_wallet=settings.RAFFLE_WALLET_ADDRESS,
                to_wallet=winner.ton_wallet,
                amount_ton=raffle.prize_pool_ton,
                tx_type="prize"
            )

            await db.commit()

            logger.info(f"Sent {raffle.prize_pool_ton} TON to winner {winner.id}")

        except Exception as e:
            logger.error(f"Failed to send prize: {e}")


# Global raffle service instance
raffle_service = RaffleService()
