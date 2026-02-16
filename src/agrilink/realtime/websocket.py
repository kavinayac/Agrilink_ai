"""WebSocket connection manager and endpoints."""

import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from agrilink.events.schema import BaseEvent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["websocket"])


class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        """Initialize connection manager."""
        # Map user_id to list of websockets (user can have multiple tabs open)
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """
        Accept connection and store it.
        
        Args:
            websocket: WebSocket connection
            user_id: User identifier
        """
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        self.active_connections[user_id].append(websocket)
        logger.info(f"User {user_id} connected. Active connections: {len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        """
        Remove connection.
        
        Args:
            websocket: WebSocket connection
            user_id: User identifier
        """
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
                
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                
        logger.info(f"User {user_id} disconnected")

    async def send_personal_message(self, message: dict, user_id: str):
        """
        Send message to specific user.
        
        Args:
            message: Message data
            user_id: User identifier
        """
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                if connection.client_state == WebSocketState.CONNECTED:
                    await connection.send_json(message)

    async def broadcast(self, message: dict):
        """
        Broadcast message to all connected users.
        
        Args:
            message: Message data
        """
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                if connection.client_state == WebSocketState.CONNECTED:
                    await connection.send_json(message)


manager = ConnectionManager()


@router.websocket("/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time updates.
    
    Args:
        websocket: WebSocket connection
        user_id: User identifier
    """
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive and listen for client messages (optional)
            data = await websocket.receive_text()
            # For now, we just echo back or log
            logger.debug(f"Received from {user_id}: {data}")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket error for {user_id}: {e}")
        manager.disconnect(websocket, user_id)


async def broadcast_event_to_clients(event: BaseEvent):
    """
    Broadcast event to connected WebSocket clients.
    
    This function handles the logic of which users should see which events.
    For now, we'll broadcast most events to everyone for the demo,
    but filter personal ones.
    
    Args:
        event: The event to broadcast
    """
    event_data = event.model_dump(mode="json")
    
    # If event has a specific user_id, send only to them
    if event.user_id and event.user_id != "system":
        await manager.send_personal_message(event_data, event.user_id)
    else:
        # Broadcast public events
        await manager.broadcast(event_data)
