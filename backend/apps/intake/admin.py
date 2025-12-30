"""
Admin configuration for Student Intake submissions.
"""

from django.contrib import admin
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from .models import StudentIntakeSubmission


@admin.register(StudentIntakeSubmission)
class StudentIntakeSubmissionAdmin(admin.ModelAdmin):
    """Admin interface for managing student intake submissions."""
    
    list_display = [
        'submission_id',
        'full_name',
        'mdcat_roll_number',
        'merit_number',
        'merit_percentage',
        'mobile_display',
        'email_display',
        'status',
        'created_at',
        'approved_by',
    ]
    
    list_filter = [
        'status',
        'created_at',
        'gender',
        'last_qualification',
    ]
    
    search_fields = [
        'submission_id',
        'full_name',
        'cnic_or_bform',
        'mobile',
        'email',
        'mdcat_roll_number',
    ]
    
    readonly_fields = [
        'submission_id',
        'created_at',
        'updated_at',
        'approved_by',
        'approved_at',
        'created_student',
        'duplicate_check_display',
    ]
    
    fieldsets = (
        ('Submission Information', {
            'fields': ('submission_id', 'status', 'created_at', 'updated_at')
        }),
        ('Personal Information', {
            'fields': (
                'full_name', 'father_name', 'gender', 'date_of_birth',
                'cnic_or_bform', 'mobile', 'email', 'address'
            )
        }),
        ('Guardian Information', {
            'fields': (
                'guardian_name', 'guardian_relation', 'guardian_phone_whatsapp'
            )
        }),
        ('Admission / Merit Details', {
            'fields': (
                'mdcat_roll_number', 'merit_number', 'merit_percentage'
            )
        }),
        ('Academic Background', {
            'fields': (
                'last_qualification', 'institute_name', 'board_or_university',
                'passing_year', 'total_marks_or_grade', 'obtained_marks_or_grade',
                'subjects'
            )
        }),
        ('Documents', {
            'fields': (
                'passport_size_photo', 'cnic_front', 'cnic_back', 'domicile',
                'matric_certificate', 'fsc_certificate', 'migration_certificate',
                'other_document_1', 'other_document_2'
            )
        }),
        ('Review & Approval', {
            'fields': (
                'staff_notes', 'force_approve', 'duplicate_check_display',
                'approved_by', 'approved_at', 'created_student'
            )
        }),
    )
    
    actions = ['approve_and_create_student']
    
    def mobile_display(self, obj):
        """Display mobile number (redacted for privacy)."""
        if obj.mobile:
            # Show only last 4 digits
            return f"***{obj.mobile[-4:]}" if len(obj.mobile) >= 4 else "***"
        return "-"
    mobile_display.short_description = 'Mobile'
    
    def email_display(self, obj):
        """Display email (partially redacted for privacy)."""
        if obj.email:
            parts = obj.email.split('@')
            if len(parts) == 2:
                username = parts[0]
                domain = parts[1]
                # Show first 2 chars and last 2 chars of username
                if len(username) > 4:
                    masked = f"{username[:2]}***{username[-2:]}@{domain}"
                else:
                    masked = f"***@{domain}"
                return masked
        return "-"
    email_display.short_description = 'Email'
    
    def duplicate_check_display(self, obj):
        """Display duplicate check results."""
        if obj.pk:
            duplicates = obj.check_duplicates()
            has_duplicates = any(duplicates.values())
            
            if not has_duplicates:
                return format_html('<span style="color: green;">✓ No duplicates found</span>')
            
            result = []
            if duplicates['cnic']:
                result.append(f"<strong>CNIC:</strong> {', '.join(duplicates['cnic'])}")
            if duplicates['mobile']:
                result.append(f"<strong>Mobile:</strong> {', '.join(duplicates['mobile'])}")
            if duplicates['email']:
                result.append(f"<strong>Email:</strong> {', '.join(duplicates['email'])}")
            if duplicates['mdcat']:
                result.append(f"<strong>MDCAT:</strong> {', '.join(duplicates['mdcat'])}")
            
            return format_html(
                '<span style="color: red;">⚠ Duplicates found:</span><br/>' +
                '<br/>'.join(result)
            )
        return "Save the submission first to check for duplicates."
    duplicate_check_display.short_description = 'Duplicate Check'
    
    def approve_and_create_student(self, request, queryset):
        """Admin action to approve submissions and create Student records.
        
        Allowed roles: ADMIN, COORDINATOR, OFFICE_ASSISTANT
        """
        # Check user permissions
        # Allowed roles: ADMIN, COORDINATOR, OFFICE_ASSISTANT
        user = request.user
        allowed_roles = ['ADMIN', 'COORDINATOR', 'OFFICE_ASSISTANT']
        
        # Check if user has admin role or is superuser
        # Note: If COORDINATOR or OFFICE_ASSISTANT roles don't exist in User model yet,
        # they can be added to User.ROLE_CHOICES and this will automatically work
        if not (user.is_superuser or 
                (hasattr(user, 'role') and user.role in allowed_roles)):
            self.message_user(
                request,
                'You do not have permission to approve submissions. Required roles: ADMIN, COORDINATOR, or OFFICE_ASSISTANT.',
                level=messages.ERROR
            )
            return
        
        approved_count = 0
        blocked_count = 0
        error_count = 0
        
        for submission in queryset:
            if submission.status == 'APPROVED':
                continue
            
            try:
                with transaction.atomic():
                    # Check for duplicates
                    duplicates = submission.check_duplicates()
                    has_duplicates = any(duplicates.values())
                    
                    if has_duplicates and not submission.force_approve:
                        # Block approval, set to NEEDS_REVIEW
                        submission.status = 'NEEDS_REVIEW'
                        duplicate_details = []
                        if duplicates['cnic']:
                            duplicate_details.append(f"CNIC: {', '.join(duplicates['cnic'])}")
                        if duplicates['mobile']:
                            duplicate_details.append(f"Mobile: {', '.join(duplicates['mobile'])}")
                        if duplicates['email']:
                            duplicate_details.append(f"Email: {', '.join(duplicates['email'])}")
                        if duplicates['mdcat']:
                            duplicate_details.append(f"MDCAT: {', '.join(duplicates['mdcat'])}")
                        
                        submission.staff_notes = (
                            f"{submission.staff_notes}\n\n" if submission.staff_notes else ""
                        ) + f"Blocked approval due to duplicates: {'; '.join(duplicate_details)}"
                        submission.save()
                        blocked_count += 1
                        continue
                    
                    # Create Student record
                    try:
                        from apps.students.models import Student
                        
                        student = Student.objects.create(
                            full_name=submission.full_name,
                            father_name=submission.father_name,
                            gender=submission.gender,
                            date_of_birth=submission.date_of_birth,
                            cnic_or_bform=submission.cnic_or_bform,
                            mobile=submission.mobile,
                            email=submission.email,
                            address=submission.address,
                            guardian_name=submission.guardian_name,
                            guardian_relation=submission.guardian_relation,
                            guardian_phone_whatsapp=submission.guardian_phone_whatsapp,
                            mdcat_roll_number=submission.mdcat_roll_number,
                            merit_number=submission.merit_number,
                            merit_percentage=submission.merit_percentage,
                            last_qualification=submission.last_qualification,
                            institute_name=submission.institute_name,
                            board_or_university=submission.board_or_university,
                            passing_year=submission.passing_year,
                            total_marks_or_grade=submission.total_marks_or_grade,
                            obtained_marks_or_grade=submission.obtained_marks_or_grade,
                            subjects=submission.subjects,
                            # Note: Documents are not copied to Student model in this phase
                            # Program/Batch/Group are NOT assigned in this phase
                        )
                        
                        # Link student to submission
                        submission.created_student = student
                        submission.status = 'APPROVED'
                        submission.approved_by = user
                        submission.approved_at = timezone.now()
                        submission.save()
                        
                        approved_count += 1
                        
                    except ImportError:
                        # Student model doesn't exist yet
                        self.message_user(
                            request,
                            f'Student model not found. Cannot create Student record for {submission.submission_id}.',
                            level=messages.WARNING
                        )
                        # Still mark as approved if force_approve is set
                        if submission.force_approve:
                            submission.status = 'APPROVED'
                            submission.approved_by = user
                            submission.approved_at = timezone.now()
                            submission.save()
                            approved_count += 1
                        else:
                            error_count += 1
                    
            except Exception as e:
                error_count += 1
                self.message_user(
                    request,
                    f'Error processing {submission.submission_id}: {str(e)}',
                    level=messages.ERROR
                )
        
        # Summary message
        if approved_count > 0:
            self.message_user(
                request,
                f'Successfully approved {approved_count} submission(s) and created Student record(s).',
                level=messages.SUCCESS
            )
        if blocked_count > 0:
            self.message_user(
                request,
                f'Blocked {blocked_count} submission(s) due to duplicates. Set status to NEEDS_REVIEW.',
                level=messages.WARNING
            )
        if error_count > 0:
            self.message_user(
                request,
                f'Encountered errors processing {error_count} submission(s).',
                level=messages.ERROR
            )
    
    approve_and_create_student.short_description = 'Approve & Create Student'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('approved_by', 'created_student')
