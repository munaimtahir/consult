"""
Tests for the acknowledge_assign endpoint.
"""

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from apps.accounts.models import User
from apps.departments.models import Department
from apps.patients.models import Patient
from apps.consults.models import ConsultRequest


class AcknowledgeAssignTests(TestCase):
    """Test suite for the acknowledge_assign combined action."""

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
        
        self.doctor_cardio = User.objects.create_user(
            email="cardio_doc@pmc.edu.pk",
            password="password123",
            first_name="Cardio",
            last_name="Doc",
            department=self.dept_cardio,
            role='DOCTOR',
            designation='RESIDENT_3'
        )
        
        self.senior_cardio = User.objects.create_user(
            email="senior_cardio@pmc.edu.pk",
            password="password123",
            first_name="Senior",
            last_name="Cardio",
            department=self.dept_cardio,
            role='DEPARTMENT_USER',
            designation='PROFESSOR',
            can_manage_consults_in_department=True
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

    def test_hod_can_acknowledge_and_assign(self):
        """Test that HOD can acknowledge and assign a consult."""
        # Create a consult
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
        
        # Acknowledge and assign to a doctor
        response = self.client.post(
            f'/api/v1/consults/requests/{consult.id}/acknowledge-assign/',
            {'assigned_to_user_id': self.doctor_cardio.id}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh consult from DB
        consult.refresh_from_db()
        
        # Verify all fields are set correctly
        self.assertEqual(consult.status, 'IN_PROGRESS')
        self.assertEqual(consult.received_by, self.hod_cardio)
        self.assertIsNotNone(consult.received_at)
        self.assertEqual(consult.assigned_to, self.doctor_cardio)
        self.assertEqual(consult.assigned_by, self.hod_cardio)
        self.assertIsNotNone(consult.assigned_at)
        self.assertEqual(consult.assignment_type, 'manual')
        
        # Also verify deprecated fields for backward compatibility
        self.assertEqual(consult.acknowledged_by, self.hod_cardio)
        self.assertIsNotNone(consult.acknowledged_at)

    def test_delegated_receiver_can_acknowledge_and_assign(self):
        """Test that delegated receiver can acknowledge and assign a consult."""
        # Set delegated receiver
        self.dept_cardio.delegated_receiver = self.senior_cardio
        self.dept_cardio.save()
        
        # Create a consult
        consult = ConsultRequest.objects.create(
            patient=self.patient,
            requester=self.doctor_er,
            requesting_department=self.dept_er,
            target_department=self.dept_cardio,
            urgency='URGENT',
            reason_for_consult='Chest pain evaluation',
            status='SUBMITTED'
        )
        
        # Login as delegated receiver
        self.client.force_authenticate(user=self.senior_cardio)
        
        # Acknowledge and assign to a doctor
        response = self.client.post(
            f'/api/v1/consults/requests/{consult.id}/acknowledge-assign/',
            {'assigned_to_user_id': self.doctor_cardio.id}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh consult from DB
        consult.refresh_from_db()
        
        # Verify all fields are set correctly
        self.assertEqual(consult.status, 'IN_PROGRESS')
        self.assertEqual(consult.received_by, self.senior_cardio)
        self.assertEqual(consult.assigned_to, self.doctor_cardio)
        self.assertEqual(consult.assigned_by, self.senior_cardio)

    def test_regular_doctor_cannot_acknowledge_and_assign(self):
        """Test that regular doctor cannot acknowledge and assign."""
        # Create a consult
        consult = ConsultRequest.objects.create(
            patient=self.patient,
            requester=self.doctor_er,
            requesting_department=self.dept_er,
            target_department=self.dept_cardio,
            urgency='URGENT',
            reason_for_consult='Chest pain evaluation',
            status='SUBMITTED'
        )
        
        # Login as regular doctor
        self.client.force_authenticate(user=self.doctor_cardio)
        
        # Try to acknowledge and assign
        response = self.client.post(
            f'/api/v1/consults/requests/{consult.id}/acknowledge-assign/',
            {'assigned_to_user_id': self.doctor_cardio.id}
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Refresh consult from DB
        consult.refresh_from_db()
        
        # Verify consult is unchanged
        self.assertEqual(consult.status, 'SUBMITTED')
        self.assertIsNone(consult.received_by)
        self.assertIsNone(consult.assigned_to)

    def test_cannot_acknowledge_already_assigned_consult(self):
        """Test that already assigned consults cannot be acknowledged again."""
        # Create a consult that's already assigned
        consult = ConsultRequest.objects.create(
            patient=self.patient,
            requester=self.doctor_er,
            requesting_department=self.dept_er,
            target_department=self.dept_cardio,
            urgency='URGENT',
            reason_for_consult='Chest pain evaluation',
            status='IN_PROGRESS',
            assigned_to=self.doctor_cardio
        )
        
        # Login as HOD
        self.client.force_authenticate(user=self.hod_cardio)
        
        # Try to acknowledge and assign again
        response = self.client.post(
            f'/api/v1/consults/requests/{consult.id}/acknowledge-assign/',
            {'assigned_to_user_id': self.doctor_cardio.id}
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_assigned_user_must_be_in_target_department(self):
        """Test that assigned user must belong to target department."""
        # Create a consult
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
        
        # Try to assign to a doctor from a different department
        response = self.client.post(
            f'/api/v1/consults/requests/{consult.id}/acknowledge-assign/',
            {'assigned_to_user_id': self.doctor_er.id}
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('target department', response.data['error'].lower())

    def test_atomic_transaction(self):
        """Test that acknowledgement and assignment happen atomically."""
        # Create a consult
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
        
        # Acknowledge and assign
        response = self.client.post(
            f'/api/v1/consults/requests/{consult.id}/acknowledge-assign/',
            {'assigned_to_user_id': self.doctor_cardio.id}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh consult from DB
        consult.refresh_from_db()
        
        # Verify both received_by and assigned_to are set
        # They should be set together, never one without the other
        if consult.received_by is not None:
            self.assertIsNotNone(consult.assigned_to)
        if consult.assigned_to is not None:
            self.assertIsNotNone(consult.received_by)
        
        # Verify timestamps are close (within a second)
        if consult.received_at and consult.assigned_at:
            time_diff = abs((consult.received_at - consult.assigned_at).total_seconds())
            self.assertLess(time_diff, 1.0)
