"""
Tests for Analytics service and views.
"""

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta

from apps.accounts.models import User
from apps.departments.models import Department
from apps.patients.models import Patient
from apps.consults.models import ConsultRequest, ConsultNote
from apps.analytics.models import DoctorPerformanceMetric, DepartmentDailyStats, ConsultTimeline
from apps.analytics.services import AnalyticsService


class AnalyticsServiceTests(TestCase):
    """Tests for the AnalyticsService."""

    def setUp(self):
        """Set up test data."""
        self.dept_er = Department.objects.create(name="Emergency", code="ER")
        self.dept_cardio = Department.objects.create(name="Cardiology", code="CARDIO")
        
        self.doctor_er = User.objects.create_user(
            email="er_doc@pmc.edu.pk",
            password="password123",
            first_name="ER",
            last_name="Doc",
            department=self.dept_er,
            role='DOCTOR'
        )
        
        self.doctor_cardio = User.objects.create_user(
            email="cardio_doc@pmc.edu.pk",
            password="password123",
            first_name="Cardio",
            last_name="Doc",
            department=self.dept_cardio,
            role='HOD'
        )
        
        self.admin = User.objects.create_user(
            email="admin@pmc.edu.pk",
            password="password123",
            first_name="Admin",
            last_name="User",
            role='ADMIN',
            can_view_global_dashboard=True
        )
        
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
        
        # Create a completed consult
        self.consult = ConsultRequest.objects.create(
            patient=self.patient,
            requester=self.doctor_er,
            requesting_department=self.dept_er,
            target_department=self.dept_cardio,
            assigned_to=self.doctor_cardio,
            urgency='URGENT',
            reason_for_consult='Chest pain evaluation',
            status='COMPLETED',
            acknowledged_at=timezone.now() - timedelta(hours=1),
            completed_at=timezone.now()
        )

    def test_get_doctor_performance(self):
        """Test getting doctor performance metrics."""
        metrics = AnalyticsService.get_doctor_performance(self.doctor_cardio)
        
        self.assertEqual(metrics['doctor_id'], self.doctor_cardio.id)
        self.assertEqual(metrics['doctor_name'], 'Cardio Doc')
        self.assertIn('consults_completed', metrics)
        self.assertIn('sla_compliance_rate', metrics)
        self.assertIn('avg_response_time_minutes', metrics)

    def test_get_department_stats(self):
        """Test getting department statistics."""
        stats = AnalyticsService.get_department_stats(self.dept_cardio)
        
        self.assertEqual(stats['department_id'], self.dept_cardio.id)
        self.assertEqual(stats['department_name'], 'Cardiology')
        self.assertIn('total_received', stats)
        self.assertIn('completed', stats)
        self.assertIn('sla_compliance_rate', stats)

    def test_get_global_stats(self):
        """Test getting global system statistics."""
        stats = AnalyticsService.get_global_stats()
        
        self.assertIn('total_consults', stats)
        self.assertIn('completed', stats)
        self.assertIn('sla_compliance_rate', stats)
        self.assertIn('department_ranking', stats)

    def test_add_timeline_event(self):
        """Test adding a timeline event."""
        event = AnalyticsService.add_timeline_event(
            consult=self.consult,
            event_type='CREATED',
            actor=self.doctor_er,
            description='Test event'
        )
        
        self.assertIsNotNone(event.id)
        self.assertEqual(event.event_type, 'CREATED')
        self.assertEqual(event.actor, self.doctor_er)

    def test_get_consult_timeline(self):
        """Test getting consult timeline."""
        # Add a timeline event
        AnalyticsService.add_timeline_event(
            consult=self.consult,
            event_type='CREATED',
            actor=self.doctor_er
        )
        
        timeline = AnalyticsService.get_consult_timeline(self.consult)
        
        self.assertIsInstance(timeline, list)
        self.assertGreater(len(timeline), 0)
        self.assertIn('event_type', timeline[0])
        self.assertIn('timestamp_human', timeline[0])


class AnalyticsViewsTests(TestCase):
    """Tests for Analytics API views."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        self.dept = Department.objects.create(name="Cardiology", code="CARDIO")
        
        self.doctor = User.objects.create_user(
            email="doctor@pmc.edu.pk",
            password="password123",
            first_name="Test",
            last_name="Doctor",
            department=self.dept,
            role='DOCTOR'
        )
        
        self.hod = User.objects.create_user(
            email="hod@pmc.edu.pk",
            password="password123",
            first_name="Test",
            last_name="HOD",
            department=self.dept,
            role='HOD'
        )
        
        self.admin = User.objects.create_user(
            email="admin@pmc.edu.pk",
            password="password123",
            first_name="Admin",
            last_name="User",
            role='ADMIN',
            can_view_global_dashboard=True
        )

    def test_my_performance_endpoint(self):
        """Test the my-performance endpoint."""
        self.client.force_authenticate(user=self.doctor)
        response = self.client.get('/api/v1/analytics/doctor-performance/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['doctor_id'], self.doctor.id)

    def test_department_stats_endpoint(self):
        """Test the department stats endpoint."""
        self.client.force_authenticate(user=self.hod)
        response = self.client.get('/api/v1/analytics/department-stats/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['department_id'], self.dept.id)

    def test_global_stats_requires_permission(self):
        """Test that global stats requires permission."""
        # Regular doctor cannot access
        self.client.force_authenticate(user=self.doctor)
        response = self.client.get('/api/v1/analytics/global-stats/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_global_stats_admin_access(self):
        """Test that admin can access global stats."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/v1/analytics/global-stats/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_consults', response.data)
