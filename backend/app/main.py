"""Main application entry point"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from loguru import logger

from app.config import settings
from app.database.session import init_db, close_db
from app.api.routes import router as api_router
from app.api.websocket import websocket_manager
from app.services.scheduler_service import scheduler_service
from app.bot.handlers import start


# Initialize bot
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan"""
    logger.info("Starting application...")

    # Register bot handlers (do this in lifespan to avoid reload issues)
    if not start.router._parent_router:  # Only attach if not already attached
        dp.include_router(start.router)

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Start scheduler
    scheduler_service.start()

    # Start bot polling in background
    asyncio.create_task(dp.start_polling(bot))
    logger.info("Bot started")

    yield

    # Cleanup
    logger.info("Shutting down application...")
    scheduler_service.stop()
    await close_db()
    await bot.session.close()


# Create FastAPI app
app = FastAPI(
    title="Web3 Raffle Bot API",
    description="API for Web3 Raffle Telegram Mini App",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket_manager.connect(websocket)

    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back for ping/pong
            await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        websocket_manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower()
    )
