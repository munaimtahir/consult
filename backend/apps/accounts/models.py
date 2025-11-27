"""
Custom User model for Hospital Consult System.
Extends Django's AbstractUser with PMC-specific fields.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


class User(AbstractUser):
    """Represents a user in the Hospital Consult System.

    This model extends Django's built-in `AbstractUser` to include fields
    and logic specific to the hospital's operational hierarchy, such as roles,
    designations, and departments. It uses the email address as the primary
    means of identification.

    Attributes:
        role: The user's primary role (e.g., 'DOCTOR', 'HOD').
        designation: The user's medical or administrative title.
        department: A foreign key to the user's assigned department.
        seniority_level: An integer calculated from designation, used for
                         escalation.
        phone_number: The user's contact phone number.
        profile_photo: A URL to the user's profile photo, typically from
                       Google.
        is_on_call: A boolean indicating if the user is currently on call.
    """
    
    ROLE_CHOICES = [
        ('DOCTOR', 'Doctor'),
        ('DEPARTMENT_USER', 'Department User'),
        ('HOD', 'Head of Department'),
        ('ADMIN', 'Administrator'),
    ]
    
    DESIGNATION_CHOICES = [
        ('RESIDENT_1', 'Resident 1'),
        ('RESIDENT_2', 'Resident 2'),
        ('RESIDENT_3', 'Resident 3'),
        ('RESIDENT_4', 'Resident 4'),
        ('RESIDENT_5', 'Resident 5'),
        ('SENIOR_REGISTRAR', 'Senior Registrar'),
        ('ASSISTANT_PROFESSOR', 'Assistant Professor'),
        ('PROFESSOR', 'Professor'),
        ('HOD', 'Head of Department'),
    ]
    
    # Override email to make it unique and required
    email = models.EmailField(unique=True)
    
    # Hospital-specific fields
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='DOCTOR')
    designation = models.CharField(
        max_length=50,
        choices=DESIGNATION_CHOICES,
        blank=True,
        help_text='Medical designation/rank'
    )
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    seniority_level = models.IntegerField(
        default=1,
        help_text='Auto-calculated from designation for escalation hierarchy'
    )
    phone_number = models.CharField(max_length=20, blank=True)
    profile_photo = models.URLField(blank=True, help_text='Photo from Google OAuth')
    is_on_call = models.BooleanField(default=False)
    
    # Use email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        ordering = ['department', '-seniority_level']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['department', 'role']),
            models.Index(fields=['designation', 'seniority_level']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def save(self, *args, **kwargs):
        """Overrides the default save method to add custom logic.

        This method performs several actions before saving the user:
        1. Calculates and sets the `seniority_level` based on the `designation`.
        2. Automatically sets the user's `role` based on their `designation`.
        3. Validates that the user's email address ends with '@pmc.edu.pk'.
        4. Sets the `username` to the part of the email before the '@' if it's not
           already set.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Raises:
            ValidationError: If the email address does not have the
                             '@pmc.edu.pk' domain.
        """
        # Map designation to seniority level
        designation_seniority_map = {
            'RESIDENT_1': 1,
            'RESIDENT_2': 2,
            'RESIDENT_3': 3,
            'RESIDENT_4': 4,
            'RESIDENT_5': 5,
            'SENIOR_REGISTRAR': 6,
            'ASSISTANT_PROFESSOR': 7,
            'PROFESSOR': 8,
            'HOD': 9,
        }
        
        if self.designation:
            self.seniority_level = designation_seniority_map.get(self.designation, 1)
            
            # Auto-set role based on designation
            if self.designation == 'HOD':
                self.role = 'HOD'
            elif self.designation in ['ASSISTANT_PROFESSOR', 'PROFESSOR']:
                self.role = 'DEPARTMENT_USER'
            else:
                self.role = 'DOCTOR'
        
        # Validate email domain
        if self.email and not self.email.endswith('@pmc.edu.pk'):
            raise ValidationError('Only @pmc.edu.pk email addresses are allowed.')
        
        # Set username from email if not provided
        if not self.username:
            self.username = self.email.split('@')[0]
        
        super().save(*args, **kwargs)
    
    @property
    def designation_display(self):
        """Returns the human-readable version of the designation.

        Returns:
            A string representing the full designation name (e.g.,
            'Senior Registrar').
        """
        return dict(self.DESIGNATION_CHOICES).get(self.designation, '')
    
    @property
    def is_hod(self):
        """Checks if the user is a Head of Department.

        Returns:
            True if the user's role is 'HOD', False otherwise.
        """
        return self.role == 'HOD'
    
    @property
    def is_admin_user(self):
        """Checks if the user has administrative privileges.

        Returns:
            True if the user's role is 'ADMIN' or if they are a superuser,
            False otherwise.
        """
        return self.role == 'ADMIN' or self.is_superuser
    
    @property
    def can_assign_consults(self):
        """Checks if the user has permission to assign consults.

        Returns:
            True if the user's role is 'HOD', 'DEPARTMENT_USER', or 'ADMIN',
            False otherwise.
        """
        return self.role in ['HOD', 'DEPARTMENT_USER', 'ADMIN']
