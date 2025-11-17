"""Scheduler service for automated tasks"""

from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.database.session import AsyncSessionLocal
from app.database.models import RaffleStatus
from app.database.crud import RaffleCRUD
from app.services.raffle_service import raffle_service
from app.api.websocket import websocket_manager


class SchedulerService:
    """Service for scheduling automated tasks"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    def start(self):
        """Start scheduler"""
        # Check for raffles ready to draw (every 10 seconds)
        self.scheduler.add_job(
            self.check_raffles_ready_to_draw,
            trigger=IntervalTrigger(seconds=10),
            id="check_raffles_ready",
            replace_existing=True
        )

        # Check transaction statuses (every 5 seconds)
        # self.scheduler.add_job(
        #     self.check_transaction_statuses,
        #     trigger=IntervalTrigger(seconds=5),
        #     id="check_transactions",
        #     replace_existing=True
        # )

        self.scheduler.start()
        logger.info("Scheduler started")

    def stop(self):
        """Stop scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")

    async def check_raffles_ready_to_draw(self):
        """Check for raffles with expired timers"""
        try:
            async with AsyncSessionLocal() as db:
                # Get all waiting raffles
                raffles = await RaffleCRUD.get_all_active(db)

                for raffle in raffles:
                    if raffle.status != RaffleStatus.WAITING:
                        continue

                    if raffle.waiting_until and datetime.utcnow() >= raffle.waiting_until:
                        logger.info(f"Raffle #{raffle.id} timer expired, starting draw")

                        try:
                            # Execute drawing
                            await raffle_service.draw_raffle(db, raffle.id)

                            # Broadcast completion
                            await websocket_manager.broadcast_raffle_completed(
                                raffle_id=raffle.id,
                                winner_id=raffle.winner_id
                            )

                        except Exception as e:
                            logger.error(f"Failed to draw raffle #{raffle.id}: {e}")

        except Exception as e:
            logger.error(f"Error checking raffles ready to draw: {e}")

    async def check_transaction_statuses(self):
        """Check pending transaction statuses"""
        # TODO: Implement transaction status checking
        pass


# Global scheduler instance
scheduler_service = SchedulerService()
