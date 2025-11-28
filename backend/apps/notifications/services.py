"""
Notification Service
Handles sending real-time notifications and emails.
"""

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from apps.core.services.email_service import EmailService
from apps.core.constants import get_urgency_color

class NotificationService:
    """Provides a centralized service for handling notifications.

    This class is responsible for sending both real-time WebSocket
    notifications and emails for various events in the consult workflow.
    """
    
    @staticmethod
    def _send_ws_message(group_name, message_type, data):
        """A helper method to send a WebSocket message to a group.

        Args:
            group_name: The name of the channel group to send the message to.
            message_type: The type of the notification message.
            data: A dictionary of data to be sent with the message.
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
        """Sends notifications for a newly created consult.

        This method sends both an email and a real-time WebSocket
        notification to the target department.

        Args:
            consult: The `ConsultRequest` instance that was just created.
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
                'urgency_color': get_urgency_color(consult.urgency),
                'message': f"New {consult.urgency} consult for {consult.patient.name}"
            }
        )
    
    @staticmethod
    def notify_consult_assigned(consult, doctor):
        """Sends notifications when a consult is assigned to a doctor.

        Args:
            consult: The `ConsultRequest` instance that was assigned.
            doctor: The `User` who was assigned the consult.
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
                'urgency_color': get_urgency_color(consult.urgency),
                'message': f"You have been assigned a consult for {consult.patient.name}"
            }
        )
    
    @staticmethod
    def notify_note_added(consult, note):
        """Sends notifications when a new note is added to a consult.

        Notifies the assigned doctor and the original requester, unless
        they are the author of the note.

        Args:
            consult: The `ConsultRequest` the note was added to.
            note: The `ConsultNote` instance that was just created.
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
                    'note_type': note.note_type,
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
                    'note_type': note.note_type,
                    'message': f"New note from {note.author.get_full_name()} on consult #{consult.id}"
                }
            )
    
    @staticmethod
    def notify_consult_completed(consult):
        """Sends notifications when a consult is completed.

        Args:
            consult: The `ConsultRequest` instance that was completed.
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
        """Sends an escalation notification to the Head of Department.

        Args:
            consult: The `ConsultRequest` instance that is being escalated.
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
                    'urgency_color': get_urgency_color(consult.urgency),
                    'message': f"URGENT: Consult for {consult.patient.name} is overdue"
                }
            )

    @staticmethod
    def notify_consult_escalated(consult, from_user, to_user, level):
        """Sends notifications when a consult is escalated.

        Args:
            consult: The ConsultRequest instance.
            from_user: The user the consult was escalated from.
            to_user: The user the consult was escalated to.
            level: The new escalation level.
        """
        # Notify the new assignee
        if to_user:
            NotificationService._send_ws_message(
                f'user_{to_user.id}',
                'CONSULT_ESCALATED_TO_YOU',
                {
                    'id': consult.id,
                    'patient_name': consult.patient.name,
                    'urgency': consult.urgency,
                    'urgency_color': get_urgency_color(consult.urgency),
                    'escalation_level': level,
                    'message': f"Escalated consult for {consult.patient.name} assigned to you"
                }
            )

        # Notify the previous assignee
        if from_user and from_user != to_user:
            NotificationService._send_ws_message(
                f'user_{from_user.id}',
                'CONSULT_ESCALATED_FROM_YOU',
                {
                    'id': consult.id,
                    'patient_name': consult.patient.name,
                    'message': f"Consult for {consult.patient.name} has been escalated"
                }
            )

    @staticmethod
    def notify_hod_escalation(consult, hod):
        """Notifies HOD about an escalated consult.

        Args:
            consult: The ConsultRequest instance.
            hod: The HOD User to notify.
        """
        NotificationService._send_ws_message(
            f'user_{hod.id}',
            'HOD_ESCALATION_ALERT',
            {
                'id': consult.id,
                'patient_name': consult.patient.name,
                'urgency': consult.urgency,
                'urgency_color': get_urgency_color(consult.urgency),
                'escalation_level': consult.escalation_level,
                'message': f"ATTENTION: Consult #{consult.id} for {consult.patient.name} has been escalated"
            }
        )

    @staticmethod
    def notify_requester_delay(consult):
        """Notifies the requester that their consult is delayed.

        Args:
            consult: The ConsultRequest instance.
        """
        NotificationService._send_ws_message(
            f'user_{consult.requester.id}',
            'CONSULT_DELAYED',
            {
                'id': consult.id,
                'patient_name': consult.patient.name,
                'target_department': consult.target_department.name,
                'message': f"Your consult for {consult.patient.name} is taking longer than expected"
            }
        )

    @staticmethod
    def notify_sla_warning(consult):
        """Sends a warning when consult is approaching SLA deadline.

        Args:
            consult: The ConsultRequest instance.
        """
        # Notify assigned doctor
        if consult.assigned_to:
            NotificationService._send_ws_message(
                f'user_{consult.assigned_to.id}',
                'SLA_WARNING',
                {
                    'id': consult.id,
                    'patient_name': consult.patient.name,
                    'urgency': consult.urgency,
                    'urgency_color': get_urgency_color(consult.urgency),
                    'message': f"Warning: Consult for {consult.patient.name} is approaching deadline"
                }
            )

        # Notify department
        NotificationService._send_ws_message(
            f'dept_{consult.target_department.id}',
            'SLA_WARNING',
            {
                'id': consult.id,
                'patient_name': consult.patient.name,
                'urgency': consult.urgency,
                'urgency_color': get_urgency_color(consult.urgency),
                'message': f"Warning: Consult #{consult.id} is approaching deadline"
            }
        )

    @staticmethod
    def notify_auto_assignment(consult, doctor, assignment_mode):
        """Notifies about automatic assignment.

        Args:
            consult: The ConsultRequest instance.
            doctor: The assigned User.
            assignment_mode: The mode used for assignment.
        """
        mode_display = {
            'LOAD_BALANCE': 'load balancing',
            'ON_CALL': 'on-call schedule',
            'ROUND_ROBIN': 'round robin',
            'SENIORITY': 'seniority-based'
        }.get(assignment_mode, 'auto-assignment')

        NotificationService._send_ws_message(
            f'user_{doctor.id}',
            'AUTO_ASSIGNED',
            {
                'id': consult.id,
                'patient_name': consult.patient.name,
                'urgency': consult.urgency,
                'urgency_color': get_urgency_color(consult.urgency),
                'assignment_mode': assignment_mode,
                'message': f"New {consult.urgency} consult auto-assigned to you via {mode_display}"
            }
        )
