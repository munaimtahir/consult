"""
Tests for Core services including audit, assignment, and escalation.
"""

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta

from apps.accounts.models import User
from apps.departments.models import Department
from apps.patients.models import Patient
from apps.consults.models import ConsultRequest
from apps.core.models import (
    AuditLog, FilterPreset, OnCallSchedule, AssignmentPolicy
)
from apps.core.services.audit_service import AuditService
from apps.core.services.assignment_service import AssignmentService
from apps.core.services.escalation_service import EscalationService


class AuditServiceTests(TestCase):
    """Tests for the AuditService."""

    def setUp(self):
        """Set up test data."""
        self.dept = Department.objects.create(name="Cardiology", code="CARDIO")
        
        self.doctor = User.objects.create_user(
            email="doctor@pmc.edu.pk",
            password="password123",
            first_name="Test",
            last_name="Doctor",
            department=self.dept,
            role='DOCTOR'
        )
        
        self.patient = Patient.objects.create(
            name="John Doe",
            mrn="MRN12345",
            age=44,
            gender="M",
            ward="General Ward",
            bed_number="A1",
            primary_department=self.dept,
            primary_diagnosis="Chest pain"
        )
        
        self.consult = ConsultRequest.objects.create(
            patient=self.patient,
            requester=self.doctor,
            requesting_department=self.dept,
            target_department=self.dept,
            urgency='ROUTINE',
            reason_for_consult='Test consult'
        )

    def test_log_action(self):
        """Test basic action logging."""
        log = AuditService.log_action(
            action='CONSULT_CREATED',
            actor=self.doctor,
            consult=self.consult,
            details={'test': 'value'}
        )
        
        self.assertIsNotNone(log.id)
        self.assertEqual(log.action, 'CONSULT_CREATED')
        self.assertEqual(log.actor, self.doctor)
        self.assertEqual(log.consult, self.consult)
        self.assertEqual(log.details['test'], 'value')

    def test_log_consult_created(self):
        """Test consult creation logging."""
        log = AuditService.log_consult_created(self.consult, self.doctor)
        
        self.assertEqual(log.action, 'CONSULT_CREATED')
        self.assertIn('urgency', log.details)

    def test_log_consult_assigned(self):
        """Test consult assignment logging."""
        assignee = User.objects.create_user(
            email="assignee@pmc.edu.pk",
            password="password123",
            department=self.dept,
            role='DOCTOR'
        )
        
        log = AuditService.log_consult_assigned(
            self.consult,
            assignee,
            self.doctor
        )
        
        self.assertEqual(log.action, 'CONSULT_ASSIGNED')
        self.assertEqual(log.target_user, assignee)

    def test_log_unauthorized_access(self):
        """Test unauthorized access logging."""
        log = AuditService.log_unauthorized_access(
            user=self.doctor,
            resource_type='CONSULT',
            resource_id=999,
            action_attempted='view'
        )
        
        self.assertIsNotNone(log.id)
        self.assertEqual(log.resource_type, 'CONSULT')


class AssignmentServiceTests(TestCase):
    """Tests for the AssignmentService."""

    def setUp(self):
        """Set up test data."""
        self.dept = Department.objects.create(name="Cardiology", code="CARDIO")
        
        self.doctor1 = User.objects.create_user(
            email="doctor1@pmc.edu.pk",
            password="password123",
            first_name="Doctor",
            last_name="One",
            department=self.dept,
            role='DOCTOR',
            seniority_level=3
        )
        
        self.doctor2 = User.objects.create_user(
            email="doctor2@pmc.edu.pk",
            password="password123",
            first_name="Doctor",
            last_name="Two",
            department=self.dept,
            role='DOCTOR',
            seniority_level=5
        )
        
        self.hod = User.objects.create_user(
            email="hod@pmc.edu.pk",
            password="password123",
            first_name="Test",
            last_name="HOD",
            department=self.dept,
            role='HOD',
            seniority_level=9
        )
        
        self.patient = Patient.objects.create(
            name="John Doe",
            mrn="MRN12345",
            age=44,
            gender="M",
            ward="General Ward",
            bed_number="A1",
            primary_department=self.dept,
            primary_diagnosis="Chest pain"
        )
        
        self.consult = ConsultRequest.objects.create(
            patient=self.patient,
            requester=self.doctor1,
            requesting_department=self.dept,
            target_department=self.dept,
            urgency='ROUTINE',
            reason_for_consult='Test consult'
        )

    def test_get_assignment_policy(self):
        """Test getting assignment policy."""
        # Create a policy
        policy = AssignmentPolicy.objects.create(
            department=self.dept,
            urgency='ROUTINE',
            assignment_mode='LOAD_BALANCE',
            is_active=True
        )
        
        result = AssignmentService.get_assignment_policy(self.dept, 'ROUTINE')
        
        self.assertEqual(result, policy)

    def test_get_load_balance_stats(self):
        """Test getting load balance statistics."""
        stats = AssignmentService.get_load_balance_stats(self.dept)
        
        self.assertIsInstance(stats, list)
        # Should have 3 users in the department
        self.assertEqual(len(stats), 3)
        
        # Check that stats contain expected fields
        if stats:
            self.assertIn('user_id', stats[0])
            self.assertIn('active_consults', stats[0])

    def test_auto_assign_with_load_balance(self):
        """Test auto-assignment with load balance mode."""
        # Create load balance policy
        AssignmentPolicy.objects.create(
            department=self.dept,
            urgency='ROUTINE',
            assignment_mode='LOAD_BALANCE',
            is_active=True
        )
        
        assignee = AssignmentService.auto_assign(self.consult)
        
        # Should assign to someone
        self.assertIsNotNone(assignee)
        self.assertEqual(assignee.department, self.dept)

    def test_on_call_assignment(self):
        """Test on-call assignment."""
        # Set a doctor as on-call
        self.doctor1.is_on_call = True
        self.doctor1.save()
        
        on_call = AssignmentService.get_on_call_doctor(self.dept)
        
        self.assertEqual(on_call, self.doctor1)


