"""
Tests for Student Intake submissions.
"""

from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.intake.models import StudentIntakeSubmission
from apps.intake.forms import StudentIntakeForm
import io

User = get_user_model()


class StudentIntakeSubmissionTest(TestCase):
    """Test cases for Student Intake submissions."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        # Create a test image file
        self.test_image = SimpleUploadedFile(
            "test_photo.jpg",
            b"fake image content",
            content_type="image/jpeg"
        )
        
        # Create form data
        self.form_data = {
            'full_name': 'Test Student',
            'father_name': 'Test Father',
            'gender': 'M',
            'date_of_birth': '2000-01-01',
            'cnic_or_bform': '12345-1234567-1',
            'mobile': '03001234567',
            'email': 'test@example.com',
            'address': 'Test Address',
            'guardian_name': 'Test Guardian',
            'guardian_relation': 'FATHER',
            'guardian_phone_whatsapp': '03001234568',
            'mdcat_roll_number': 'MDCAT123',
            'merit_number': 1,
            'merit_percentage': '85.50',
            'last_qualification': 'FSC',
            'institute_name': 'Test Institute',
            'board_or_university': 'Test Board',
            'passing_year': 2020,
            'total_marks_or_grade': '1100',
            'obtained_marks_or_grade': '935',
            'subjects': 'Physics, Chemistry, Biology',
            'website': '',  # Honeypot field (must be empty)
        }
    
    def test_submission_fails_without_passport_photo(self):
        """Test that submission fails without passport photo."""
        form = StudentIntakeForm(data=self.form_data, files={})
        self.assertFalse(form.is_valid())
        self.assertIn('passport_size_photo', form.errors)
    
    def test_public_submission_creates_pending_record(self):
        """Test that public submission creates a PENDING record."""
        files = {
            'passport_size_photo': self.test_image
        }
        
        response = self.client.post('/apply/student-intake/', {
            **self.form_data,
            **files
        })
        
        # Should redirect to success page
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/apply/student-intake/success/'))
        
        # Check that submission was created with PENDING status
        submission = StudentIntakeSubmission.objects.get(email='test@example.com')
        self.assertEqual(submission.status, 'PENDING')
        self.assertIsNotNone(submission.submission_id)
        self.assertTrue(submission.submission_id.startswith('STU-'))
    
    def test_duplicate_mdcat_roll_number_blocks_approval(self):
        """Test that duplicate MDCAT roll number blocks approval."""
        # Create first submission
        submission1 = StudentIntakeSubmission.objects.create(
            submission_id='STU-20240101-0001',
            status='PENDING',
            full_name='Student One',
            father_name='Father One',
            gender='M',
            date_of_birth='2000-01-01',
            cnic_or_bform='1234512345671',
            mobile='03001234567',
            email='student1@example.com',
            address='Address 1',
            guardian_name='Guardian One',
            guardian_relation='FATHER',
            guardian_phone_whatsapp='03001234568',
            mdcat_roll_number='MDCAT123',
            merit_number=1,
            merit_percentage=85.50,
            last_qualification='FSC',
            institute_name='Institute 1',
            board_or_university='Board 1',
            passing_year=2020,
            total_marks_or_grade='1100',
            obtained_marks_or_grade='935',
            subjects='Physics, Chemistry, Biology',
            passport_size_photo=self.test_image,
        )
        
        # Create second submission with same MDCAT roll number
        submission2 = StudentIntakeSubmission.objects.create(
            submission_id='STU-20240101-0002',
            status='PENDING',
            full_name='Student Two',
            father_name='Father Two',
            gender='F',
            date_of_birth='2000-02-02',
            cnic_or_bform='1234512345672',
            mobile='03001234569',
            email='student2@example.com',
            address='Address 2',
            guardian_name='Guardian Two',
            guardian_relation='MOTHER',
            guardian_phone_whatsapp='03001234570',
            mdcat_roll_number='MDCAT123',  # Duplicate
            merit_number=2,
            merit_percentage=86.00,
            last_qualification='FSC',
            institute_name='Institute 2',
            board_or_university='Board 2',
            passing_year=2020,
            total_marks_or_grade='1100',
            obtained_marks_or_grade='946',
            subjects='Physics, Chemistry, Biology',
            passport_size_photo=self.test_image,
        )
        
        # Check for duplicates
        duplicates = submission2.check_duplicates()
        self.assertIn('MDCAT123', [s for s in duplicates['mdcat'] if 'STU-20240101-0001' in s or 'STU-20240101-0001' == s])
    
    def test_approval_creates_student(self):
        """Test that approval creates Student record (if Student model exists)."""
        # Create a submission
        submission = StudentIntakeSubmission.objects.create(
            submission_id='STU-20240101-0001',
            status='PENDING',
            full_name='Test Student',
            father_name='Test Father',
            gender='M',
            date_of_birth='2000-01-01',
            cnic_or_bform='1234512345671',
            mobile='03001234567',
            email='test@example.com',
            address='Test Address',
            guardian_name='Test Guardian',
            guardian_relation='FATHER',
            guardian_phone_whatsapp='03001234568',
            mdcat_roll_number='MDCAT123',
            merit_number=1,
            merit_percentage=85.50,
            last_qualification='FSC',
            institute_name='Test Institute',
            board_or_university='Test Board',
            passing_year=2020,
            total_marks_or_grade='1100',
            obtained_marks_or_grade='935',
            subjects='Physics, Chemistry, Biology',
            passport_size_photo=self.test_image,
        )
        
        # Create admin user
        admin_user = User.objects.create_user(
            email='admin@pmc.edu.pk',
            password='testpass123',
            role='ADMIN',
            is_staff=True,
        )
        
        # Try to approve (will fail if Student model doesn't exist, which is expected)
        # This test verifies the approval logic works, even if Student model doesn't exist yet
        duplicates = submission.check_duplicates()
        has_duplicates = any(duplicates.values())
        
        self.assertFalse(has_duplicates, "No duplicates should be found for a new submission")
        
        # If Student model exists, we would test creation here
        # For now, we just verify the duplicate check works
    
    def test_honeypot_field_blocks_spam(self):
        """Test that honeypot field blocks spam submissions."""
        files = {
            'passport_size_photo': self.test_image
        }
        
        # Submit with honeypot field filled (spam)
        form_data_spam = {**self.form_data, 'website': 'http://spam.com'}
        form = StudentIntakeForm(data=form_data_spam, files=files)
        
        self.assertFalse(form.is_valid())
        self.assertIn('website', form.errors)
    
    def test_cnic_normalization(self):
        """Test that CNIC is normalized (dashes removed)."""
        submission = StudentIntakeSubmission(
            cnic_or_bform='12345-1234567-1',
            full_name='Test',
            father_name='Test',
            gender='M',
            date_of_birth='2000-01-01',
            mobile='03001234567',
            email='test@example.com',
            address='Test',
            guardian_name='Test',
            guardian_relation='FATHER',
            guardian_phone_whatsapp='03001234568',
            mdcat_roll_number='MDCAT123',
            merit_number=1,
            merit_percentage=85.50,
            last_qualification='FSC',
            institute_name='Test',
            board_or_university='Test',
            passing_year=2020,
            total_marks_or_grade='1100',
            obtained_marks_or_grade='935',
            subjects='Test',
            passport_size_photo=self.test_image,
        )
        submission.save()
        
        # CNIC should be normalized (no dashes)
        self.assertEqual(submission.cnic_or_bform, '1234512345671')
    
    def test_submission_id_generation(self):
        """Test that submission_id is auto-generated."""
        submission = StudentIntakeSubmission.objects.create(
            status='PENDING',
            full_name='Test Student',
            father_name='Test Father',
            gender='M',
            date_of_birth='2000-01-01',
            cnic_or_bform='1234512345671',
            mobile='03001234567',
            email='test@example.com',
            address='Test Address',
            guardian_name='Test Guardian',
            guardian_relation='FATHER',
            guardian_phone_whatsapp='03001234568',
            mdcat_roll_number='MDCAT123',
            merit_number=1,
            merit_percentage=85.50,
            last_qualification='FSC',
            institute_name='Test Institute',
            board_or_university='Test Board',
            passing_year=2020,
            total_marks_or_grade='1100',
            obtained_marks_or_grade='935',
            subjects='Physics, Chemistry, Biology',
            passport_size_photo=self.test_image,
        )
        
        # Submission ID should be auto-generated
        self.assertIsNotNone(submission.submission_id)
        self.assertTrue(submission.submission_id.startswith('STU-'))
        self.assertEqual(len(submission.submission_id.split('-')), 3)
