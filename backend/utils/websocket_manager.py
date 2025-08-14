"""
WebSocket Manager for handling real-time client connections
"""

import logging
import json
import asyncio
from typing import Dict, List, Any, Optional, Set
from fastapi import WebSocket
from datetime import datetime

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections and real-time communication."""
    
    def __init__(self):
        # Store active connections by user_id
        self.active_connections: Dict[str, WebSocket] = {}
        
        # Store subscriptions by user_id
        self.subscriptions: Dict[str, Set[str]] = {}
        
        # Store connection metadata
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Lock for thread safety
        self._lock = asyncio.Lock()
    
    async def connect(self, user_id: str, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        
        async with self._lock:
            # Disconnect existing connection if any
            if user_id in self.active_connections:
                await self.disconnect(user_id)
            
            # Store the new connection
            self.active_connections[user_id] = websocket
            
            # Initialize subscriptions
            self.subscriptions[user_id] = set()
            
            # Store connection metadata
            self.connection_metadata[user_id] = {
                "connected_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "message_count": 0
            }
            
            logger.info(f"WebSocket connected for user {user_id}. Active connections: {len(self.active_connections)}")
    
    async def disconnect(self, user_id: str):
        """Disconnect a WebSocket connection."""
        
        async with self._lock:
            if user_id in self.active_connections:
                try:
                    websocket = self.active_connections[user_id]
                    await websocket.close()
                except Exception as e:
                    logger.warning(f"Error closing WebSocket for user {user_id}: {str(e)}")
                
                # Clean up stored data
                del self.active_connections[user_id]
                
                if user_id in self.subscriptions:
                    del self.subscriptions[user_id]
                
                if user_id in self.connection_metadata:
                    del self.connection_metadata[user_id]
                
                logger.info(f"WebSocket disconnected for user {user_id}. Active connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, user_id: str, message: Dict[str, Any]):
        """Send a message to a specific user."""
        
        if user_id not in self.active_connections:
            logger.warning(f"Cannot send message to user {user_id}: not connected")
            return False
        
        try:
            websocket = self.active_connections[user_id]
            
            # Add timestamp to message
            message["timestamp"] = datetime.now().isoformat()
            
            await websocket.send_text(json.dumps(message))
            
            # Update metadata
            if user_id in self.connection_metadata:
                self.connection_metadata[user_id]["last_activity"] = datetime.now().isoformat()
                self.connection_metadata[user_id]["message_count"] += 1
            
            logger.debug(f"Message sent to user {user_id}: {message.get('type', 'unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending message to user {user_id}: {str(e)}")
            
            # Connection might be broken, remove it
            await self.disconnect(user_id)
            return False
    
    async def broadcast_message(self, message: Dict[str, Any], exclude_users: Optional[List[str]] = None):
        """Send a message to all connected users."""
        
        exclude_users = exclude_users or []
        message["timestamp"] = datetime.now().isoformat()
        
        disconnected_users = []
        
        for user_id, websocket in self.active_connections.items():
            if user_id in exclude_users:
                continue
            
            try:
                await websocket.send_text(json.dumps(message))
                
                # Update metadata
                if user_id in self.connection_metadata:
                    self.connection_metadata[user_id]["last_activity"] = datetime.now().isoformat()
                    self.connection_metadata[user_id]["message_count"] += 1
                
            except Exception as e:
                logger.error(f"Error broadcasting to user {user_id}: {str(e)}")
                disconnected_users.append(user_id)
        
        # Clean up disconnected users
        for user_id in disconnected_users:
            await self.disconnect(user_id)
        
        logger.info(f"Broadcast message sent to {len(self.active_connections) - len(exclude_users)} users")
    
    async def send_to_subscribers(self, subscription_type: str, message: Dict[str, Any]):
        """Send message to users subscribed to a specific type."""
        
        message["timestamp"] = datetime.now().isoformat()
        message["subscription_type"] = subscription_type
        
        sent_count = 0
        disconnected_users = []
        
        for user_id, subscriptions in self.subscriptions.items():
            if subscription_type in subscriptions and user_id in self.active_connections:
                try:
                    websocket = self.active_connections[user_id]
                    await websocket.send_text(json.dumps(message))
                    
                    # Update metadata
                    if user_id in self.connection_metadata:
                        self.connection_metadata[user_id]["last_activity"] = datetime.now().isoformat()
                        self.connection_metadata[user_id]["message_count"] += 1
                    
                    sent_count += 1
                    
                except Exception as e:
                    logger.error(f"Error sending subscription message to user {user_id}: {str(e)}")
                    disconnected_users.append(user_id)
        
        # Clean up disconnected users
        for user_id in disconnected_users:
            await self.disconnect(user_id)
        
        logger.info(f"Subscription message sent to {sent_count} users subscribed to {subscription_type}")
    
    async def add_subscription(self, user_id: str, subscription_type: str):
        """Add a subscription for a user."""
        
        if user_id not in self.subscriptions:
            self.subscriptions[user_id] = set()
        
        self.subscriptions[user_id].add(subscription_type)
        logger.info(f"User {user_id} subscribed to {subscription_type}")
    
    async def remove_subscription(self, user_id: str, subscription_type: str):
        """Remove a subscription for a user."""
        
        if user_id in self.subscriptions:
            self.subscriptions[user_id].discard(subscription_type)
            logger.info(f"User {user_id} unsubscribed from {subscription_type}")
    
    async def get_user_subscriptions(self, user_id: str) -> Set[str]:
        """Get all subscriptions for a user."""
        
        return self.subscriptions.get(user_id, set())
    
    def get_connected_users(self) -> List[str]:
        """Get list of currently connected users."""
        
        return list(self.active_connections.keys())
    
    def get_connection_count(self) -> int:
        """Get total number of active connections."""
        
        return len(self.active_connections)
    
    def get_connection_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get connection information for a user."""
        
        if user_id not in self.active_connections:
            return None
        
        metadata = self.connection_metadata.get(user_id, {})
        subscriptions = self.subscriptions.get(user_id, set())
        
        return {
            "user_id": user_id,
            "connected": True,
            "connected_at": metadata.get("connected_at"),
            "last_activity": metadata.get("last_activity"),
            "message_count": metadata.get("message_count", 0),
            "subscriptions": list(subscriptions)
        }
    
    def get_all_connections_info(self) -> List[Dict[str, Any]]:
        """Get information about all active connections."""
        
        connections_info = []
        
        for user_id in self.active_connections.keys():
            info = self.get_connection_info(user_id)
            if info:
                connections_info.append(info)
        
        return connections_info
    
    async def ping_all_connections(self):
        """Send ping to all connections to check if they're still alive."""
        
        ping_message = {
            "type": "ping",
            "timestamp": datetime.now().isoformat()
        }
        
        disconnected_users = []
        
        for user_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(ping_message))
                
            except Exception as e:
                logger.warning(f"Ping failed for user {user_id}: {str(e)}")
                disconnected_users.append(user_id)
        
        # Clean up disconnected users
        for user_id in disconnected_users:
            await self.disconnect(user_id)
        
        logger.info(f"Pinged {len(self.active_connections)} connections, removed {len(disconnected_users)} dead connections")
    
    async def send_task_update(
        self, 
        user_id: str, 
        task_id: str, 
        status: str, 
        result: Optional[Any] = None, 
        error: Optional[str] = None
    ):
        """Send task update to specific user."""
        
        update_message = {
            "type": "task_update",
            "task_id": task_id,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
        if result is not None:
            update_message["result"] = result
        
        if error is not None:
            update_message["error"] = error
        
        await self.send_personal_message(user_id, update_message)
    
    async def send_agent_status_update(self, agent_name: str, status: str, details: Optional[Dict[str, Any]] = None):
        """Send agent status update to all subscribers."""
        
        update_message = {
            "type": "agent_status_update",
            "agent_name": agent_name,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
        if details:
            update_message["details"] = details
        
        await self.send_to_subscribers("agent_updates", update_message)
    
    async def send_system_alert(self, alert_type: str, message: str, severity: str = "info"):
        """Send system alert to all connected users."""
        
        alert_message = {
            "type": "system_alert",
            "alert_type": alert_type,
            "message": message,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.broadcast_message(alert_message)
    
    async def send_analytics_update(self, user_id: str, analytics_data: Dict[str, Any]):
        """Send analytics update to specific user."""
        
        analytics_message = {
            "type": "analytics_update",
            "data": analytics_data,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.send_personal_message(user_id, analytics_message)
    
    async def cleanup_inactive_connections(self, max_inactive_minutes: int = 30):
        """Clean up connections that have been inactive for too long."""
        
        current_time = datetime.now()
        inactive_users = []
        
        for user_id, metadata in self.connection_metadata.items():
            last_activity = datetime.fromisoformat(metadata.get("last_activity", current_time.isoformat()))
            inactive_duration = (current_time - last_activity).total_seconds() / 60
            
            if inactive_duration > max_inactive_minutes:
                inactive_users.append(user_id)
        
        for user_id in inactive_users:
            logger.info(f"Cleaning up inactive connection for user {user_id}")
            await self.disconnect(user_id)
        
        return len(inactive_users)


# Global WebSocket manager instance
websocket_manager = WebSocketManager()