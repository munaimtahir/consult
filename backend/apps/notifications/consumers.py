"""
WebSocket consumers for Notifications app.
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class NotificationConsumer(AsyncWebsocketConsumer):
    """Handles WebSocket connections for real-time notifications.

    This consumer manages the lifecycle of a WebSocket connection for a user.
    It adds the user to a personal group and a department group (if
    applicable) to receive targeted notifications.
    """
    
    async def connect(self):
        """Handles a new WebSocket connection.

        Authenticates the user and subscribes them to their user-specific
        and department-specific notification groups.
        """
        self.user = self.scope['user']
        
        # Check if user is authenticated (not AnonymousUser)
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)  # Unauthorized
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
        if hasattr(self.user, 'department_id') and self.user.department_id:
            self.dept_group_name = f'dept_{self.user.department_id}'
            await self.channel_layer.group_add(
                self.dept_group_name,
                self.channel_name
            )
    
    async def disconnect(self, close_code):
        """Handles a WebSocket disconnection.

        Unsubscribes the user from their notification groups.

        Args:
            close_code: The code indicating the reason for closure.
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
        """Sends a notification message to the WebSocket client.

        This method is called when a message is sent to a group the user
        is subscribed to.

        Args:
            event: A dictionary containing the notification data.
        """
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event['data']))
