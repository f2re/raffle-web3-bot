"""WebSocket manager for real-time updates"""

from typing import List
from fastapi import WebSocket
from loguru import logger


class ConnectionManager:
    """WebSocket connection manager"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []

        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to broadcast to client: {e}")
                disconnected.append(connection)

        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

    async def broadcast_raffle_update(self, raffle_id: int, raffle_data: dict):
        """Broadcast raffle update"""
        await self.broadcast({
            "type": "raffle_update",
            "raffle_id": raffle_id,
            "data": raffle_data
        })

    async def broadcast_raffle_started(self, raffle_id: int, waiting_until: str):
        """Broadcast raffle timer started"""
        await self.broadcast({
            "type": "raffle_started",
            "raffle_id": raffle_id,
            "waiting_until": waiting_until
        })

    async def broadcast_raffle_completed(self, raffle_id: int, winner_id: int):
        """Broadcast raffle completed"""
        await self.broadcast({
            "type": "raffle_completed",
            "raffle_id": raffle_id,
            "winner_id": winner_id
        })


# Global WebSocket manager
websocket_manager = ConnectionManager()
