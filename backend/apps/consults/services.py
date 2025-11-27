"""
Consult Service
Business logic for consult workflow.
"""

from django.utils import timezone
from .models import ConsultRequest, ConsultNote
from apps.notifications.services import NotificationService

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
        consult = ConsultRequest.objects.create(
            patient=patient,
            requester=requester,
            target_department=target_department,
            urgency=urgency,
            reason_for_consult=reason_for_consult,
            **kwargs
        )
        
        # Send real-time notification to target department
        NotificationService.notify_new_consult(consult)
        
        return consult
    
    @staticmethod
    def assign_consult(consult, doctor):
        """Assigns a consult to a doctor and updates its status.

        Args:
            consult: The `ConsultRequest` to be assigned.
            doctor: The `User` to whom the consult is being assigned.

        Returns:
            The updated `ConsultRequest` instance.
        """
        consult.assigned_to = doctor
        
        # Update status based on current state
        if consult.status == 'PENDING':
            consult.status = 'ACKNOWLEDGED'
            consult.acknowledged_at = timezone.now()
        elif consult.status == 'ACKNOWLEDGED':
            consult.status = 'IN_PROGRESS'
            
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
        consult.save()
        
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
        
        # Update first_response_at if this is the first note (not tracked in model yet, but logic is here)
        # Also update status to IN_PROGRESS if it was ACKNOWLEDGED
        if consult.status == 'ACKNOWLEDGED':
            consult.status = 'IN_PROGRESS'
            consult.save()
            
        # If this is a final note, complete the consult
        if note.is_final:
            ConsultService.complete_consult(consult)
        
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
