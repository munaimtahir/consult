"""
Email Reply Service
Handles processing email replies to perform actions on consults.
"""

from django.utils import timezone
from apps.notifications.models import EmailNotification
from apps.consults.models import ConsultRequest
from apps.consults.services import ConsultService
import logging

logger = logging.getLogger(__name__)


class EmailReplyService:
    """
    Service for processing email replies and executing actions.
    """
    
    # Supported reply commands
    COMMANDS = {
        'acknowledged': 'acknowledge',
        'acknowledge': 'acknowledge',
        'ack': 'acknowledge',
        'complete': 'complete',
        'completed': 'complete',
        'close': 'close',
        'closed': 'close',
    }
    
    @staticmethod
    def process_email_reply(reply_token, sender_email, reply_body):
        """
        Process an email reply and execute the requested action.
        
        Args:
            reply_token: UUID token from the email notification
            sender_email: Email address of the person replying
            reply_body: Text content of the email reply
        
        Returns:
            dict with 'success', 'message', and 'action_taken' keys
        """
        try:
            # Find the email notification by token
            try:
                notification = EmailNotification.objects.get(reply_token=reply_token)
            except EmailNotification.DoesNotExist:
                return {
                    'success': False,
                    'message': 'Invalid reply token',
                    'action_taken': None
                }
            
            # Verify sender is the recipient
            if notification.recipient.email.lower() != sender_email.lower():
                logger.warning(
                    f"Email reply from unauthorized sender: {sender_email} "
                    f"(expected: {notification.recipient.email})"
                )
                return {
                    'success': False,
                    'message': 'Unauthorized: You are not the recipient of this email',
                    'action_taken': None
                }
            
            # Check if consult still exists
            if not notification.consult:
                return {
                    'success': False,
                    'message': 'Consult no longer exists',
                    'action_taken': None
                }
            
            consult = notification.consult
            
            # Parse command from reply body
            command = EmailReplyService._parse_command(reply_body)
            
            if not command:
                return {
                    'success': False,
                    'message': 'No valid command found. Supported commands: acknowledged, complete, close',
                    'action_taken': None
                }
            
            # Execute the command
            result = EmailReplyService._execute_command(
                consult, 
                notification.recipient, 
                command
            )
            
            # Update notification record
            notification.reply_received = True
            notification.reply_received_at = timezone.now()
            notification.reply_action_taken = command
            notification.save()
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing email reply: {e}")
            return {
                'success': False,
                'message': f'Error processing reply: {str(e)}',
                'action_taken': None
            }
    
    @staticmethod
    def _parse_command(reply_body):
        """
        Parse command from email reply body.
        
        Args:
            reply_body: Text content of the email
        
        Returns:
            Command string or None
        """
        if not reply_body:
            return None
        
        # Normalize reply body
        body_lower = reply_body.lower().strip()
        
        # Check for commands
        for keyword, command in EmailReplyService.COMMANDS.items():
            if keyword in body_lower:
                return command
        
        return None
    
    @staticmethod
    def _execute_command(consult, user, command):
        """
        Execute a command on a consult.
        
        Args:
            consult: ConsultRequest instance
            user: User executing the command
            command: Command to execute
        
        Returns:
            dict with result information
        """
        try:
            if command == 'acknowledge':
                # Check if user can acknowledge this consult
                if user.department != consult.target_department:
                    return {
                        'success': False,
                        'message': 'You can only acknowledge consults for your department',
                        'action_taken': None
                    }
                
                if consult.status != 'SUBMITTED':
                    return {
                        'success': False,
                        'message': f'Consult is already {consult.status.lower()}',
                        'action_taken': None
                    }
                
                ConsultService.acknowledge_consult(consult, user)
                return {
                    'success': True,
                    'message': f'Consult #{consult.id} has been acknowledged',
                    'action_taken': 'acknowledge'
                }
            
            elif command == 'complete':
                # Check if user can complete this consult
                if consult.assigned_to != user and user.department != consult.target_department:
                    return {
                        'success': False,
                        'message': 'You are not assigned to this consult',
                        'action_taken': None
                    }
                
                if consult.status in ['COMPLETED', 'CLOSED']:
                    return {
                        'success': False,
                        'message': f'Consult is already {consult.status.lower()}',
                        'action_taken': None
                    }
                
                ConsultService.complete_consult(consult)
                return {
                    'success': True,
                    'message': f'Consult #{consult.id} has been completed',
                    'action_taken': 'complete'
                }
            
            elif command == 'close':
                # Check if user can close this consult
                if consult.assigned_to != user and user.department != consult.target_department:
                    return {
                        'success': False,
                        'message': 'You are not assigned to this consult',
                        'action_taken': None
                    }
                
                if consult.status == 'CLOSED':
                    return {
                        'success': False,
                        'message': 'Consult is already closed',
                        'action_taken': None
                    }
                
                consult.status = 'CLOSED'
                consult.completed_at = timezone.now()
                consult.save()
                
                from apps.notifications.services import NotificationService
                NotificationService.notify_consult_closed(consult)
                
                return {
                    'success': True,
                    'message': f'Consult #{consult.id} has been closed',
                    'action_taken': 'close'
                }
            
            else:
                return {
                    'success': False,
                    'message': f'Unknown command: {command}',
                    'action_taken': None
                }
                
        except Exception as e:
            logger.error(f"Error executing command {command}: {e}")
            return {
                'success': False,
                'message': f'Error executing command: {str(e)}',
                'action_taken': None
            }

