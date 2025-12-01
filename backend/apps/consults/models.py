"""
Consult models for Hospital Consult System.
"""

from django.db import models
from django.utils import timezone
from datetime import timedelta


class ConsultRequest(models.Model):
    """Represents a request for a medical consultation.

    This model is the central object in the consult workflow, tracking all
    information related to a single consultation request, from its initiation
    to its completion. It includes details about the patient, the requesting
    and target departments, clinical information, and SLA tracking.

    Attributes:
        patient: A foreign key to the `Patient` model.
        requester: The `User` who initiated the consult request.
        requesting_department: The department initiating the consult.
        target_department: The department to which the consult is directed.
        assigned_to: The `User` currently assigned to handle the consult.
        status: The current status of the consult (e.g., 'PENDING',
                'COMPLETED').
        urgency: The clinical urgency of the consult (e.g., 'EMERGENCY',
                 'ROUTINE').
        reason_for_consult: The primary clinical reason for the request.
        is_overdue: A boolean indicating if the consult has exceeded its SLA.
        escalation_level: An integer tracking the number of times the
                          consult has been escalated.
    """
    
    STATUS_CHOICES = [
        ('SUBMITTED', 'Submitted'),
        ('ACKNOWLEDGED', 'Acknowledged'),
        ('IN_PROGRESS', 'In Progress'),
        ('MORE_INFO_REQUIRED', 'More Information Required'),
        ('COMPLETED', 'Completed'),
        ('CLOSED', 'Closed'),
    ]
    
    URGENCY_CHOICES = [
        ('EMERGENCY', 'Emergency'),
        ('URGENT', 'Urgent'),
        ('ROUTINE', 'Routine'),
    ]
    
    # Core fields
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.PROTECT,
        related_name='consults'
    )
    requester = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='requested_consults'
    )
    requesting_department = models.ForeignKey(
        'departments.Department',
        on_delete=models.PROTECT,
        related_name='outgoing_consults'
    )
    target_department = models.ForeignKey(
        'departments.Department',
        on_delete=models.PROTECT,
        related_name='incoming_consults'
    )
    
    # Assignment
    assigned_to = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_consults',
        help_text='Doctor assigned to handle this consult'
    )
    
    # Status and urgency
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='SUBMITTED'
    )
    urgency = models.CharField(
        max_length=20,
        choices=URGENCY_CHOICES,
        default='ROUTINE'
    )
    
    # Clinical information
    reason_for_consult = models.TextField(
        help_text='Why is this consult being requested?'
    )
    clinical_question = models.TextField(
        blank=True,
        help_text='Specific question for the consulting team'
    )
    relevant_history = models.TextField(
        blank=True,
        help_text='Relevant patient history'
    )
    current_medications = models.TextField(
        blank=True,
        help_text='Current medications'
    )
    vital_signs = models.TextField(
        blank=True,
        help_text='Latest vital signs'
    )
    lab_results = models.TextField(
        blank=True,
        help_text='Relevant lab results'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Audit fields
    acknowledged_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_consults'
    )
    last_action_summary = models.TextField(blank=True)
    
    # SLA tracking
    expected_response_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Expected time for response based on SLA'
    )
    is_overdue = models.BooleanField(
        default=False,
        help_text='Whether this consult is overdue'
    )
    escalation_level = models.IntegerField(
        default=0,
        help_text='Number of times this has been escalated'
    )
    
    class Meta:
        db_table = 'consult_requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['target_department', 'status']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['urgency', '-created_at']),
            models.Index(fields=['is_overdue', 'status']),
        ]
    
    def __str__(self):
        return f"Consult #{self.id} - {self.patient.name} ({self.urgency})"
    
    def save(self, *args, **kwargs):
        """Overrides the default save method to add custom logic.

        This method calculates the `expected_response_time` based on the
        target department's SLA for the given urgency level. It also updates
        the `is_overdue` status before saving.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        if not self.expected_response_time:
            # Get SLA from target department based on urgency
            sla_minutes = {
                'EMERGENCY': self.target_department.emergency_sla,
                'URGENT': self.target_department.urgent_sla,
                'ROUTINE': self.target_department.routine_sla,
            }.get(self.urgency, self.target_department.routine_sla)
            
            base_time = self.created_at or timezone.now()
            self.expected_response_time = base_time + timedelta(minutes=sla_minutes)
        
        # Check if overdue
        if self.status not in ['COMPLETED', 'CANCELLED']:
            self.is_overdue = timezone.now() > self.expected_response_time
        
        super().save(*args, **kwargs)
    
    @property
    def time_elapsed(self):
        """Calculates the time elapsed since the consult was created.

        Returns:
            A `timedelta` object representing the duration.
        """
        if self.completed_at:
            return self.completed_at - self.created_at
        return timezone.now() - self.created_at
    
    @property
    def time_to_acknowledgement(self):
        """Calculates the time it took to acknowledge the consult.

        Returns:
            A `timedelta` object, or `None` if not yet acknowledged.
        """
        if self.acknowledged_at:
            return self.acknowledged_at - self.created_at
        return None
    
    @property
    def time_to_completion(self):
        """Calculates the total time taken to complete the consult.

        Returns:
            A `timedelta` object, or `None` if not yet completed.
        """
        if self.completed_at:
            return self.completed_at - self.created_at
        return None
    
    @property
    def is_pending_assignment(self):
        """Checks if the consult is awaiting assignment to a user.

        Returns:
            True if the consult is pending or acknowledged but not yet
            assigned, False otherwise.
        """
        return self.status in ['PENDING', 'ACKNOWLEDGED'] and not self.assigned_to
    
    @property
    def sla_compliance(self):
        """Determines if the consult met its SLA.

        Returns:
            True if the consult was completed within the expected response
            time, False otherwise.
        """
        if self.completed_at:
            return self.completed_at <= self.expected_response_time
        return not self.is_overdue


class ConsultNote(models.Model):
    """Represents a note associated with a `ConsultRequest`.

    These notes are used to document the progress, findings, and
    recommendations related to a consult. A special 'final' note can be
    used to mark the completion of the consult.

    Attributes:
        consult: A foreign key to the `ConsultRequest` this note belongs to.
        author: The `User` who wrote the note.
        note_type: The type of the note (e.g., 'PROGRESS', 'FINAL').
        content: The main text content of the note.
        is_final: A boolean indicating if this is the final note that
                  completes the consult.
    """
    
    NOTE_TYPE_CHOICES = [
        ('PROGRESS_UPDATE', 'Progress Update'),
        ('PLAN_MANAGEMENT', 'Plan / Management'),
        ('REQUEST_MORE_INFO', 'Request More Information'),
        ('ASSIGNED_TO', 'Assigned To'),
        ('FOLLOW_UP_NEEDED', 'Follow-up Needed'),
        ('CLOSE_CONSULT', 'Close Consult'),
    ]
    
    consult = models.ForeignKey(
        ConsultRequest,
        on_delete=models.CASCADE,
        related_name='notes'
    )
    author = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='consult_notes'
    )
    note_type = models.CharField(
        max_length=20,
        choices=NOTE_TYPE_CHOICES,
        default='PROGRESS_UPDATE'
    )
    content = models.TextField()
    assigned_to = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assignment_notes',
        help_text='User this note is assigning the consult to'
    )
    
    # Recommendations
    recommendations = models.TextField(
        blank=True,
        help_text='Specific recommendations for patient care'
    )
    follow_up_required = models.BooleanField(
        default=False,
        help_text='Does this require follow-up?'
    )
    follow_up_instructions = models.TextField(
        blank=True,
        help_text='Instructions for follow-up'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_final = models.BooleanField(
        default=False,
        help_text='Is this the final note that completes the consult?'
    )
    
    class Meta:
        db_table = 'consult_notes'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['consult', 'created_at']),
            models.Index(fields=['author', '-created_at']),
        ]
    
    def __str__(self):
        return f"Note by {self.author.get_full_name()} on Consult #{self.consult.id}"
    
    def save(self, *args, **kwargs):
        """Overrides the default save method to add custom logic.

        If the note is of a certain type, this method will update the
        associated `ConsultRequest`'s status and other fields accordingly.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().save(*args, **kwargs)
        
        consult = self.consult

        if self.note_type == 'CLOSE_CONSULT' and consult.status != 'CLOSED':
            consult.status = 'CLOSED'
            consult.completed_at = timezone.now()
        elif self.note_type == 'REQUEST_MORE_INFO':
            consult.status = 'MORE_INFO_REQUIRED'
        elif self.note_type == 'ASSIGNED_TO' and self.assigned_to:
            consult.assigned_to = self.assigned_to
            consult.status = 'IN_PROGRESS'

        consult.last_action_summary = f"{self.get_note_type_display()} by {self.author.get_full_name()}"
        consult.save()
