"""
Consult Service
Business logic for consult workflow.
"""

from django.utils import timezone
from django.db import transaction
from .models import ConsultRequest, ConsultNote
from apps.notifications.services import NotificationService
from apps.departments.models import OnCall
from apps.accounts.models import User

class ConsultService:
    """Encapsulates the business logic for the consult workflow.

    This service class provides a set of static methods for performing
    actions related to consult requests, such as creating, assigning, and
    completing them. It ensures that state transitions are handled
    correctly and that necessary side effects, like sending notifications,
    are triggered.
    """
    
    @staticmethod
    def create_consult(requester, patient, target_department, urgency, reason_for_consult, **kwargs):
        """Creates a new consult request and sends notifications.

        If a doctor is on-call for the target department, it auto-assigns
        the consult to them.

        Args:
            requester: The user initiating the request.
            patient: The patient for whom the consult is requested.
            target_department: The department the consult is directed to.
            urgency: The urgency level of the consult.
            reason_for_consult: The reason for the consult.
            **kwargs: Additional fields for the `ConsultRequest` model.

        Returns:
            The newly created `ConsultRequest` instance.
        """
        consult = ConsultRequest(
            patient=patient,
            requester=requester,
            requesting_department=requester.department,
            target_department=target_department,
            urgency=urgency,
            reason_for_consult=reason_for_consult,
            **kwargs
        )

        # Check for on-call doctor
        today = timezone.now().date()
        on_call_entry = OnCall.objects.filter(department=target_department, date=today).first()

        if on_call_entry and on_call_entry.doctor:
            now = timezone.now()
            consult.assigned_to = on_call_entry.doctor
            consult.assigned_by = on_call_entry.doctor  # Auto-assigned to self
            consult.assigned_at = now
            consult.assignment_type = 'auto'
            consult.status = 'IN_PROGRESS'
            consult.acknowledged_at = now
            consult.acknowledged_by = on_call_entry.doctor
            consult.received_by = on_call_entry.doctor
            consult.received_at = now
            consult.last_action_summary = f"Auto-assigned to on-call doctor: {on_call_entry.doctor.get_full_name()}"
            consult.save()
            NotificationService.notify_consult_assigned(consult, on_call_entry.doctor)
        else:
            # If no on-call doctor, try to assign to the most junior doctor
            junior_doctor = User.objects.filter(
                department=target_department,
                is_active=True
            ).order_by('-hierarchy_number').first()

            if junior_doctor:
                now = timezone.now()
                consult.assigned_to = junior_doctor
                consult.assigned_by = junior_doctor  # Auto-assigned to self
                consult.assigned_at = now
                consult.assignment_type = 'auto'
                consult.status = 'IN_PROGRESS'
                consult.acknowledged_at = now
                consult.acknowledged_by = junior_doctor
                consult.received_by = junior_doctor
                consult.received_at = now
                consult.last_action_summary = f"Auto-assigned by hierarchy to: {junior_doctor.get_full_name()}"
                consult.save()
                NotificationService.notify_consult_assigned(consult, junior_doctor)
            else:
                # Fallback: No on-call, no junior doctor found. Create unassigned consult.
                consult.save()
                NotificationService.notify_new_consult(consult)
        
        return consult
    
    @staticmethod
    def assign_consult(consult, doctor, assigner=None):
        """Assigns a consult to a doctor and updates its status.

        Args:
            consult: The `ConsultRequest` to be assigned.
            doctor: The `User` to whom the consult is being assigned.
            assigner: The user performing the assignment (optional).

        Returns:
            The updated `ConsultRequest` instance.
        """
        now = timezone.now()
        consult.assigned_to = doctor
        consult.assigned_by = assigner
        consult.assigned_at = now
        consult.assignment_type = 'manual'
        
        # Update status based on current state
        if consult.status == 'SUBMITTED':
            consult.status = 'ACKNOWLEDGED'
            consult.acknowledged_at = now
            consult.acknowledged_by = assigner or doctor
            # Also set new received fields
            consult.received_by = assigner or doctor
            consult.received_at = now
        else:
            consult.status = 'IN_PROGRESS'
            
        consult.last_action_summary = f"Assigned to {doctor.get_full_name()}"
        consult.save()
        
        NotificationService.notify_consult_assigned(consult, doctor)
        
        return consult
    
    @staticmethod
    def acknowledge_consult(consult, user):
        """Acknowledges a consult request.

        Args:
            consult: The `ConsultRequest` to be acknowledged.
            user: The user acknowledging the consult.

        Returns:
            The updated `ConsultRequest` instance.
        """
        consult.status = 'ACKNOWLEDGED'
        consult.acknowledged_at = timezone.now()
        consult.acknowledged_by = user
        consult.last_action_summary = f"Acknowledged by {user.get_full_name()}"
        consult.save()
        
        NotificationService.notify_consult_acknowledged(consult)

        return consult
    
    @staticmethod
    @transaction.atomic
    def acknowledge_and_assign_consult(consult, acknowledger, assigned_to_user):
        """Acknowledges and assigns a consult in one atomic action.

        This is the new workflow where acknowledgement and assignment must happen together.
        Uses @transaction.atomic to ensure both operations succeed or fail together.
        
        Args:
            consult: The `ConsultRequest` to be acknowledged and assigned.
            acknowledger: The user acknowledging the consult (HOD or delegated receiver).
            assigned_to_user: The user to whom the consult is being assigned.

        Returns:
            The updated `ConsultRequest` instance.
        """
        now = timezone.now()
        
        # Set receipt/acknowledgement fields
        consult.received_by = acknowledger
        consult.received_at = now
        
        # Also set deprecated acknowledged_by for backward compatibility
        consult.acknowledged_by = acknowledger
        consult.acknowledged_at = now
        
        # Set assignment fields
        consult.assigned_to = assigned_to_user
        consult.assigned_by = acknowledger
        consult.assigned_at = now
        consult.assignment_type = 'manual'
        
        # Update status to IN_PROGRESS
        consult.status = 'IN_PROGRESS'
        
        consult.last_action_summary = f"Acknowledged and assigned to {assigned_to_user.get_full_name()} by {acknowledger.get_full_name()}"
        consult.save()
        
        # Send notifications
        NotificationService.notify_consult_assigned(consult, assigned_to_user)
        
        return consult
    
    @staticmethod
    def add_note(consult, author, content, note_type='PROGRESS', **kwargs):
        """Adds a note to a consult and updates its status.

        If the note is final, it also completes the consult.

        Args:
            consult: The `ConsultRequest` to add the note to.
            author: The `User` writing the note.
            content: The content of the note.
            note_type: The type of the note.
            **kwargs: Additional fields for the `ConsultNote` model.

        Returns:
            The newly created `ConsultNote` instance.
        """
        note = ConsultNote.objects.create(
            consult=consult,
            author=author,
            content=content,
            note_type=note_type,
            **kwargs
        )
        
        # The ConsultNote's save() method now handles status changes.
        # This service method is now responsible for creating the note
        # and triggering side effects like notifications.
        
        NotificationService.notify_note_added(consult, note)
        
        return note
    
    @staticmethod
    def complete_consult(consult):
        """Marks a consult as completed.

        Args:
            consult: The `ConsultRequest` to be completed.

        Returns:
            The updated `ConsultRequest` instance.
        """
        consult.status = 'COMPLETED'
        consult.completed_at = timezone.now()
        consult.save()
        
        NotificationService.notify_consult_completed(consult)
        
        return consult
        
    @staticmethod
    def cancel_consult(consult):
        """Cancels a consult request.

        Args:
            consult: The `ConsultRequest` to be cancelled.

        Returns:
            The updated `ConsultRequest` instance.
        """
        consult.status = 'CANCELLED'
        consult.save()
        
        return consult
