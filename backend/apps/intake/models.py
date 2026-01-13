"""
Student Intake Submission model for collecting student application data.
"""

import re
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


def normalize_cnic(value):
    """Normalize CNIC/B-Form by removing dashes and spaces."""
    if not value:
        return value
    return re.sub(r'[-\s]', '', str(value))


def intake_upload_path(instance, filename):
    """Generate upload path for intake documents."""
    # Use submission_id if available, otherwise use pk or 'temp'
    identifier = instance.submission_id if hasattr(instance, 'submission_id') and instance.submission_id else (
        f'temp-{instance.pk}' if instance.pk else 'temp'
    )
    return f'intake/{identifier}/{filename}'


class StudentIntakeSubmission(models.Model):
    """Represents a student intake form submission awaiting verification."""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('NEEDS_REVIEW', 'Needs Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    QUALIFICATION_CHOICES = [
        ('MATRIC', 'Matric'),
        ('FSC', 'FSc'),
        ('A_LEVELS', 'A-Levels'),
        ('OTHER', 'Other'),
    ]
    
    GUARDIAN_RELATION_CHOICES = [
        ('FATHER', 'Father'),
        ('MOTHER', 'Mother'),
        ('GUARDIAN', 'Guardian'),
        ('OTHER', 'Other'),
    ]
    
    # System / Meta fields
    submission_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text='Unique submission reference (STU-YYYYMMDD-XXXX)'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        db_index=True,
        help_text='Current verification status'
    )
    staff_notes = models.TextField(
        blank=True,
        help_text='Internal notes for staff review'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_intake_submissions',
        help_text='Staff member who approved this submission'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    # TODO: Re-enable when students app is created
    # created_student = models.ForeignKey(
    #     'students.Student',
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name='intake_submission',
    #     help_text='Student record created from this submission (if approved)'
    # )
    force_approve = models.BooleanField(
        default=False,
        help_text='Admin-only override to bypass duplicate checks'
    )
    
    # A) Personal Information (ALL REQUIRED)
    full_name = models.CharField(max_length=200)
    father_name = models.CharField(max_length=200)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    cnic_or_bform = models.CharField(
        max_length=20,
        db_index=True,
        help_text='CNIC or B-Form number (normalized)'
    )
    mobile = models.CharField(
        max_length=20,
        db_index=True,
        help_text='Mobile phone number (required)'
    )
    email = models.EmailField(
        db_index=True,
        help_text='Email address (required)'
    )
    address = models.TextField()
    
    # B) Guardian Information (ALL REQUIRED)
    guardian_name = models.CharField(max_length=200)
    guardian_relation = models.CharField(
        max_length=20,
        choices=GUARDIAN_RELATION_CHOICES
    )
    guardian_phone_whatsapp = models.CharField(
        max_length=20,
        help_text='Guardian WhatsApp number (required)'
    )
    
    # C) Admission / Merit Details (ALL REQUIRED)
    mdcat_roll_number = models.CharField(
        max_length=50,
        db_index=True,
        help_text='MDCAT Roll Number (required, checked for duplicates)'
    )
    merit_number = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text='Merit number (must be > 0)'
    )
    merit_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0.00), MaxValueValidator(100.00)],
        help_text='Merit percentage (0.00-100.00)'
    )
    
    # D) Academic Background (ALL REQUIRED)
    last_qualification = models.CharField(
        max_length=20,
        choices=QUALIFICATION_CHOICES
    )
    institute_name = models.CharField(max_length=200)
    board_or_university = models.CharField(max_length=200)
    passing_year = models.IntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(2100)]
    )
    total_marks_or_grade = models.CharField(max_length=50)
    obtained_marks_or_grade = models.CharField(max_length=50)
    subjects = models.CharField(
        max_length=500,
        help_text='Subjects studied (short text)'
    )
    
    # E) Documents
    # MANDATORY
    passport_size_photo = models.ImageField(
        upload_to=intake_upload_path,
        help_text='Passport-size photograph (jpg/png only, max 1MB, REQUIRED)'
    )
    
    # OPTIONAL
    cnic_front = models.FileField(
        upload_to=intake_upload_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])],
        help_text='CNIC front (pdf/jpg/png, max 3MB)'
    )
    cnic_back = models.FileField(
        upload_to=intake_upload_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])],
        help_text='CNIC back (pdf/jpg/png, max 3MB)'
    )
    domicile = models.FileField(
        upload_to=intake_upload_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])],
        help_text='Domicile certificate (pdf/jpg/png, max 3MB)'
    )
    matric_certificate = models.FileField(
        upload_to=intake_upload_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])],
        help_text='Matric certificate (pdf/jpg/png, max 3MB)'
    )
    fsc_certificate = models.FileField(
        upload_to=intake_upload_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])],
        help_text='FSc certificate (pdf/jpg/png, max 3MB)'
    )
    migration_certificate = models.FileField(
        upload_to=intake_upload_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])],
        help_text='Migration certificate (pdf/jpg/png, max 3MB)'
    )
    other_document_1 = models.FileField(
        upload_to=intake_upload_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])],
        help_text='Other document 1 (pdf/jpg/png, max 3MB)'
    )
    other_document_2 = models.FileField(
        upload_to=intake_upload_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])],
        help_text='Other document 2 (pdf/jpg/png, max 3MB)'
    )
    
    class Meta:
        db_table = 'student_intake_submissions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['cnic_or_bform']),
            models.Index(fields=['mobile']),
            models.Index(fields=['email']),
            models.Index(fields=['mdcat_roll_number']),
            models.Index(fields=['status']),
            models.Index(fields=['submission_id']),
        ]
        verbose_name = 'Student Intake Submission'
        verbose_name_plural = 'Student Intake Submissions'
    
    def __str__(self):
        return f"{self.submission_id} - {self.full_name}"
    
    def clean(self):
        """Validate the model instance."""
        super().clean()
        
        # Normalize CNIC/B-Form
        if self.cnic_or_bform:
            self.cnic_or_bform = normalize_cnic(self.cnic_or_bform)
            # Validate length (11-13 digits)
            if not (11 <= len(self.cnic_or_bform) <= 13):
                raise ValidationError({
                    'cnic_or_bform': 'CNIC/B-Form must be 11-13 digits.'
                })
        
        # Validate mobile number (basic)
        if self.mobile:
            mobile_digits = re.sub(r'[^\d]', '', self.mobile)
            if len(mobile_digits) < 10 or len(mobile_digits) > 15:
                raise ValidationError({
                    'mobile': 'Mobile number must be 10-15 digits.'
                })
        
        # Validate guardian WhatsApp
        if self.guardian_phone_whatsapp:
            guardian_digits = re.sub(r'[^\d]', '', self.guardian_phone_whatsapp)
            if len(guardian_digits) < 10 or len(guardian_digits) > 15:
                raise ValidationError({
                    'guardian_phone_whatsapp': 'Guardian WhatsApp number must be 10-15 digits.'
                })
    
    def save(self, *args, **kwargs):
        """Override save to generate submission_id if not set."""
        if not self.submission_id:
            # Generate submission_id: STU-YYYYMMDD-XXXX
            today = timezone.now().date()
            date_str = today.strftime('%Y%m%d')
            
            # Get the last submission number for today
            last_submission = StudentIntakeSubmission.objects.filter(
                submission_id__startswith=f'STU-{date_str}-'
            ).order_by('-submission_id').first()
            
            if last_submission:
                # Extract and increment the number
                try:
                    last_num = int(last_submission.submission_id.split('-')[-1])
                    next_num = last_num + 1
                except (ValueError, IndexError):
                    next_num = 1
            else:
                next_num = 1
            
            self.submission_id = f'STU-{date_str}-{next_num:04d}'
        
        # Normalize CNIC before saving
        if self.cnic_or_bform:
            self.cnic_or_bform = normalize_cnic(self.cnic_or_bform)
        
        self.full_clean()
        super().save(*args, **kwargs)
    
    def check_duplicates(self):
        """Check for duplicate submissions based on CNIC, Mobile, Email, MDCAT Roll No.
        
        Returns:
            dict: Dictionary with keys 'cnic', 'mobile', 'email', 'mdcat' containing
                  lists of duplicate submission IDs if found, empty lists otherwise.
        """
        duplicates = {
            'cnic': [],
            'mobile': [],
            'email': [],
            'mdcat': [],
        }
        
        if not self.cnic_or_bform:
            return duplicates
        
        # Check CNIC/B-Form
        cnic_normalized = normalize_cnic(self.cnic_or_bform)
        cnic_duplicates = StudentIntakeSubmission.objects.filter(
            cnic_or_bform=cnic_normalized
        ).exclude(pk=self.pk if self.pk else None)
        duplicates['cnic'] = [s.submission_id for s in cnic_duplicates]
        
        # Check Mobile
        if self.mobile:
            mobile_duplicates = StudentIntakeSubmission.objects.filter(
                mobile=self.mobile
            ).exclude(pk=self.pk if self.pk else None)
            duplicates['mobile'] = [s.submission_id for s in mobile_duplicates]
        
        # Check Email
        if self.email:
            email_duplicates = StudentIntakeSubmission.objects.filter(
                email=self.email
            ).exclude(pk=self.pk if self.pk else None)
            duplicates['email'] = [s.submission_id for s in email_duplicates]
        
        # Check MDCAT Roll Number
        if self.mdcat_roll_number:
            mdcat_duplicates = StudentIntakeSubmission.objects.filter(
                mdcat_roll_number=self.mdcat_roll_number
            ).exclude(pk=self.pk if self.pk else None)
            duplicates['mdcat'] = [s.submission_id for s in mdcat_duplicates]
        
        # Also check against Student model if it exists
        try:
            from apps.students.models import Student
            
            # Check CNIC in Student model
            student_cnic = Student.objects.filter(cnic_or_bform=cnic_normalized).first()
            if student_cnic:
                duplicates['cnic'].append(f'STUDENT-{student_cnic.id}')
            
            # Check Mobile in Student model
            if self.mobile:
                student_mobile = Student.objects.filter(mobile=self.mobile).first()
                if student_mobile:
                    duplicates['mobile'].append(f'STUDENT-{student_mobile.id}')
            
            # Check Email in Student model
            if self.email:
                student_email = Student.objects.filter(email=self.email).first()
                if student_email:
                    duplicates['email'].append(f'STUDENT-{student_email.id}')
            
            # Check MDCAT Roll Number in Student model
            if self.mdcat_roll_number:
                student_mdcat = Student.objects.filter(mdcat_roll_number=self.mdcat_roll_number).first()
                if student_mdcat:
                    duplicates['mdcat'].append(f'STUDENT-{student_mdcat.id}')
        except ImportError:
            # Student model doesn't exist yet, skip
            pass
        
        return duplicates
