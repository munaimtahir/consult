"""
Email Service
Handles sending transactional emails using Django's email backend.
Supports email reply handling through unique tokens.
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from django.utils import timezone
from apps.notifications.models import EmailNotification
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """
    Service for sending emails.
    """
    
    @staticmethod
    def send_email(subject, template_name, context, recipient_list, notification_type=None, consult=None, reply_token=None):
        """
        Send an email using a template and track it in EmailNotification model.
        
        Args:
            subject: Email subject
            template_name: Template path
            context: Template context
            recipient_list: List of recipient email addresses
            notification_type: Type of notification (for tracking)
            consult: ConsultRequest instance (if applicable)
            reply_token: UUID token for email reply handling (auto-generated if not provided)
        
        Returns:
            List of EmailNotification instances created
        """
        html_message = render_to_string(template_name, context)
        plain_message = strip_tags(html_message)
        
        notifications_created = []
        
        for recipient_email in recipient_list:
            try:
                # Get user from email
                from apps.accounts.models import User
                try:
                    recipient_user = User.objects.get(email=recipient_email)
                except User.DoesNotExist:
                    logger.warning(f"User with email {recipient_email} not found, skipping email")
                    continue
                
                # Generate reply token if not provided
                if reply_token is None:
                    import uuid
                    reply_token = uuid.uuid4()
                
                # Add reply token to context for email template
                context_with_token = context.copy()
                context_with_token['reply_token'] = reply_token
                context_with_token['reply_email'] = f"reply+{reply_token}@{settings.EMAIL_DOMAIN}" if hasattr(settings, 'EMAIL_DOMAIN') else f"reply+{reply_token}@pmc.edu.pk"
                
                # Render template with token
                html_message_with_token = render_to_string(template_name, context_with_token)
                plain_message_with_token = strip_tags(html_message_with_token)
                
                # Send email
                send_mail(
                    subject=subject,
                    message=plain_message_with_token,
                    html_message=html_message_with_token,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient_email],
                    fail_silently=False,
                )
                
                # Create EmailNotification record
                notification = EmailNotification.objects.create(
                    notification_type=notification_type or 'CONSULT_GENERATED',
                    consult=consult,
                    recipient=recipient_user,
                    subject=subject,
                    sent_successfully=True,
                    reply_token=reply_token
                )
                notifications_created.append(notification)
                
            except Exception as e:
                logger.error(f"Error sending email to {recipient_email}: {e}")
                
                # Create failed notification record
                try:
                    from apps.accounts.models import User
                    recipient_user = User.objects.get(email=recipient_email)
                    notification = EmailNotification.objects.create(
                        notification_type=notification_type or 'CONSULT_GENERATED',
                        consult=consult,
                        recipient=recipient_user,
                        subject=subject,
                        sent_successfully=False,
                        error_message=str(e),
                        reply_token=reply_token if reply_token else None
                    )
                    notifications_created.append(notification)
                except Exception:
                    pass
        
        return notifications_created
    
    @staticmethod
    def send_new_consult_notification(consult):
        """
        Send email when new consult is created.
        Sends to target department HOD and assigned doctor (if any).
        """
        subject = f'New {consult.urgency} Consult Request: {consult.patient.name}'
        context = {
            'consult': consult,
            'patient': consult.patient,
            'requester': consult.requester,
            'target_department': consult.target_department,
            'url': f"{settings.FRONTEND_URL}/consults/{consult.id}" if hasattr(settings, 'FRONTEND_URL') else f"http://localhost:3000/consults/{consult.id}"
        }
        
        recipient_list = []
        
        # Send to HOD of target department
        if consult.target_department.head and consult.target_department.head.email:
            recipient_list.append(consult.target_department.head.email)
        
        # Send to assigned doctor if different from HOD
        if consult.assigned_to and consult.assigned_to.email:
            if consult.assigned_to.email not in recipient_list:
                recipient_list.append(consult.assigned_to.email)
        
        if recipient_list:
            EmailService.send_email(
                subject=subject,
                template_name='emails/new_consult.html',
                context=context,
                recipient_list=recipient_list,
                notification_type='CONSULT_GENERATED',
                consult=consult
            )
            
    @staticmethod
    def send_consult_assigned_notification(consult):
        """
        Send email when consult is assigned.
        """
        subject = f'Consult Assigned: {consult.patient.name}'
        context = {
            'consult': consult,
            'patient': consult.patient,
            'assigned_to': consult.assigned_to,
            'url': f"{settings.FRONTEND_URL}/consults/{consult.id}" if hasattr(settings, 'FRONTEND_URL') else f"http://localhost:3000/consults/{consult.id}"
        }
        
        recipient_list = []
        if consult.assigned_to and consult.assigned_to.email:
            recipient_list.append(consult.assigned_to.email)
            
        if recipient_list:
            EmailService.send_email(
                subject=subject,
                template_name='emails/consult_assigned.html',
                context=context,
                recipient_list=recipient_list,
                notification_type='REASSIGNMENT',
                consult=consult
            )
    
    @staticmethod
    def send_consult_acknowledged_notification(consult):
        """
        Send email when consult is acknowledged.
        Notifies the requester that their consult has been acknowledged.
        """
        subject = f'Consult Acknowledged: {consult.patient.name}'
        context = {
            'consult': consult,
            'patient': consult.patient,
            'acknowledged_by': consult.acknowledged_by,
            'target_department': consult.target_department,
            'acknowledged_at': consult.acknowledged_at,
            'url': f"{settings.FRONTEND_URL}/consults/{consult.id}" if hasattr(settings, 'FRONTEND_URL') else f"http://localhost:3000/consults/{consult.id}"
        }
        
        recipient_list = []
        if consult.requester and consult.requester.email:
            recipient_list.append(consult.requester.email)
            
        if recipient_list:
            EmailService.send_email(
                subject=subject,
                template_name='emails/consult_acknowledged.html',
                context=context,
                recipient_list=recipient_list,
                notification_type='CONSULT_ACKNOWLEDGED',
                consult=consult
            )
    
    @staticmethod
    def send_note_added_notification(consult, note):
        """
        Send email when a note is added to a consult.
        Notifies relevant parties (requester, assigned doctor) unless they are the author.
        """
        subject = f'New Note Added to Consult #{consult.id}: {consult.patient.name}'
        context = {
            'consult': consult,
            'patient': consult.patient,
            'note': note,
            'note_author': note.author,
            'url': f"{settings.FRONTEND_URL}/consults/{consult.id}" if hasattr(settings, 'FRONTEND_URL') else f"http://localhost:3000/consults/{consult.id}"
        }
        
        recipient_list = []
        
        # Notify requester if they didn't write the note
        if consult.requester and consult.requester.email and consult.requester != note.author:
            recipient_list.append(consult.requester.email)
        
        # Notify assigned doctor if they didn't write the note
        if consult.assigned_to and consult.assigned_to.email and consult.assigned_to != note.author:
            if consult.assigned_to.email not in recipient_list:
                recipient_list.append(consult.assigned_to.email)
        
        if recipient_list:
            EmailService.send_email(
                subject=subject,
                template_name='emails/note_added.html',
                context=context,
                recipient_list=recipient_list,
                notification_type='NOTE_ADDED',
                consult=consult
            )
            
    @staticmethod
    def send_consult_completed_notification(consult):
        """
        Send email when consult is completed.
        """
        subject = f'Consult Completed: {consult.patient.name}'
        context = {
            'consult': consult,
            'patient': consult.patient,
            'completed_by': consult.assigned_to, # Or whoever completed it
            'completed_at': consult.completed_at,
            'url': f"{settings.FRONTEND_URL}/consults/{consult.id}" if hasattr(settings, 'FRONTEND_URL') else f"http://localhost:3000/consults/{consult.id}"
        }
        
        recipient_list = []
        if consult.requester and consult.requester.email:
            recipient_list.append(consult.requester.email)
            
        if recipient_list:
            EmailService.send_email(
                subject=subject,
                template_name='emails/consult_completed.html',
                context=context,
                recipient_list=recipient_list,
                notification_type='CONSULT_CLOSED',
                consult=consult
            )
    
    @staticmethod
    def send_consult_closed_notification(consult):
        """
        Send email when consult is closed.
        Similar to completed but for explicit closure status.
        """
        subject = f'Consult Closed: {consult.patient.name}'
        context = {
            'consult': consult,
            'patient': consult.patient,
            'closed_by': consult.assigned_to,
            'url': f"{settings.FRONTEND_URL}/consults/{consult.id}" if hasattr(settings, 'FRONTEND_URL') else f"http://localhost:3000/consults/{consult.id}"
        }
        
        recipient_list = []
        if consult.requester and consult.requester.email:
            recipient_list.append(consult.requester.email)
        
        # Also notify assigned doctor if different from requester
        if consult.assigned_to and consult.assigned_to.email:
            if consult.assigned_to.email not in recipient_list:
                recipient_list.append(consult.assigned_to.email)
            
        if recipient_list:
            EmailService.send_email(
                subject=subject,
                template_name='emails/consult_closed.html',
                context=context,
                recipient_list=recipient_list,
                notification_type='CONSULT_CLOSED',
                consult=consult
            )
    
    @staticmethod
    def send_sla_breach_notification(consult):
        """
        Send email when SLA time is breached.
        Notifies HOD, assigned doctor, and requester.
        """
        subject = f'URGENT: SLA Breach - Consult #{consult.id} for {consult.patient.name}'
        context = {
            'consult': consult,
            'patient': consult.patient,
            'expected_response_time': consult.expected_response_time,
            'time_overdue': timezone.now() - consult.expected_response_time if consult.expected_response_time else None,
            'url': f"{settings.FRONTEND_URL}/consults/{consult.id}" if hasattr(settings, 'FRONTEND_URL') else f"http://localhost:3000/consults/{consult.id}"
        }
        
        recipient_list = []
        
        # Notify HOD
        if consult.target_department.head and consult.target_department.head.email:
            recipient_list.append(consult.target_department.head.email)
        
        # Notify assigned doctor
        if consult.assigned_to and consult.assigned_to.email:
            if consult.assigned_to.email not in recipient_list:
                recipient_list.append(consult.assigned_to.email)
        
        # Notify requester
        if consult.requester and consult.requester.email:
            if consult.requester.email not in recipient_list:
                recipient_list.append(consult.requester.email)
        
        if recipient_list:
            EmailService.send_email(
                subject=subject,
                template_name='emails/sla_breach.html',
                context=context,
                recipient_list=recipient_list,
                notification_type='SLA_BREACH',
                consult=consult
            )
    
    @staticmethod
    def send_reassignment_notification(consult, previous_assignee=None):
        """
        Send email when consult is reassigned.
        Notifies both the new assignee and previous assignee (if any).
        """
        subject = f'Consult Reassigned: {consult.patient.name}'
        context = {
            'consult': consult,
            'patient': consult.patient,
            'new_assignee': consult.assigned_to,
            'previous_assignee': previous_assignee,
            'url': f"{settings.FRONTEND_URL}/consults/{consult.id}" if hasattr(settings, 'FRONTEND_URL') else f"http://localhost:3000/consults/{consult.id}"
        }
        
        recipient_list = []
        
        # Notify new assignee
        if consult.assigned_to and consult.assigned_to.email:
            recipient_list.append(consult.assigned_to.email)
        
        # Notify previous assignee if different
        if previous_assignee and previous_assignee.email:
            if previous_assignee.email not in recipient_list:
                recipient_list.append(previous_assignee.email)
        
        # Notify requester
        if consult.requester and consult.requester.email:
            if consult.requester.email not in recipient_list:
                recipient_list.append(consult.requester.email)
        
        if recipient_list:
            EmailService.send_email(
                subject=subject,
                template_name='emails/reassignment.html',
                context=context,
                recipient_list=recipient_list,
                notification_type='REASSIGNMENT',
                consult=consult
            )
    
    @staticmethod
    def send_analytics_report(recipient, report_data, report_type='DAILY'):
        """
        Send analytics report email.
        
        Args:
            recipient: User to send report to
            report_data: Dictionary with analytics data
            report_type: Type of report (DAILY, WEEKLY, MONTHLY)
        """
        subject = f'{report_type.title()} Analytics Report - Consult System'
        context = {
            'recipient': recipient,
            'report_data': report_data,
            'report_type': report_type,
            'generated_at': timezone.now(),
            'url': f"{settings.FRONTEND_URL}/analytics" if hasattr(settings, 'FRONTEND_URL') else f"http://localhost:3000/analytics"
        }
        
        recipient_list = []
        if recipient and recipient.email:
            recipient_list.append(recipient.email)
        
        if recipient_list:
            EmailService.send_email(
                subject=subject,
                template_name='emails/analytics_report.html',
                context=context,
                recipient_list=recipient_list,
                notification_type='ANALYTICS',
                consult=None
            )
