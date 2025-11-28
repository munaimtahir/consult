"""
Assignment Service
Handles auto-assignment, load balancing, and on-call routing.
"""

from django.utils import timezone
from django.db.models import Count, Q

from apps.core.models import AssignmentPolicy, OnCallSchedule
from apps.accounts.models import User


class AssignmentService:
    """Provides methods for automatic consult assignment.

    This service implements various assignment strategies including
    round-robin, load balancing, seniority-based, and on-call routing.
    """

    @staticmethod
    def get_assignment_policy(department, urgency):
        """Gets the assignment policy for a department and urgency level.

        Args:
            department: The Department instance.
            urgency: The urgency level string.

        Returns:
            AssignmentPolicy instance or None if not configured.
        """
        try:
            return AssignmentPolicy.objects.get(
                department=department,
                urgency=urgency,
                is_active=True
            )
        except AssignmentPolicy.DoesNotExist:
            return None

    @staticmethod
    def auto_assign(consult, request=None):
        """Automatically assigns a consult based on department policy.

        Args:
            consult: The ConsultRequest to assign.
            request: Optional HTTP request for audit logging.

        Returns:
            The assigned User or None if no auto-assignment policy.
        """
        policy = AssignmentService.get_assignment_policy(
            consult.target_department,
            consult.urgency
        )

        if not policy or policy.assignment_mode == 'MANUAL':
            return None

        assignee = None
        mode = policy.assignment_mode

        if mode == 'ON_CALL':
            assignee = AssignmentService._assign_on_call(consult.target_department)
        elif mode == 'LOAD_BALANCE':
            assignee = AssignmentService._assign_load_balance(
                consult.target_department,
                policy.min_seniority
            )
        elif mode == 'ROUND_ROBIN':
            assignee = AssignmentService._assign_round_robin(
                consult.target_department,
                policy.min_seniority
            )
        elif mode == 'SENIORITY':
            assignee = AssignmentService._assign_by_seniority(
                consult.target_department,
                policy.min_seniority,
                consult.urgency
            )

        if assignee:
            from apps.core.services.audit_service import AuditService
            AuditService.log_auto_assignment(consult, assignee, mode, request)

        return assignee

    @staticmethod
    def _assign_on_call(department):
        """Assigns to the currently on-call doctor.

        Args:
            department: The Department instance.

        Returns:
            The on-call User or None.
        """
        now = timezone.now()
        try:
            schedule = OnCallSchedule.objects.get(
                department=department,
                is_active=True,
                start_time__lte=now,
                end_time__gte=now
            )
            return schedule.user
        except OnCallSchedule.DoesNotExist:
            # Fall back to any on-call user in department
            return User.objects.filter(
                department=department,
                is_on_call=True,
                is_active=True
            ).first()

    @staticmethod
    def _assign_load_balance(department, min_seniority=1):
        """Assigns to the doctor with the fewest active consults.

        Args:
            department: The Department instance.
            min_seniority: Minimum seniority level required.

        Returns:
            The User with least load or None.
        """
        eligible_users = User.objects.filter(
            department=department,
            is_active=True,
            seniority_level__gte=min_seniority,
            role__in=['DOCTOR', 'HOD', 'DEPARTMENT_USER']
        ).annotate(
            active_consults=Count(
                'assigned_consults',
                filter=Q(assigned_consults__status__in=['PENDING', 'ACKNOWLEDGED', 'IN_PROGRESS'])
            )
        ).order_by('active_consults', '-seniority_level')

        return eligible_users.first()

    @staticmethod
    def _assign_round_robin(department, min_seniority=1):
        """Assigns to the next doctor in rotation.

        Uses the last assignment time to determine rotation order.

        Args:
            department: The Department instance.
            min_seniority: Minimum seniority level required.

        Returns:
            The next User in rotation or None.
        """
        from apps.consults.models import ConsultRequest

        # Get eligible users
        eligible_users = list(User.objects.filter(
            department=department,
            is_active=True,
            seniority_level__gte=min_seniority,
            role__in=['DOCTOR', 'HOD', 'DEPARTMENT_USER']
        ).order_by('id'))

        if not eligible_users:
            return None

        # Find the last assigned user
        last_assigned = ConsultRequest.objects.filter(
            target_department=department,
            assigned_to__isnull=False
        ).order_by('-updated_at').first()

        if last_assigned and last_assigned.assigned_to in eligible_users:
            # Get the next user in the list
            last_index = eligible_users.index(last_assigned.assigned_to)
            next_index = (last_index + 1) % len(eligible_users)
            return eligible_users[next_index]

        return eligible_users[0]

    @staticmethod
    def _assign_by_seniority(department, min_seniority=1, urgency='ROUTINE'):
        """Assigns based on seniority level.

        Emergency consults go to more senior doctors,
        routine consults can go to junior doctors.

        Args:
            department: The Department instance.
            min_seniority: Minimum seniority level required.
            urgency: The consult urgency level.

        Returns:
            The appropriate User based on seniority or None.
        """
        seniority_order = 'seniority_level' if urgency == 'ROUTINE' else '-seniority_level'

        eligible_users = User.objects.filter(
            department=department,
            is_active=True,
            seniority_level__gte=min_seniority,
            role__in=['DOCTOR', 'HOD', 'DEPARTMENT_USER']
        ).annotate(
            active_consults=Count(
                'assigned_consults',
                filter=Q(assigned_consults__status__in=['PENDING', 'ACKNOWLEDGED', 'IN_PROGRESS'])
            )
        ).order_by(seniority_order, 'active_consults')

        return eligible_users.first()

    @staticmethod
    def get_load_balance_stats(department):
        """Gets load balance statistics for a department.

        Args:
            department: The Department instance.

        Returns:
            List of dicts with user load information.
        """
        users = User.objects.filter(
            department=department,
            is_active=True,
            role__in=['DOCTOR', 'HOD', 'DEPARTMENT_USER']
        ).annotate(
            active_consults=Count(
                'assigned_consults',
                filter=Q(assigned_consults__status__in=['PENDING', 'ACKNOWLEDGED', 'IN_PROGRESS'])
            ),
            pending_consults=Count(
                'assigned_consults',
                filter=Q(assigned_consults__status__in=['PENDING', 'ACKNOWLEDGED'])
            ),
            completed_today=Count(
                'assigned_consults',
                filter=Q(
                    assigned_consults__status='COMPLETED',
                    assigned_consults__completed_at__date=timezone.now().date()
                )
            )
        ).order_by('-active_consults')

        return [
            {
                'user_id': user.id,
                'name': user.get_full_name(),
                'designation': user.designation_display,
                'seniority_level': user.seniority_level,
                'is_on_call': user.is_on_call,
                'active_consults': user.active_consults,
                'pending_consults': user.pending_consults,
                'completed_today': user.completed_today,
            }
            for user in users
        ]

    @staticmethod
    def get_on_call_doctor(department):
        """Gets the currently on-call doctor for a department.

        Args:
            department: The Department instance.

        Returns:
            User instance or None.
        """
        now = timezone.now()
        try:
            schedule = OnCallSchedule.objects.get(
                department=department,
                is_active=True,
                start_time__lte=now,
                end_time__gte=now
            )
            return schedule.user
        except OnCallSchedule.DoesNotExist:
            return User.objects.filter(
                department=department,
                is_on_call=True,
                is_active=True
            ).first()