class EscalationServiceTests(TestCase):
    """Tests for the EscalationService."""

    def setUp(self):
        """Set up test data."""
        self.dept = Department.objects.create(name="Cardiology", code="CARDIO")
        
        self.junior = User.objects.create_user(
            email="junior@pmc.edu.pk",
            password="password123",
            first_name="Junior",
            last_name="Doctor",
            department=self.dept,
            role='DOCTOR',
            seniority_level=2
        )
        
        self.senior = User.objects.create_user(
            email="senior@pmc.edu.pk",
            password="password123",
            first_name="Senior",
            last_name="Doctor",
            department=self.dept,
            role='DOCTOR',
            seniority_level=6
        )
        
        self.patient = Patient.objects.create(
            name="John Doe",
            mrn="MRN12345",
            age=44,
            gender="M",
            ward="General Ward",
            bed_number="A1",
            primary_department=self.dept,
            primary_diagnosis="Chest pain"
        )

    def test_get_overdue_consults(self):
        """Test getting overdue consults."""
        # Create a consult that is overdue (expected_response_time in the past)
        past_time = timezone.now() - timedelta(hours=1)
        overdue = ConsultRequest.objects.create(
            patient=self.patient,
            requester=self.junior,
            requesting_department=self.dept,
            target_department=self.dept,
            urgency='ROUTINE',
            reason_for_consult='Test',
            status='PENDING'
        )
        # Update the expected_response_time to the past to make it overdue
        # Use update() to avoid triggering save() which recalculates is_overdue
        ConsultRequest.objects.filter(pk=overdue.pk).update(
            expected_response_time=past_time,
            is_overdue=True
        )
        overdue.refresh_from_db()
        
        result = EscalationService.get_overdue_consults(self.dept)
        
        self.assertIn(overdue, result)

    def test_get_approaching_deadline_consults(self):
        """Test getting consults approaching deadline."""
        # Create a consult with deadline soon
        approaching = ConsultRequest.objects.create(
            patient=self.patient,
            requester=self.junior,
            requesting_department=self.dept,
            target_department=self.dept,
            urgency='ROUTINE',
            reason_for_consult='Test',
            expected_response_time=timezone.now() + timedelta(minutes=15)
        )
        
        result = EscalationService.get_approaching_deadline_consults(
            self.dept,
            threshold_minutes=30
        )
        
        self.assertIn(approaching, result)


class FilterPresetTests(TestCase):
    """Tests for filter preset functionality."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.dept = Department.objects.create(name="Cardiology", code="CARDIO")
        
        self.user = User.objects.create_user(
            email="user@pmc.edu.pk",
            password="password123",
            first_name="Test",
            last_name="User",
            department=self.dept,
            role='DOCTOR'
        )

    def test_create_filter_preset(self):
        """Test creating a filter preset."""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'name': 'My Emergency Filters',
            'filters': {
                'urgency': 'EMERGENCY',
                'status': 'PENDING'
            },
            'is_default': False
        }
        
        response = self.client.post('/api/v1/filter-presets/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'My Emergency Filters')

    def test_list_filter_presets(self):
        """Test listing filter presets."""
        # Create a preset
        FilterPreset.objects.create(
            user=self.user,
            name='Test Preset',
            filters={'status': 'PENDING'}
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/filter-presets/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # The response might be paginated, so check results key or the response itself
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)

    def test_only_own_presets_visible(self):
        """Test that users can only see their own presets."""
        other_user = User.objects.create_user(
            email="other@pmc.edu.pk",
            password="password123",
            department=self.dept,
            role='DOCTOR'
        )
        
        # Create presets for both users
        FilterPreset.objects.create(
            user=self.user,
            name='My Preset',
            filters={}
        )
        FilterPreset.objects.create(
            user=other_user,
            name='Other Preset',
            filters={}
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/filter-presets/')
        
        # The response might be paginated, so check results key or the response itself
        results = response.data.get('results', response.data)
        
        # Should only see own preset
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'My Preset')
