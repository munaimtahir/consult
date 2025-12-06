from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import ConsultRequest
from apps.notifications.services import NotificationService
from apps.accounts.models import User
from .services import ConsultService

@shared_task
def check_delayed_consults():
    """
    Checks for consults that have exceeded their acknowledgment time
    and triggers the appropriate delay action.
    """
    now = timezone.now()
    consults_to_check = ConsultRequest.objects.filter(
        status='SUBMITTED',
        acknowledged_at__isnull=True
    ).select_related('target_department', 'assigned_to')

    for consult in consults_to_check:
        max_response_time = consult.target_department.max_response_time
        if now > consult.created_at + timedelta(minutes=max_response_time):
            consult.is_overdue = True
            consult.save()

            # Trigger delay action
            action = consult.target_department.delay_action
            if action == 'NOTIFY_HOD':
                if consult.target_department.head:
                    NotificationService.notify_hod_escalation(consult, consult.target_department.head)
            elif action == 'ESCALATE':
                # Escalate to the next most senior doctor in the department
                current_seniority = consult.assigned_to.seniority_level if consult.assigned_to else 0
                next_doctor = User.objects.filter(
                    department=consult.target_department,
                    seniority_level__gt=current_seniority,
                    is_active=True,
                    role__in=['DOCTOR', 'HOD', 'DEPARTMENT_USER']
                ).order_by('seniority_level').first()
                if next_doctor:
                    ConsultService.assign_consult(consult, next_doctor)
            elif action == 'AUTO_ASSIGN':
                # Assign to the most junior doctor in the department
                junior_doctor = User.objects.filter(
                    department=consult.target_department,
                    is_active=True,
                    role__in=['DOCTOR', 'HOD', 'DEPARTMENT_USER']
                ).order_by('seniority_level').first()
                if junior_doctor:
                    ConsultService.assign_consult(consult, junior_doctor)
            # MARK_OVERDUE is handled by setting is_overdue = True

@shared_task
def check_sla_breaches():
    """
    Checks for consults that have breached their SLA and sends notifications.
    This task should run periodically (e.g., every 15 minutes).
    """
    from apps.core.services.escalation_service import EscalationService
    
    now = timezone.now()
    
    # Update overdue status for all active consults
    EscalationService.update_overdue_status_all()
    
    # Find consults that have breached SLA but haven't been notified yet
    # We check for consults that are overdue and haven't been completed/closed
    breached_consults = ConsultRequest.objects.filter(
        is_overdue=True,
        expected_response_time__lt=now,
        status__in=['SUBMITTED', 'ACKNOWLEDGED', 'IN_PROGRESS', 'MORE_INFO_REQUIRED']
    ).select_related('target_department', 'assigned_to', 'requester', 'patient')
    
    for consult in breached_consults:
        # Check if we've already sent an SLA breach notification recently (within last hour)
        from apps.notifications.models import EmailNotification
        recent_notification = EmailNotification.objects.filter(
            consult=consult,
            notification_type='SLA_BREACH',
            sent_at__gte=now - timedelta(hours=1)
        ).exists()
        
        if not recent_notification:
            # Try to escalate if needed
            EscalationService.check_and_escalate(consult)
            
            # Send SLA breach notification
            NotificationService.notify_sla_breach(consult)
