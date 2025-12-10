"""
Department model for Hospital Consult System.
"""

from django.db import models
from django.conf import settings


class Department(models.Model):
    """Represents a medical department or specialty.

    This model stores information about each department, including its name,
    code, head, and service level agreement (SLA) times for consults of
    varying urgency.

    Attributes:
        name: The full name of the department.
        code: A short, unique code for the department.
        parent: A self-referential FK for sub-department hierarchy.
        head: A foreign key to the `User` who is the head of this
              department.
        emergency_sla: The SLA for emergency consults, in minutes.
        urgent_sla: The SLA for urgent consults, in minutes.
        routine_sla: The SLA for routine consults, in minutes.
    """
    
    DEPARTMENT_TYPE_CHOICES = [
        ('CLINICAL', 'Clinical'),
        ('ADMINISTRATIVE', 'Administrative'),
        ('SUPPORT', 'Support'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, help_text='Short code (e.g., CARDIO)')
    department_type = models.CharField(
        max_length=20,
        choices=DEPARTMENT_TYPE_CHOICES,
        default='CLINICAL',
        help_text='Type of department'
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='subdepartments',
        on_delete=models.PROTECT,
        help_text='Parent department for sub-department hierarchy'
    )
    head = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments',
        limit_choices_to={'role': 'HOD'}
    )
    delegated_receiver = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='delegated_departments',
        help_text='Senior doctor delegated to receive and assign consults'
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

    # Delay Policy
    max_response_time = models.IntegerField(
        default=30,
        help_text='Maximum allowed time in minutes to acknowledge a consult'
    )
    delay_action = models.CharField(
        max_length=20,
        choices=[
            ('NOTIFY_HOD', 'Notify HOD'),
            ('ESCALATE', 'Escalate to Senior'),
            ('AUTO_ASSIGN', 'Auto-assign'),
            ('MARK_OVERDUE', 'Mark as Overdue'),
        ],
        default='MARK_OVERDUE',
        help_text='Action to take when a consult is delayed'
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
    
    @property
    def is_subdepartment(self):
        """Returns whether this department is a sub-department.

        Returns:
            True if this department has a parent, False otherwise.
        """
        return self.parent is not None
    
    def get_all_subdepartments(self):
        """Returns all subdepartments (direct children) of this department.

        Returns:
            A QuerySet of Department objects.
        """
        return self.subdepartments.filter(is_active=True)


class OnCall(models.Model):
    """Represents the on-call schedule for a department."""
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.CASCADE,
        related_name='on_call_schedule'
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='on_call_duties'
    )
    date = models.DateField(db_index=True)

    class Meta:
        db_table = 'on_call_schedule'
        unique_together = ('department', 'date')
        ordering = ['date']

    def __str__(self):
        return f"On-call for {self.department.name} on {self.date}: {self.doctor.get_full_name()}"
