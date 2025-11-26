"""
Notification Service
Handles sending real-time notifications and emails.
"""

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from apps.core.services.email_service import EmailService

class NotificationService:
    """
    Service for handling notifications.
    """
    
    @staticmethod
    def _send_ws_message(group_name, message_type, data):
        """
        Helper to send WebSocket message to a group.
        """
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'notification_message',
                'data': {
                    'type': message_type,
                    **data
                }
            }
        )
    
    @staticmethod
    def notify_new_consult(consult):
        """
        Notify target department about new consult.
        """
        # Send email
        EmailService.send_new_consult_notification(consult)
        
        # Real-time notification to department group
        NotificationService._send_ws_message(
            f'dept_{consult.target_department.id}',
            'NEW_CONSULT',
            {
                'id': consult.id,
                'patient_name': consult.patient.name,
                'urgency': consult.urgency,
                'message': f"New {consult.urgency} consult for {consult.patient.name}"
            }
        )
    
    @staticmethod
    def notify_consult_assigned(consult, doctor):
        """
        Notify doctor about assignment.
        """
        # Send email
        EmailService.send_consult_assigned_notification(consult)
        
        # Real-time notification to doctor
        NotificationService._send_ws_message(
            f'user_{doctor.id}',
            'CONSULT_ASSIGNED',
            {
                'id': consult.id,
                'patient_name': consult.patient.name,
                'urgency': consult.urgency,
                'message': f"You have been assigned a consult for {consult.patient.name}"
            }
        )
    
    @staticmethod
    def notify_note_added(consult, note):
        """
        Notify relevant parties about new note.
        """
        # Notify assigned doctor if note is not by them
        if consult.assigned_to and consult.assigned_to != note.author:
            NotificationService._send_ws_message(
                f'user_{consult.assigned_to.id}',
                'NEW_NOTE',
                {
                    'id': consult.id,
                    'note_id': note.id,
                    'author': note.author.get_full_name(),
                    'message': f"New note from {note.author.get_full_name()} on consult #{consult.id}"
                }
            )
            
        # Notify requester if note is not by them
        if consult.requester != note.author:
            NotificationService._send_ws_message(
                f'user_{consult.requester.id}',
                'NEW_NOTE',
                {
                    'id': consult.id,
                    'note_id': note.id,
                    'author': note.author.get_full_name(),
                    'message': f"New note from {note.author.get_full_name()} on consult #{consult.id}"
                }
            )
    
    @staticmethod
    def notify_consult_completed(consult):
        """
        Notify requester about completion.
        """
        # Send email
        EmailService.send_consult_completed_notification(consult)
        
        # Real-time notification to requester
        NotificationService._send_ws_message(
            f'user_{consult.requester.id}',
            'CONSULT_COMPLETED',
            {
                'id': consult.id,
                'patient_name': consult.patient.name,
                'message': f"Consult for {consult.patient.name} has been completed"
            }
        )
    
    @staticmethod
    def escalate_to_hod(consult):
        """
        Notify HOD about escalation.
        """
        if consult.target_department.head:
            # Real-time notification to HOD
            NotificationService._send_ws_message(
                f'user_{consult.target_department.head.id}',
                'CONSULT_ESCALATED',
                {
                    'id': consult.id,
                    'patient_name': consult.patient.name,
                    'urgency': consult.urgency,
                    'message': f"URGENT: Consult for {consult.patient.name} is overdue"
                }
            )
