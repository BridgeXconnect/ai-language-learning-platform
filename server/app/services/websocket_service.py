"""
WebSocket Service for Real-time Course Manager Updates
Provides real-time workflow status and agent health monitoring
"""

import json
import logging
import asyncio
from typing import Dict, Set, Optional, Any, List
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
import traceback

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        # Active connections by user ID
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        
        # Workflow subscriptions - user_id -> set of workflow_ids
        self.workflow_subscriptions: Dict[int, Set[str]] = {}
        
        # Agent health subscriptions - user_id -> bool
        self.health_subscriptions: Dict[int, bool] = {}
        
        # Connection metadata
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
        
        # Message queue for offline users
        self.message_queue: Dict[int, List[Dict[str, Any]]] = {}
        
        # Statistics
        self.stats = {
            "total_connections": 0,
            "current_connections": 0,
            "messages_sent": 0,
            "messages_failed": 0,
            "last_reset": datetime.utcnow().isoformat()
        }
    
    async def connect(self, websocket: WebSocket, user_id: int, client_info: Optional[Dict[str, Any]] = None):
        """Accept a new WebSocket connection."""
        try:
            await websocket.accept()
            
            # Initialize user connections if not exists
            if user_id not in self.active_connections:
                self.active_connections[user_id] = set()
                self.workflow_subscriptions[user_id] = set()
                self.health_subscriptions[user_id] = False
            
            # Add connection
            self.active_connections[user_id].add(websocket)
            
            # Store connection metadata
            self.connection_metadata[websocket] = {
                "user_id": user_id,
                "connected_at": datetime.utcnow().isoformat(),
                "client_info": client_info or {},
                "last_ping": datetime.utcnow().isoformat()
            }
            
            # Update stats
            self.stats["total_connections"] += 1
            self.stats["current_connections"] = sum(len(connections) for connections in self.active_connections.values())
            
            logger.info(f"WebSocket connected for user {user_id}. Total connections: {self.stats['current_connections']}")
            
            # Send welcome message
            await self._send_to_connection(websocket, {
                "type": "connection_established",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Real-time updates enabled"
            })
            
            # Send any queued messages
            await self._send_queued_messages(user_id)
            
        except Exception as e:
            logger.error(f"Failed to establish WebSocket connection for user {user_id}: {e}")
            await self._safe_close(websocket)
    
    async def disconnect(self, websocket: WebSocket):
        """Handle WebSocket disconnection."""
        try:
            metadata = self.connection_metadata.get(websocket, {})
            user_id = metadata.get("user_id")
            
            if user_id and user_id in self.active_connections:
                self.active_connections[user_id].discard(websocket)
                
                # Clean up empty user entries
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
                    if user_id in self.workflow_subscriptions:
                        del self.workflow_subscriptions[user_id]
                    if user_id in self.health_subscriptions:
                        del self.health_subscriptions[user_id]
            
            # Remove metadata
            if websocket in self.connection_metadata:
                del self.connection_metadata[websocket]
            
            # Update stats
            self.stats["current_connections"] = sum(len(connections) for connections in self.active_connections.values())
            
            logger.info(f"WebSocket disconnected for user {user_id}. Remaining connections: {self.stats['current_connections']}")
            
        except Exception as e:
            logger.error(f"Error during WebSocket disconnection: {e}")
    
    async def subscribe_to_workflow(self, user_id: int, workflow_id: str):
        """Subscribe user to workflow updates."""
        if user_id in self.workflow_subscriptions:
            self.workflow_subscriptions[user_id].add(workflow_id)
            logger.info(f"User {user_id} subscribed to workflow {workflow_id}")
            
            # Send confirmation
            await self.send_to_user(user_id, {
                "type": "workflow_subscription_confirmed",
                "workflow_id": workflow_id,
                "timestamp": datetime.utcnow().isoformat()
            })
    
    async def unsubscribe_from_workflow(self, user_id: int, workflow_id: str):
        """Unsubscribe user from workflow updates."""
        if user_id in self.workflow_subscriptions:
            self.workflow_subscriptions[user_id].discard(workflow_id)
            logger.info(f"User {user_id} unsubscribed from workflow {workflow_id}")
    
    async def subscribe_to_health_updates(self, user_id: int):
        """Subscribe user to agent health updates."""
        if user_id in self.health_subscriptions:
            self.health_subscriptions[user_id] = True
            logger.info(f"User {user_id} subscribed to health updates")
            
            # Send confirmation
            await self.send_to_user(user_id, {
                "type": "health_subscription_confirmed",
                "timestamp": datetime.utcnow().isoformat()
            })
    
    async def unsubscribe_from_health_updates(self, user_id: int):
        """Unsubscribe user from agent health updates."""
        if user_id in self.health_subscriptions:
            self.health_subscriptions[user_id] = False
            logger.info(f"User {user_id} unsubscribed from health updates")
    
    async def send_to_user(self, user_id: int, message: Dict[str, Any]) -> bool:
        """Send message to all connections for a specific user."""
        if user_id not in self.active_connections:
            # Queue message for offline user
            if user_id not in self.message_queue:
                self.message_queue[user_id] = []
            
            self.message_queue[user_id].append({
                **message,
                "queued_at": datetime.utcnow().isoformat()
            })
            
            # Limit queue size
            if len(self.message_queue[user_id]) > 50:
                self.message_queue[user_id] = self.message_queue[user_id][-50:]
            
            return False
        
        connections = self.active_connections[user_id].copy()
        failed_connections = []
        success_count = 0
        
        for connection in connections:
            success = await self._send_to_connection(connection, message)
            if success:
                success_count += 1
            else:
                failed_connections.append(connection)
        
        # Clean up failed connections
        for failed_connection in failed_connections:
            await self.disconnect(failed_connection)
        
        return success_count > 0
    
    async def broadcast_workflow_update(self, workflow_id: str, update_data: Dict[str, Any]):
        """Broadcast workflow update to subscribed users."""
        message = {
            "type": "workflow_update",
            "workflow_id": workflow_id,
            "data": update_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        sent_count = 0
        for user_id, workflow_subscriptions in self.workflow_subscriptions.items():
            if workflow_id in workflow_subscriptions:
                success = await self.send_to_user(user_id, message)
                if success:
                    sent_count += 1
        
        if sent_count > 0:
            logger.info(f"Workflow update for {workflow_id} sent to {sent_count} users")
        
        return sent_count
    
    async def broadcast_health_update(self, health_data: Dict[str, Any]):
        """Broadcast agent health update to subscribed users."""
        message = {
            "type": "health_update",
            "data": health_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        sent_count = 0
        for user_id, subscribed in self.health_subscriptions.items():
            if subscribed:
                success = await self.send_to_user(user_id, message)
                if success:
                    sent_count += 1
        
        if sent_count > 0:
            logger.info(f"Health update sent to {sent_count} users")
        
        return sent_count
    
    async def send_system_message(self, message: str, level: str = "info"):
        """Send system message to all connected users."""
        system_message = {
            "type": "system_message",
            "level": level,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        sent_count = 0
        for user_id in self.active_connections.keys():
            success = await self.send_to_user(user_id, system_message)
            if success:
                sent_count += 1
        
        logger.info(f"System message sent to {sent_count} users: {message}")
        return sent_count
    
    async def _send_to_connection(self, websocket: WebSocket, message: Dict[str, Any]) -> bool:
        """Send message to a specific WebSocket connection."""
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_text(json.dumps(message))
                self.stats["messages_sent"] += 1
                
                # Update last ping time
                if websocket in self.connection_metadata:
                    self.connection_metadata[websocket]["last_ping"] = datetime.utcnow().isoformat()
                
                return True
            else:
                return False
                
        except WebSocketDisconnect:
            await self.disconnect(websocket)
            return False
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {e}")
            self.stats["messages_failed"] += 1
            await self.disconnect(websocket)
            return False
    
    async def _send_queued_messages(self, user_id: int):
        """Send any queued messages to a newly connected user."""
        if user_id in self.message_queue and self.message_queue[user_id]:
            messages = self.message_queue[user_id]
            logger.info(f"Sending {len(messages)} queued messages to user {user_id}")
            
            for message in messages:
                await self.send_to_user(user_id, {
                    **message,
                    "type": f"queued_{message.get('type', 'message')}"
                })
            
            # Clear queue
            del self.message_queue[user_id]
    
    async def _safe_close(self, websocket: WebSocket):
        """Safely close a WebSocket connection."""
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.close()
        except Exception as e:
            logger.error(f"Error closing WebSocket: {e}")
    
    async def ping_connections(self):
        """Send ping to all connections to keep them alive."""
        ping_message = {
            "type": "ping",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        total_connections = sum(len(connections) for connections in self.active_connections.values())
        if total_connections > 0:
            logger.debug(f"Pinging {total_connections} WebSocket connections")
            
            for user_id in list(self.active_connections.keys()):
                await self.send_to_user(user_id, ping_message)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection manager statistics."""
        return {
            **self.stats,
            "current_connections": sum(len(connections) for connections in self.active_connections.values()),
            "unique_users": len(self.active_connections),
            "workflow_subscriptions": sum(len(subs) for subs in self.workflow_subscriptions.values()),
            "health_subscriptions": sum(1 for subscribed in self.health_subscriptions.values() if subscribed),
            "queued_messages": sum(len(queue) for queue in self.message_queue.values()),
            "current_time": datetime.utcnow().isoformat()
        }
    
    def get_user_info(self, user_id: int) -> Dict[str, Any]:
        """Get information about a specific user's connections."""
        connections = self.active_connections.get(user_id, set())
        workflow_subs = self.workflow_subscriptions.get(user_id, set())
        health_sub = self.health_subscriptions.get(user_id, False)
        queued = len(self.message_queue.get(user_id, []))
        
        connection_details = []
        for connection in connections:
            metadata = self.connection_metadata.get(connection, {})
            connection_details.append({
                "connected_at": metadata.get("connected_at"),
                "last_ping": metadata.get("last_ping"),
                "client_info": metadata.get("client_info", {})
            })
        
        return {
            "user_id": user_id,
            "connection_count": len(connections),
            "connections": connection_details,
            "workflow_subscriptions": list(workflow_subs),
            "health_subscription": health_sub,
            "queued_messages": queued
        }

# Global connection manager instance
connection_manager = ConnectionManager()

class WebSocketService:
    """Service for handling WebSocket operations."""
    
    def __init__(self):
        self.manager = connection_manager
        self._ping_task = None
        self._monitoring_active = False
    
    async def start_monitoring(self):
        """Start background monitoring tasks."""
        if not self._monitoring_active:
            self._monitoring_active = True
            self._ping_task = asyncio.create_task(self._ping_loop())
            logger.info("WebSocket monitoring started")
    
    async def stop_monitoring(self):
        """Stop background monitoring tasks."""
        self._monitoring_active = False
        if self._ping_task:
            self._ping_task.cancel()
            try:
                await self._ping_task
            except asyncio.CancelledError:
                pass
        logger.info("WebSocket monitoring stopped")
    
    async def _ping_loop(self):
        """Background task to ping connections."""
        while self._monitoring_active:
            try:
                await self.manager.ping_connections()
                await asyncio.sleep(30)  # Ping every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in ping loop: {e}")
                await asyncio.sleep(30)
    
    async def handle_message(self, websocket: WebSocket, message_data: Dict[str, Any], user_id: int):
        """Handle incoming WebSocket messages."""
        try:
            message_type = message_data.get("type")
            
            if message_type == "subscribe_workflow":
                workflow_id = message_data.get("workflow_id")
                if workflow_id:
                    await self.manager.subscribe_to_workflow(user_id, workflow_id)
            
            elif message_type == "unsubscribe_workflow":
                workflow_id = message_data.get("workflow_id")
                if workflow_id:
                    await self.manager.unsubscribe_from_workflow(user_id, workflow_id)
            
            elif message_type == "subscribe_health":
                await self.manager.subscribe_to_health_updates(user_id)
            
            elif message_type == "unsubscribe_health":
                await self.manager.unsubscribe_from_health_updates(user_id)
            
            elif message_type == "pong":
                # Handle pong response
                logger.debug(f"Received pong from user {user_id}")
            
            else:
                logger.warning(f"Unknown message type from user {user_id}: {message_type}")
                await self.manager.send_to_user(user_id, {
                    "type": "error",
                    "message": f"Unknown message type: {message_type}",
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}\\n{traceback.format_exc()}")
            await self.manager.send_to_user(user_id, {
                "type": "error",
                "message": "Failed to process message",
                "timestamp": datetime.utcnow().isoformat()
            })

# Global WebSocket service instance
websocket_service = WebSocketService()