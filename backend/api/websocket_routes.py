"""
WebSocket routes for real-time communication with clients
"""

import logging
import json
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from fastapi.websockets import WebSocketState
from ..utils.websocket_manager import WebSocketManager

logger = logging.getLogger(__name__)

# Create router
websocket_router = APIRouter(
    prefix="/ws",
    tags=["websocket"]
)

# WebSocket manager instance
websocket_manager = WebSocketManager()


@websocket_router.websocket("/connect/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time client communication."""
    
    await websocket.accept()
    await websocket_manager.connect(user_id, websocket)
    
    logger.info(f"WebSocket connection established for user: {user_id}")
    
    try:
        # Send welcome message
        await websocket_manager.send_personal_message(
            user_id, 
            {
                "type": "connection_established",
                "message": "WebSocket connection successful",
                "user_id": user_id
            }
        )
        
        # Listen for messages from client
        while websocket.application_state == WebSocketState.CONNECTED:
            try:
                # Receive data from client
                data = await websocket.receive_text()
                
                try:
                    message = json.loads(data)
                    await handle_websocket_message(user_id, message)
                    
                except json.JSONDecodeError:
                    await websocket_manager.send_personal_message(
                        user_id,
                        {
                            "type": "error",
                            "message": "Invalid JSON format"
                        }
                    )
                
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for user: {user_id}")
                break
                
            except Exception as e:
                logger.error(f"WebSocket error for user {user_id}: {str(e)}")
                await websocket_manager.send_personal_message(
                    user_id,
                    {
                        "type": "error",
                        "message": f"Server error: {str(e)}"
                    }
                )
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user: {user_id}")
        
    except Exception as e:
        logger.error(f"WebSocket connection error for user {user_id}: {str(e)}")
        
    finally:
        await websocket_manager.disconnect(user_id)
        logger.info(f"WebSocket connection closed for user: {user_id}")


async def handle_websocket_message(user_id: str, message: Dict[str, Any]):
    """Handle incoming WebSocket messages from clients."""
    
    message_type = message.get("type")
    
    try:
        if message_type == "ping":
            # Respond to ping with pong
            await websocket_manager.send_personal_message(
                user_id,
                {
                    "type": "pong",
                    "timestamp": message.get("timestamp")
                }
            )
            
        elif message_type == "task_status_request":
            # Client requesting task status
            task_id = message.get("task_id")
            if task_id:
                await handle_task_status_request(user_id, task_id)
            else:
                await websocket_manager.send_personal_message(
                    user_id,
                    {
                        "type": "error",
                        "message": "task_id required for status request"
                    }
                )
                
        elif message_type == "subscribe_to_updates":
            # Client wants to subscribe to specific updates
            subscription_type = message.get("subscription_type", "all")
            await handle_subscription_request(user_id, subscription_type)
            
        elif message_type == "agent_status_request":
            # Client requesting agent status
            await handle_agent_status_request(user_id)
            
        else:
            await websocket_manager.send_personal_message(
                user_id,
                {
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                }
            )
            
    except Exception as e:
        logger.error(f"Error handling WebSocket message from {user_id}: {str(e)}")
        await websocket_manager.send_personal_message(
            user_id,
            {
                "type": "error",
                "message": f"Error processing message: {str(e)}"
            }
        )


async def handle_task_status_request(user_id: str, task_id: str):
    """Handle task status request from client."""
    
    try:
        # Import here to avoid circular imports
        from ..utils.task_manager import TaskManager
        
        task_manager = TaskManager()
        task_status = await task_manager.get_task_status(task_id)
        
        if task_status:
            await websocket_manager.send_personal_message(
                user_id,
                {
                    "type": "task_status_response",
                    "task_id": task_id,
                    "status": task_status
                }
            )
        else:
            await websocket_manager.send_personal_message(
                user_id,
                {
                    "type": "task_status_response",
                    "task_id": task_id,
                    "error": "Task not found"
                }
            )
            
    except Exception as e:
        logger.error(f"Error getting task status for {task_id}: {str(e)}")
        await websocket_manager.send_personal_message(
            user_id,
            {
                "type": "error",
                "message": f"Error retrieving task status: {str(e)}"
            }
        )


async def handle_subscription_request(user_id: str, subscription_type: str):
    """Handle subscription request from client."""
    
    try:
        # Add user to subscription list (implement based on your needs)
        await websocket_manager.add_subscription(user_id, subscription_type)
        
        await websocket_manager.send_personal_message(
            user_id,
            {
                "type": "subscription_confirmed",
                "subscription_type": subscription_type,
                "message": f"Subscribed to {subscription_type} updates"
            }
        )
        
    except Exception as e:
        logger.error(f"Error handling subscription for {user_id}: {str(e)}")
        await websocket_manager.send_personal_message(
            user_id,
            {
                "type": "error",
                "message": f"Error setting up subscription: {str(e)}"
            }
        )


async def handle_agent_status_request(user_id: str):
    """Handle agent status request from client."""
    
    try:
        # Import here to avoid circular imports
        from ..agents.social_optimizer import SocialOptimizerCrew
        
        # This would typically be injected or managed globally
        social_crew = SocialOptimizerCrew()
        
        if social_crew.initialized:
            agent_status = await social_crew.get_agents_status()
            
            await websocket_manager.send_personal_message(
                user_id,
                {
                    "type": "agent_status_response",
                    "agents": agent_status
                }
            )
        else:
            await websocket_manager.send_personal_message(
                user_id,
                {
                    "type": "agent_status_response",
                    "message": "Agents not initialized yet"
                }
            )
            
    except Exception as e:
        logger.error(f"Error getting agent status: {str(e)}")
        await websocket_manager.send_personal_message(
            user_id,
            {
                "type": "error",
                "message": f"Error retrieving agent status: {str(e)}"
            }
        )


# Additional WebSocket endpoints for specific functionalities

@websocket_router.websocket("/live-analytics/{user_id}")
async def live_analytics_websocket(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for live analytics updates."""
    
    await websocket.accept()
    logger.info(f"Live analytics WebSocket connected for user: {user_id}")
    
    try:
        while True:
            # Send periodic analytics updates
            analytics_data = await get_live_analytics_data(user_id)
            
            await websocket.send_text(json.dumps({
                "type": "analytics_update",
                "data": analytics_data,
                "timestamp": "now"  # Replace with actual timestamp
            }))
            
            # Wait for 30 seconds before next update
            await asyncio.sleep(30)
            
    except WebSocketDisconnect:
        logger.info(f"Live analytics WebSocket disconnected for user: {user_id}")
    except Exception as e:
        logger.error(f"Live analytics WebSocket error for user {user_id}: {str(e)}")


async def get_live_analytics_data(user_id: str) -> Dict[str, Any]:
    """Get live analytics data for user."""
    
    try:
        # This would typically fetch real analytics data
        # For now, return mock data
        return {
            "active_tasks": 2,
            "completed_tasks_today": 5,
            "agent_activity": {
                "social_optimizer": "active",
                "content_writer": "idle",
                "traffic_analyst": "active",
                "video_creator": "idle",
                "script_writer": "idle"
            },
            "recent_content_performance": {
                "total_posts": 10,
                "avg_engagement": 4.2,
                "trending_topics": ["AI", "Social Media", "Content Creation"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting live analytics data: {str(e)}")
        return {"error": "Failed to fetch analytics data"}


# Import asyncio for sleep function
import asyncio