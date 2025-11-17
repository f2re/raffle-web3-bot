"""Initialize raffles on startup"""

import asyncio
from loguru import logger

from app.database.session import AsyncSessionLocal
from app.database.models import RaffleType
from app.database.crud import RaffleCRUD
from app.services.raffle_service import raffle_service


async def init_raffles():
    """Create initial raffles for each type if they don't exist"""
    async with AsyncSessionLocal() as db:
        try:
            # Check and create EXPRESS raffle
            express_raffle = await RaffleCRUD.get_active_by_type(db, RaffleType.EXPRESS)
            if not express_raffle:
                await raffle_service.create_raffle(db, RaffleType.EXPRESS)
                logger.info("Created EXPRESS raffle")

            # Check and create STANDARD raffle
            standard_raffle = await RaffleCRUD.get_active_by_type(db, RaffleType.STANDARD)
            if not standard_raffle:
                await raffle_service.create_raffle(db, RaffleType.STANDARD)
                logger.info("Created STANDARD raffle")

            # Check and create PREMIUM raffle
            premium_raffle = await RaffleCRUD.get_active_by_type(db, RaffleType.PREMIUM)
            if not premium_raffle:
                await raffle_service.create_raffle(db, RaffleType.PREMIUM)
                logger.info("Created PREMIUM raffle")

            await db.commit()
            logger.info("Raffle initialization completed")

        except Exception as e:
            logger.error(f"Failed to initialize raffles: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(init_raffles())
