"""
Consult Service
Business logic for consult workflow.
"""

from django.utils import timezone
from .models import ConsultRequest, ConsultNote
from apps.notifications.services import NotificationService

class ConsultService:
    """Business logic for consult workflow"""
    
    @staticmethod
    def create_consult(requester, patient, target_department, urgency, reason_for_consult, **kwargs):
        """Create a new consult request"""
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
        """Assign consult to a specific doctor"""
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
        """Acknowledge a consult request"""
        consult.status = 'ACKNOWLEDGED'
        consult.acknowledged_at = timezone.now()
        consult.save()
        
        return consult
    
    @staticmethod
    def add_note(consult, author, content, note_type='PROGRESS', **kwargs):
        """Add a consult note and update timestamps"""
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
        """Mark consult as completed"""
        consult.status = 'COMPLETED'
        consult.completed_at = timezone.now()
        consult.save()
        
        NotificationService.notify_consult_completed(consult)
        
        return consult
        
    @staticmethod
    def cancel_consult(consult):
        """Cancel a consult request"""
        consult.status = 'CANCELLED'
        consult.save()
        
        return consult
