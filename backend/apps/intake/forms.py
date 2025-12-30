"""
Forms for Student Intake submissions.
"""

import re
from django import forms
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from django.conf import settings
from .models import StudentIntakeSubmission, normalize_cnic


class StudentIntakeForm(forms.ModelForm):
    """Public form for student intake submissions."""
    
    # Honeypot field (hidden, must be empty)
    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label=''
    )
    
    class Meta:
        model = StudentIntakeSubmission
        fields = [
            # Personal Information
            'full_name', 'father_name', 'gender', 'date_of_birth',
            'cnic_or_bform', 'mobile', 'email', 'address',
            # Guardian Information
            'guardian_name', 'guardian_relation', 'guardian_phone_whatsapp',
            # Admission / Merit Details
            'mdcat_roll_number', 'merit_number', 'merit_percentage',
            # Academic Background
            'last_qualification', 'institute_name', 'board_or_university',
            'passing_year', 'total_marks_or_grade', 'obtained_marks_or_grade',
            'subjects',
            # Documents
            'passport_size_photo', 'cnic_front', 'cnic_back', 'domicile',
            'matric_certificate', 'fsc_certificate', 'migration_certificate',
            'other_document_1', 'other_document_2',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
            }),
            'father_name': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
            }),
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': True,
            }),
            'cnic_or_bform': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12345-1234567-1',
                'required': True,
            }),
            'mobile': forms.TextInput(attrs={
                'type': 'tel',
                'class': 'form-control',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'type': 'email',
                'class': 'form-control',
                'required': True,
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'required': True,
            }),
            'guardian_name': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
            }),
            'guardian_relation': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
            }),
            'guardian_phone_whatsapp': forms.TextInput(attrs={
                'type': 'tel',
                'class': 'form-control',
                'required': True,
            }),
            'mdcat_roll_number': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
            }),
            'merit_number': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'required': True,
            }),
            'merit_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0,
                'max': 100,
                'required': True,
            }),
            'last_qualification': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
            }),
            'institute_name': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
            }),
            'board_or_university': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
            }),
            'passing_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1900,
                'max': 2100,
                'required': True,
            }),
            'total_marks_or_grade': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
            }),
            'obtained_marks_or_grade': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
            }),
            'subjects': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
            }),
            'passport_size_photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/jpg,image/png',
                'required': True,
            }),
            'cnic_front': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
            }),
            'cnic_back': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
            }),
            'domicile': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
            }),
            'matric_certificate': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
            }),
            'fsc_certificate': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
            }),
            'migration_certificate': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
            }),
            'other_document_1': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
            }),
            'other_document_2': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields required except optional documents
        for field_name, field in self.fields.items():
            if field_name not in ['website', 'cnic_front', 'cnic_back', 'domicile',
                                 'matric_certificate', 'fsc_certificate',
                                 'migration_certificate', 'other_document_1',
                                 'other_document_2']:
                field.required = True
    
    def clean_website(self):
        """Honeypot field - must be empty."""
        website = self.cleaned_data.get('website')
        if website:
            raise ValidationError('Spam detected.')
        return website
    
    def clean_cnic_or_bform(self):
        """Normalize and validate CNIC/B-Form."""
        cnic = self.cleaned_data.get('cnic_or_bform')
        if cnic:
            cnic = normalize_cnic(cnic)
            if not (11 <= len(cnic) <= 13):
                raise ValidationError('CNIC/B-Form must be 11-13 digits.')
        return cnic
    
    def clean_mobile(self):
        """Validate mobile number."""
        mobile = self.cleaned_data.get('mobile')
        if mobile:
            mobile_digits = re.sub(r'[^\d]', '', mobile)
            if len(mobile_digits) < 10 or len(mobile_digits) > 15:
                raise ValidationError('Mobile number must be 10-15 digits.')
        return mobile
    
    def clean_guardian_phone_whatsapp(self):
        """Validate guardian WhatsApp number."""
        phone = self.cleaned_data.get('guardian_phone_whatsapp')
        if phone:
            phone_digits = re.sub(r'[^\d]', '', phone)
            if len(phone_digits) < 10 or len(phone_digits) > 15:
                raise ValidationError('Guardian WhatsApp number must be 10-15 digits.')
        return phone
    
    def clean_passport_size_photo(self):
        """Validate passport-size photo."""
        photo = self.cleaned_data.get('passport_size_photo')
        if not photo:
            raise ValidationError('Passport-size photograph is required.')
        
        # Check file size (1MB max)
        if photo.size > 1024 * 1024:  # 1MB
            raise ValidationError('Passport photo must be less than 1MB.')
        
        # Check file extension (jpg/png only)
        ext = photo.name.split('.')[-1].lower()
        if ext not in ['jpg', 'jpeg', 'png']:
            raise ValidationError('Passport photo must be JPG or PNG format.')
        
        # Validate it's actually an image (not a PDF)
        try:
            width, height = get_image_dimensions(photo)
            if width is None or height is None:
                raise ValidationError('Invalid image file.')
            
            # Optional soft check: square-ish aspect ratio (do not hard fail)
            # We'll just log a warning if needed, but allow it
            aspect_ratio = width / height if height > 0 else 0
            # Typical passport photos are roughly 1:1.2 to 1:1.5
            # We'll allow a wide range (0.5 to 2.0) for MVP
            if not (0.5 <= aspect_ratio <= 2.0):
                # Don't fail, just note it
                pass
        except Exception:
            raise ValidationError('Invalid image file. Please upload a valid JPG or PNG image.')
        
        return photo
    
    def clean_cnic_front(self):
        """Validate CNIC front document."""
        return self._validate_optional_file(self.cleaned_data.get('cnic_front'), 'CNIC front')
    
    def clean_cnic_back(self):
        """Validate CNIC back document."""
        return self._validate_optional_file(self.cleaned_data.get('cnic_back'), 'CNIC back')
    
    def clean_domicile(self):
        """Validate domicile document."""
        return self._validate_optional_file(self.cleaned_data.get('domicile'), 'Domicile')
    
    def clean_matric_certificate(self):
        """Validate matric certificate."""
        return self._validate_optional_file(self.cleaned_data.get('matric_certificate'), 'Matric certificate')
    
    def clean_fsc_certificate(self):
        """Validate FSc certificate."""
        return self._validate_optional_file(self.cleaned_data.get('fsc_certificate'), 'FSc certificate')
    
    def clean_migration_certificate(self):
        """Validate migration certificate."""
        return self._validate_optional_file(self.cleaned_data.get('migration_certificate'), 'Migration certificate')
    
    def clean_other_document_1(self):
        """Validate other document 1."""
        return self._validate_optional_file(self.cleaned_data.get('other_document_1'), 'Other document 1')
    
    def clean_other_document_2(self):
        """Validate other document 2."""
        return self._validate_optional_file(self.cleaned_data.get('other_document_2'), 'Other document 2')
    
    def _validate_optional_file(self, file, field_name):
        """Validate optional file uploads (max 3MB, allowed extensions)."""
        if not file:
            return file
        
        # Check file size (3MB max)
        if file.size > 3 * 1024 * 1024:  # 3MB
            raise ValidationError(f'{field_name} must be less than 3MB.')
        
        # Check file extension
        ext = file.name.split('.')[-1].lower()
        if ext not in ['pdf', 'jpg', 'jpeg', 'png']:
            raise ValidationError(f'{field_name} must be PDF, JPG, or PNG format.')
        
        return file
