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
    )

    for consult in consults_to_check:
        max_response_time = consult.target_department.max_response_time
        if now > consult.created_at + timedelta(minutes=max_response_time):
            consult.is_overdue = True
            consult.save()

            # Trigger delay action
            action = consult.target_department.delay_action
            if action == 'NOTIFY_HOD':
                NotificationService.notify_hod_of_delay(consult)
            elif action == 'ESCALATE':
                # Escalate to the next most senior doctor in the department
                next_doctor = User.objects.filter(
                    department=consult.target_department,
                    hierarchy_number__lt=consult.assigned_to.hierarchy_number if consult.assigned_to else 100
                ).order_by('-hierarchy_number').first()
                if next_doctor:
                    ConsultService.assign_consult(consult, next_doctor)
            elif action == 'AUTO_ASSIGN':
                # Assign to the most junior doctor in the department
                junior_doctor = User.objects.filter(
                    department=consult.target_department,
                    is_active=True
                ).order_by('-hierarchy_number').first()
                if junior_doctor:
                    ConsultService.assign_consult(consult, junior_doctor)
            # MARK_OVERDUE is handled by setting is_overdue = True
