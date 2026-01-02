"""
Student model for SIMS.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

User = get_user_model()


class Student(models.Model):
    """Represents a student in the system."""
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    # Basic Information
    student_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text='Unique student identifier (e.g., STU-2024-001)'
    )
    full_name = models.CharField(max_length=200)
    father_name = models.CharField(max_length=200)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    
    # Identification
    cnic_or_bform = models.CharField(
        max_length=20,
        db_index=True,
        validators=[RegexValidator(regex=r'^\d{11,13}$', message='CNIC/B-Form must be 11-13 digits')],
        help_text='CNIC or B-Form number (normalized, no dashes)'
    )
    mobile = models.CharField(
        max_length=20,
        db_index=True,
        help_text='Mobile phone number'
    )
    email = models.EmailField(
        db_index=True,
        help_text='Email address'
    )
    address = models.TextField()
    
    # Academic Information
    program = models.ForeignKey(
        'academics.Program',
        on_delete=models.PROTECT,
        related_name='students',
        null=True,
        blank=True,
        help_text='Enrolled program'
    )
    admission_date = models.DateField(null=True, blank=True)
    mdcat_roll_number = models.CharField(max_length=50, blank=True, db_index=True)
    merit_number = models.IntegerField(null=True, blank=True)
    merit_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Link to intake submission if created from intake
    intake_submission = models.ForeignKey(
        'intake.StudentIntakeSubmission',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_students',
        help_text='Intake submission that created this student'
    )
    
    class Meta:
        db_table = 'students'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student_id']),
            models.Index(fields=['cnic_or_bform']),
            models.Index(fields=['mobile']),
            models.Index(fields=['email']),
            models.Index(fields=['mdcat_roll_number']),
            models.Index(fields=['is_active']),
        ]
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
    
    def __str__(self):
        return f"{self.student_id} - {self.full_name}"
    
    @property
    def user(self):
        """Get associated user account if exists."""
        # This assumes a one-to-one relationship might be added later
        # For now, we can search by email
        try:
            return User.objects.get(email=self.email)
        except User.DoesNotExist:
            return None
