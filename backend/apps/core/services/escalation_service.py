"""
Escalation Service
Handles delayed consult escalation and notifications.
"""

from datetime import timedelta
from django.utils import timezone
from django.db.models import Q

# DelayedConsultPolicy model was removed - escalation policies are now handled differently
from apps.accounts.models import User
from apps.consults.models import ConsultRequest


class EscalationService:
    """Provides methods for consult escalation.

    This service handles the escalation of delayed consults,
    including notifications and automatic reassignment.
    """

    @staticmethod
    def check_and_escalate(consult, request=None):
        """Checks if a consult needs escalation and performs it.

        Args:
            consult: The ConsultRequest to check.
            request: Optional HTTP request for audit logging.

        Returns:
            True if escalated, False otherwise.
        """
        if consult.status in ['COMPLETED', 'CANCELLED', 'CLOSED']:
            return False

        # Check if consult is overdue
        if not consult.is_overdue:
            return False

        # Get department delay action
        delay_action = consult.target_department.delay_action if consult.target_department else 'MARK_OVERDUE'
        
        # Only escalate if action is ESCALATE
        if delay_action != 'ESCALATE':
            return False

        # Determine escalation level needed
        escalation_level = EscalationService._calculate_escalation_level(consult)
        
        if escalation_level > consult.escalation_level:
            return EscalationService._perform_escalation(
                consult,
                escalation_level,
                request
            )

        return False

    @staticmethod
    def _calculate_escalation_level(consult):
        """Calculates the appropriate escalation level.

        Args:
            consult: The ConsultRequest.

        Returns:
            Integer escalation level.
        """
        if not consult.expected_response_time:
            return 1
        
        minutes_overdue = (timezone.now() - consult.expected_response_time).total_seconds() / 60
        
        # Default escalation: every 30 minutes overdue = 1 level
        return min(int(minutes_overdue / 30) + 1, 3)

    @staticmethod
    def _perform_escalation(consult, new_level, request=None):
        """Performs the escalation to a senior doctor.

        Args:
            consult: The ConsultRequest.
            new_level: The new escalation level.
            request: Optional HTTP request for audit logging.

        Returns:
            True if escalation was successful.
        """
        from apps.core.services.audit_service import AuditService
        from apps.notifications.services import NotificationService

        original_assignee = consult.assigned_to
        
        # Find a more senior doctor
        senior_doctor = EscalationService._find_senior_doctor(
            consult.target_department,
            consult.assigned_to
        )

        if senior_doctor:
            consult.assigned_to = senior_doctor
            consult.escalation_level = new_level
            consult.save()

            # Log the escalation
            try:
                AuditService.log_consult_escalated(
                    consult,
                    original_assignee,
                    senior_doctor,
                    new_level,
                    request
                )
            except Exception:
                # If audit service fails, continue with escalation
                pass

            # Send notifications
            try:
                NotificationService.notify_consult_escalated(
                    consult,
                    original_assignee,
                    senior_doctor,
                    new_level
                )
            except Exception:
                # If notification fails, continue
                pass

            # Always notify HOD if available
            if consult.target_department and consult.target_department.head:
                try:
                    NotificationService.notify_hod_escalation(
                        consult,
                        consult.target_department.head
                    )
                except Exception:
                    pass

            return True

        # If no senior doctor, just update level and notify HOD
        consult.escalation_level = new_level
        consult.save()

        if consult.target_department and consult.target_department.head:
            try:
                NotificationService.notify_hod_escalation(
                    consult,
                    consult.target_department.head
                )
            except Exception:
                pass

        return True

    @staticmethod
    def _find_senior_doctor(department, current_assignee):
        """Finds a more senior doctor to handle the consult.

        Args:
            department: The Department instance.
            current_assignee: The currently assigned User or None.

        Returns:
            User instance or None.
        """
        current_seniority = current_assignee.seniority_level if current_assignee else 0

        # Find available senior doctors
        senior_doctors = User.objects.filter(
            department=department,
            is_active=True,
            seniority_level__gt=current_seniority,
            role__in=['DOCTOR', 'HOD', 'DEPARTMENT_USER']
        ).order_by('seniority_level')

        return senior_doctors.first()

    @staticmethod
    def get_overdue_consults(department=None):
        """Gets all overdue consults, optionally filtered by department.

        Args:
            department: Optional Department to filter by.

        Returns:
            QuerySet of overdue ConsultRequest objects.
        """
        queryset = ConsultRequest.objects.filter(
            is_overdue=True,
            status__in=['SUBMITTED', 'ACKNOWLEDGED', 'IN_PROGRESS', 'MORE_INFO_REQUIRED']
        ).select_related(
            'patient',
            'requester',
            'requesting_department',
            'target_department',
            'assigned_to'
        )

        if department:
            queryset = queryset.filter(target_department=department)

        return queryset.order_by('expected_response_time')

    @staticmethod
    def get_approaching_deadline_consults(department=None, threshold_minutes=30):
        """Gets consults approaching their SLA deadline.

        Args:
            department: Optional Department to filter by.
            threshold_minutes: Minutes before deadline to include.

        Returns:
            QuerySet of ConsultRequest objects approaching deadline.
        """
        threshold_time = timezone.now() + timedelta(minutes=threshold_minutes)
        
        queryset = ConsultRequest.objects.filter(
            is_overdue=False,
            status__in=['SUBMITTED', 'ACKNOWLEDGED', 'IN_PROGRESS', 'MORE_INFO_REQUIRED'],
            expected_response_time__lte=threshold_time,
            expected_response_time__gt=timezone.now()
        ).select_related(
            'patient',
            'requester',
            'requesting_department',
            'target_department',
            'assigned_to'
        )

        if department:
            queryset = queryset.filter(target_department=department)

        return queryset.order_by('expected_response_time')

    @staticmethod
    def update_overdue_status_all():
        """Updates the is_overdue status for all active consults.

        This is typically run as a periodic task.

        Returns:
            Number of consults updated.
        """
        now = timezone.now()
        updated = ConsultRequest.objects.filter(
            status__in=['SUBMITTED', 'ACKNOWLEDGED', 'IN_PROGRESS', 'MORE_INFO_REQUIRED'],
            is_overdue=False,
            expected_response_time__lt=now
        ).exclude(status__in=['COMPLETED', 'CANCELLED', 'CLOSED']).update(is_overdue=True)

        return updated


# Celery task wrapper for update_overdue_status_all
from celery import shared_task

@shared_task
def update_overdue_status_task():
    """Celery task to update overdue status for all consults."""
    return EscalationService.update_overdue_status_all()
