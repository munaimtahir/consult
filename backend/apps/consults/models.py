"""
Consult models for Hospital Consult System.
"""

from django.db import models
from django.utils import timezone
from datetime import timedelta


class ConsultRequest(models.Model):
    """
    Main consult request model.
    Tracks the lifecycle of a consultation request from creation to completion.
    """
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACKNOWLEDGED', 'Acknowledged'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
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
        default='PENDING'
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
        """
        Override save to calculate expected response time based on urgency and department SLA.
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
        """Get time elapsed since creation"""
        if self.completed_at:
            return self.completed_at - self.created_at
        return timezone.now() - self.created_at
    
    @property
    def time_to_acknowledgement(self):
        """Get time taken to acknowledge"""
        if self.acknowledged_at:
            return self.acknowledged_at - self.created_at
        return None
    
    @property
    def time_to_completion(self):
        """Get time taken to complete"""
        if self.completed_at:
            return self.completed_at - self.created_at
        return None
    
    @property
    def is_pending_assignment(self):
        """Check if consult is pending assignment"""
        return self.status in ['PENDING', 'ACKNOWLEDGED'] and not self.assigned_to
    
    @property
    def sla_compliance(self):
        """Check if consult was completed within SLA"""
        if self.completed_at:
            return self.completed_at <= self.expected_response_time
        return not self.is_overdue


class ConsultNote(models.Model):
    """
    Notes added to a consult request.
    Can be progress notes, recommendations, or final assessments.
    """
    
    NOTE_TYPE_CHOICES = [
        ('PROGRESS', 'Progress Note'),
        ('RECOMMENDATION', 'Recommendation'),
        ('ASSESSMENT', 'Assessment'),
        ('PLAN', 'Plan'),
        ('FINAL', 'Final Note'),
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
        default='PROGRESS'
    )
    content = models.TextField()
    
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
        """
        Override save to update consult status when final note is added.
        """
        super().save(*args, **kwargs)
        
        # If this is a final note, mark the consult as completed
        if self.is_final and self.consult.status != 'COMPLETED':
            self.consult.status = 'COMPLETED'
            self.consult.completed_at = timezone.now()
            self.consult.save()
