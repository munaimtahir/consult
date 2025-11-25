"""
Department model for Hospital Consult System.
"""

from django.db import models


class Department(models.Model):
    """
    Medical department/specialty (e.g., Cardiology, Neurology).
    """
    
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, help_text='Short code (e.g., CARDIO)')
    head = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments',
        limit_choices_to={'role': 'HOD'}
    )
    contact_number = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    
    # SLA Configuration (in minutes)
    emergency_sla = models.IntegerField(
        default=60,
        help_text='SLA for emergency consults (minutes)'
    )
    urgent_sla = models.IntegerField(
        default=240,
        help_text='SLA for urgent consults (minutes)'
    )
    routine_sla = models.IntegerField(
        default=1380,
        help_text='SLA for routine consults (minutes)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'departments'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def user_count(self):
        """Get number of users in this department"""
        return self.users.count()
    
    @property
    def active_consults_count(self):
        """Get number of active consults for this department"""
        return self.incoming_consults.exclude(status='COMPLETED').count()
