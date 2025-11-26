"""
WebSocket consumers for Notifications app.
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class NotificationConsumer(AsyncWebsocketConsumer):
    """
    Consumer for handling real-time notifications.
    """
    
    async def connect(self):
        """
        Handle WebSocket connection.
        """
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return
            
        # Create a unique group for the user
        self.group_name = f'user_{self.user.id}'
        
        # Join user group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Also join department group if user belongs to one
        if self.user.department_id:
            self.dept_group_name = f'dept_{self.user.department_id}'
            await self.channel_layer.group_add(
                self.dept_group_name,
                self.channel_name
            )
    
    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.
        """
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
            
        if hasattr(self, 'dept_group_name'):
            await self.channel_layer.group_discard(
                self.dept_group_name,
                self.channel_name
            )
    
    async def notification_message(self, event):
        """
        Send notification to WebSocket.
        """
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event['data']))
