"""
Tests for the reassign endpoint.
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.accounts.models import User
from apps.departments.models import Department
from apps.patients.models import Patient
from apps.consults.models import ConsultRequest


class ReassignTests(TestCase):
    """Test suite for the reassign endpoint."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create Departments
        self.dept_er = Department.objects.create(
            name="Emergency",
            code="ER",
            emergency_sla=60,
            urgent_sla=240,
            routine_sla=1380
        )
        self.dept_cardio = Department.objects.create(
            name="Cardiology",
            code="CARDIO",
            emergency_sla=60,
            urgent_sla=240,
            routine_sla=1380
        )
        
        # Create Users
        self.doctor_er = User.objects.create_user(
            email="er_doc@pmc.edu.pk",
            password="password123",
            first_name="ER",
            last_name="Doc",
            department=self.dept_er,
            role='DOCTOR'
        )
        
        self.hod_cardio = User.objects.create_user(
            email="hod_cardio@pmc.edu.pk",
            password="password123",
            first_name="Cardio",
            last_name="HOD",
            department=self.dept_cardio,
            role='HOD',
            designation='HOD'
        )
        
        self.doctor_cardio1 = User.objects.create_user(
            email="cardio_doc1@pmc.edu.pk",
            password="password123",
            first_name="Cardio",
            last_name="Doc1",
            department=self.dept_cardio,
            role='DOCTOR',
            designation='RESIDENT_3'
        )
        
        self.doctor_cardio2 = User.objects.create_user(
            email="cardio_doc2@pmc.edu.pk",
            password="password123",
            first_name="Cardio",
            last_name="Doc2",
            department=self.dept_cardio,
            role='DOCTOR',
            designation='RESIDENT_4'
        )
        
        # Create Patient
        self.patient = Patient.objects.create(
            name="John Doe",
            mrn="MRN12345",
            age=44,
            gender="M",
            ward="General Ward",
            bed_number="A1",
            primary_department=self.dept_er,
            primary_diagnosis="Chest pain"
        )

    def test_hod_can_reassign_consult(self):
        """Test that HOD can reassign a consult to a different doctor."""
        # Create and assign a consult
        consult = ConsultRequest.objects.create(
            patient=self.patient,
            requester=self.doctor_er,
            requesting_department=self.dept_er,
            target_department=self.dept_cardio,
            urgency='URGENT',
            reason_for_consult='Chest pain evaluation',
            status='IN_PROGRESS',
            assigned_to=self.doctor_cardio1
        )
        
        # Login as HOD
        self.client.force_authenticate(user=self.hod_cardio)
        
        # Reassign to another doctor
        response = self.client.post(
            f'/api/v1/consults/requests/{consult.id}/reassign/',
            {'assigned_to_user_id': self.doctor_cardio2.id}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh consult from DB
        consult.refresh_from_db()
        
        # Verify reassignment
        self.assertEqual(consult.assigned_to, self.doctor_cardio2)
        self.assertEqual(consult.assigned_by, self.hod_cardio)
        self.assertIsNotNone(consult.assigned_at)
        self.assertEqual(consult.assignment_type, 'manual')

    def test_hod_can_reassign_to_themselves(self):
        """Test that HOD can reassign a consult to themselves."""
        # Create and assign a consult
        consult = ConsultRequest.objects.create(
            patient=self.patient,
            requester=self.doctor_er,
            requesting_department=self.dept_er,
            target_department=self.dept_cardio,
            urgency='URGENT',
            reason_for_consult='Chest pain evaluation',
            status='IN_PROGRESS',
            assigned_to=self.doctor_cardio1
        )
        
        # Login as HOD
        self.client.force_authenticate(user=self.hod_cardio)
        
        # Reassign to themselves
        response = self.client.post(
            f'/api/v1/consults/requests/{consult.id}/reassign/',
            {'assigned_to_user_id': self.hod_cardio.id}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh consult from DB
        consult.refresh_from_db()
        
        # Verify reassignment to self
        self.assertEqual(consult.assigned_to, self.hod_cardio)
        self.assertEqual(consult.assigned_by, self.hod_cardio)

    def test_regular_doctor_cannot_reassign(self):
        """Test that regular doctor cannot reassign a consult."""
        # Create and assign a consult
        consult = ConsultRequest.objects.create(
            patient=self.patient,
            requester=self.doctor_er,
            requesting_department=self.dept_er,
            target_department=self.dept_cardio,
            urgency='URGENT',
            reason_for_consult='Chest pain evaluation',
            status='IN_PROGRESS',
            assigned_to=self.doctor_cardio1
        )
        
        # Login as regular doctor
        self.client.force_authenticate(user=self.doctor_cardio1)
        
        # Try to reassign
        response = self.client.post(
            f'/api/v1/consults/requests/{consult.id}/reassign/',
            {'assigned_to_user_id': self.doctor_cardio2.id}
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Verify consult unchanged
        consult.refresh_from_db()
        self.assertEqual(consult.assigned_to, self.doctor_cardio1)

    def test_cannot_reassign_unassigned_consult(self):
        """Test that unassigned consults cannot be reassigned."""
        # Create unassigned consult
        consult = ConsultRequest.objects.create(
            patient=self.patient,
            requester=self.doctor_er,
            requesting_department=self.dept_er,
            target_department=self.dept_cardio,
            urgency='URGENT',
            reason_for_consult='Chest pain evaluation',
            status='SUBMITTED'
        )
        
        # Login as HOD
        self.client.force_authenticate(user=self.hod_cardio)
        
        # Try to reassign unassigned consult
        response = self.client.post(
            f'/api/v1/consults/requests/{consult.id}/reassign/',
            {'assigned_to_user_id': self.doctor_cardio1.id}
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('not yet assigned', response.data['error'].lower())

    def test_reassigned_user_must_be_in_target_department(self):
        """Test that reassigned user must belong to target department."""
        # Create and assign a consult
        consult = ConsultRequest.objects.create(
            patient=self.patient,
            requester=self.doctor_er,
            requesting_department=self.dept_er,
            target_department=self.dept_cardio,
            urgency='URGENT',
            reason_for_consult='Chest pain evaluation',
            status='IN_PROGRESS',
            assigned_to=self.doctor_cardio1
        )
        
        # Login as HOD
        self.client.force_authenticate(user=self.hod_cardio)
        
        # Try to reassign to doctor from different department
        response = self.client.post(
            f'/api/v1/consults/requests/{consult.id}/reassign/',
            {'assigned_to_user_id': self.doctor_er.id}
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('target department', response.data['error'].lower())
