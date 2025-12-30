"""
Audit Service
Handles logging of all significant actions in the system.
"""

from apps.core.models import AuditLog


class AuditService:
    """Provides methods for creating audit log entries.

    This service centralizes all audit logging to ensure
    consistency and completeness of the audit trail.
    """

    @staticmethod
    def log_action(
        action,
        actor=None,
        consult=None,
        target_user=None,
        department=None,
        details=None,
        request=None
    ):
        """Creates an audit log entry.

        Args:
            action: The action type from AuditLog.ACTION_CHOICES.
            actor: The user performing the action.
            consult: Optional related ConsultRequest.
            target_user: Optional user affected by the action.
            department: Optional related Department.
            details: Optional dict with additional details.
            request: Optional HTTP request for IP/user-agent.

        Returns:
            The created AuditLog instance.
        """
        ip_address = None
        user_agent = ''

        if request:
            ip_address = AuditService._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]

        return AuditLog.objects.create(
            action=action,
            actor=actor,
            consult=consult,
            target_user=target_user,
            department=department,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent
        )

    @staticmethod
    def log_consult_created(consult, actor, request=None):
        """Logs a consult creation event."""
        return AuditService.log_action(
            action='CONSULT_CREATED',
            actor=actor,
            consult=consult,
            department=consult.target_department,
            details={
                'patient_id': consult.patient_id,
                'urgency': consult.urgency,
                'target_department': consult.target_department.name
            },
            request=request
        )

    @staticmethod
    def log_consult_acknowledged(consult, actor, request=None):
        """Logs a consult acknowledgement event."""
        return AuditService.log_action(
            action='CONSULT_ACKNOWLEDGED',
            actor=actor,
            consult=consult,
            department=consult.target_department,
            details={
                'acknowledged_by': actor.get_full_name() if actor else None
            },
            request=request
        )

    @staticmethod
    def log_consult_assigned(consult, assignee, assigned_by, request=None):
        """Logs a consult assignment event."""
        return AuditService.log_action(
            action='CONSULT_ASSIGNED',
            actor=assigned_by,
            consult=consult,
            target_user=assignee,
            department=consult.target_department,
            details={
                'assigned_to': assignee.get_full_name(),
                'assigned_by': assigned_by.get_full_name() if assigned_by else 'System'
            },
            request=request
        )

    @staticmethod
    def log_consult_completed(consult, actor, request=None):
        """Logs a consult completion event."""
        return AuditService.log_action(
            action='CONSULT_COMPLETED',
            actor=actor,
            consult=consult,
            department=consult.target_department,
            details={
                'completed_by': actor.get_full_name() if actor else None,
                'time_to_completion': str(consult.time_to_completion) if consult.time_to_completion else None
            },
            request=request
        )

    @staticmethod
    def log_consult_escalated(consult, from_user, to_user, level, request=None):
        """Logs a consult escalation event."""
        return AuditService.log_action(
            action='CONSULT_ESCALATED',
            actor=from_user,
            consult=consult,
            target_user=to_user,
            department=consult.target_department,
            details={
                'from_user': from_user.get_full_name() if from_user else 'System',
                'to_user': to_user.get_full_name() if to_user else None,
                'escalation_level': level
            },
            request=request
        )

    @staticmethod
    def log_note_added(consult, note, actor, request=None):
        """Logs a note being added to a consult."""
        return AuditService.log_action(
            action='NOTE_ADDED',
            actor=actor,
            consult=consult,
            department=consult.target_department,
            details={
                'note_id': note.id,
                'note_type': note.note_type,
                'is_final': note.is_final
            },
            request=request
        )

    @staticmethod
    def log_auto_assignment(consult, assignee, mode, request=None):
        """Logs an auto-assignment event."""
        action_map = {
            'LOAD_BALANCE': 'LOAD_BALANCE_ASSIGNED',
            'ON_CALL': 'ON_CALL_ASSIGNED',
            'ROUND_ROBIN': 'AUTO_ASSIGNED',
            'SENIORITY': 'AUTO_ASSIGNED',
        }
        return AuditService.log_action(
            action=action_map.get(mode, 'AUTO_ASSIGNED'),
            actor=None,
            consult=consult,
            target_user=assignee,
            department=consult.target_department,
            details={
                'assignment_mode': mode,
                'assigned_to': assignee.get_full_name()
            },
            request=request
        )

    @staticmethod
    def log_hod_override(consult, original_assignee, new_assignee, hod, request=None):
        """Logs an HOD override of an assignment."""
        return AuditService.log_action(
            action='HOD_OVERRIDE',
            actor=hod,
            consult=consult,
            target_user=new_assignee,
            department=consult.target_department,
            details={
                'original_assignee': original_assignee.get_full_name() if original_assignee else None,
                'new_assignee': new_assignee.get_full_name(),
                'override_by': hod.get_full_name()
            },
            request=request
        )

    @staticmethod
    def log_unauthorized_access(user, resource_type, resource_id, action_attempted, request=None):
        """Logs an unauthorized access attempt."""
        ip_address = None
        user_agent = ''

        if request:
            ip_address = AuditService._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]

        # Log unauthorized access attempt to audit log
        audit_log = AuditService.log_action(
            action='UNAUTHORIZED_ACCESS',
            actor=user,
            details={
                'resource_type': resource_type,
                'resource_id': resource_id,
                'action_attempted': action_attempted,
                'ip_address': ip_address,
                'user_agent': user_agent
            },
            request=request
        )

        return audit_log

    @staticmethod
    def _get_client_ip(request):
        """Extracts client IP from request headers."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
