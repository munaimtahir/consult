"""
Department model for Hospital Consult System.
"""

from django.db import models


class Department(models.Model):
    """Represents a medical department or specialty.

    This model stores information about each department, including its name,
    code, head, and service level agreement (SLA) times for consults of
    varying urgency.

    Attributes:
        name: The full name of the department.
        code: A short, unique code for the department.
        head: A foreign key to the `User` who is the head of this
              department.
        emergency_sla: The SLA for emergency consults, in minutes.
        urgent_sla: The SLA for urgent consults, in minutes.
        routine_sla: The SLA for routine consults, in minutes.
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
        """Returns the number of users in this department.

        Returns:
            An integer representing the total number of users.
        """
        return self.users.count()
    
    @property
    def active_consults_count(self):
        """Returns the number of active consults for this department.

        Returns:
            An integer representing the number of non-completed consults.
        """
        return self.incoming_consults.exclude(status='COMPLETED').count()
