"""
Email Service
Handles sending transactional emails using Django's email backend.
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

class EmailService:
    """
    Service for sending emails.
    """
    
    @staticmethod
    def send_email(subject, template_name, context, recipient_list):
        """
        Send an email using a template.
        """
        html_message = render_to_string(template_name, context)
        plain_message = strip_tags(html_message)
        
        try:
            send_mail(
                subject=subject,
                message=plain_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            return True
        except Exception as e:
            # Log error
            print(f"Error sending email: {e}")
            return False
    
    @staticmethod
    def send_new_consult_notification(consult):
        """
        Send email when new consult is created.
        """
        subject = f'New {consult.urgency} Consult Request: {consult.patient.name}'
        context = {
            'consult': consult,
            'patient': consult.patient,
            'requester': consult.requester,
            'target_department': consult.target_department,
            'url': f"{settings.FRONTEND_URL}/consults/{consult.id}" if hasattr(settings, 'FRONTEND_URL') else f"http://localhost:3000/consults/{consult.id}"
        }
        
        # Send to HOD of target department
        recipient_list = []
        if consult.target_department.head and consult.target_department.head.email:
            recipient_list.append(consult.target_department.head.email)
            
        # Also send to department contact email if available?
        # For now, just HOD.
        
        if recipient_list:
            EmailService.send_email(
                subject=subject,
                template_name='emails/new_consult.html',
                context=context,
                recipient_list=recipient_list
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
                recipient_list=recipient_list
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
                recipient_list=recipient_list
            )
