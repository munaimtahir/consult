"""
Tests for Admin Panel endpoints.
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.accounts.models import User
from apps.departments.models import Department
from apps.patients.models import Patient
from apps.consults.models import ConsultRequest


class AdminUserViewSetTests(TestCase):
    """Tests for AdminUserViewSet."""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create departments
        self.dept_er = Department.objects.create(name="Emergency", code="ER")
        self.dept_cardio = Department.objects.create(name="Cardiology", code="CARDIO")
        
        # Create a superuser admin
        self.admin = User.objects.create_superuser(
            email="admin@pmc.edu.pk",
            password="admin123",
            first_name="Admin",
            last_name="User"
        )
        
        # Create a regular doctor
        self.doctor = User.objects.create_user(
            email="doctor@pmc.edu.pk",
            password="doctor123",
            first_name="Regular",
            last_name="Doctor",
            department=self.dept_er,
            role='DOCTOR'
        )
        
        # Create a user with only can_manage_users permission
        self.user_manager = User.objects.create_user(
            email="manager@pmc.edu.pk",
            password="manager123",
            first_name="User",
            last_name="Manager",
            department=self.dept_er,
            can_manage_users=True
        )
    
    def test_admin_can_list_users(self):
        """Admin users can list all users."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/v1/admin/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle paginated response
        data = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        emails = [u['email'] for u in data]
        self.assertIn('admin@pmc.edu.pk', emails)
        self.assertIn('doctor@pmc.edu.pk', emails)
        self.assertIn('manager@pmc.edu.pk', emails)
    
    def test_regular_user_cannot_list_users(self):
        """Regular users cannot access admin user list."""
        self.client.force_authenticate(user=self.doctor)
        response = self.client.get('/api/v1/admin/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_user_manager_can_list_users(self):
        """Users with can_manage_users permission can list users."""
        self.client.force_authenticate(user=self.user_manager)
        response = self.client.get('/api/v1/admin/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_admin_can_create_user(self):
        """Admin can create new users."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/v1/admin/users/', {
            'email': 'newuser@pmc.edu.pk',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpass123',
            'department': self.dept_cardio.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(email='newuser@pmc.edu.pk').count(), 1)
    
    def test_admin_can_update_user(self):
        """Admin can update user information."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(f'/api/v1/admin/users/{self.doctor.id}/', {
            'first_name': 'Updated',
            'department': self.dept_cardio.id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.doctor.refresh_from_db()
        self.assertEqual(self.doctor.first_name, 'Updated')
        self.assertEqual(self.doctor.department, self.dept_cardio)
    
    def test_admin_can_deactivate_user(self):
        """Admin can deactivate a user."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(f'/api/v1/admin/users/{self.doctor.id}/deactivate/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.doctor.refresh_from_db()
        self.assertFalse(self.doctor.is_active)
    
    def test_admin_cannot_deactivate_self(self):
        """Admin cannot deactivate their own account."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(f'/api/v1/admin/users/{self.admin.id}/deactivate/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_superuser_can_update_permissions(self):
        """Superuser can update user permissions."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(f'/api/v1/admin/users/{self.doctor.id}/update_permissions/', {
            'can_manage_users': True,
            'can_view_department_dashboard': True
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.doctor.refresh_from_db()
        self.assertTrue(self.doctor.can_manage_users)
        self.assertTrue(self.doctor.can_view_department_dashboard)
    
    def test_non_superuser_cannot_update_permissions(self):
        """Users without can_manage_permissions cannot update permissions."""
        self.client.force_authenticate(user=self.user_manager)
        response = self.client.patch(f'/api/v1/admin/users/{self.doctor.id}/update_permissions/', {
            'can_manage_users': True
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminDepartmentViewSetTests(TestCase):
    """Tests for AdminDepartmentViewSet."""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create departments
        self.dept_er = Department.objects.create(name="Emergency", code="ER")
        self.dept_cardio = Department.objects.create(name="Cardiology", code="CARDIO")
        
        # Create admin user
        self.admin = User.objects.create_superuser(
            email="admin@pmc.edu.pk",
            password="admin123",
            first_name="Admin",
            last_name="User"
        )
        
        # Create regular doctor
        self.doctor = User.objects.create_user(
            email="doctor@pmc.edu.pk",
            password="doctor123",
            first_name="Regular",
            last_name="Doctor",
            department=self.dept_er,
            role='DOCTOR'
        )
    
    def test_admin_can_list_departments(self):
        """Admin can list all departments."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/v1/admin/departments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle paginated response
        data = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        codes = [d['code'] for d in data]
        self.assertIn('ER', codes)
        self.assertIn('CARDIO', codes)
    
    def test_regular_user_cannot_list_admin_departments(self):
        """Regular users cannot access admin department list."""
        self.client.force_authenticate(user=self.doctor)
        response = self.client.get('/api/v1/admin/departments/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_admin_can_create_department(self):
        """Admin can create new departments."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/v1/admin/departments/', {
            'name': 'Neurology',
            'code': 'NEURO',
            'department_type': 'CLINICAL'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Department.objects.filter(code='NEURO').count(), 1)
    
    def test_admin_can_create_subdepartment(self):
        """Admin can create subdepartments."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/v1/admin/departments/', {
            'name': 'Pediatric Cardiology',
            'code': 'PCARD',
            'department_type': 'CLINICAL',
            'parent': self.dept_cardio.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        subdept = Department.objects.get(code='PCARD')
        self.assertEqual(subdept.parent, self.dept_cardio)
    
    def test_admin_can_update_department(self):
        """Admin can update department information."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(f'/api/v1/admin/departments/{self.dept_er.id}/', {
            'name': 'Emergency Room',
            'contact_number': '123-456-7890'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.dept_er.refresh_from_db()
        self.assertEqual(self.dept_er.name, 'Emergency Room')
        self.assertEqual(self.dept_er.contact_number, '123-456-7890')
    
    def test_cannot_delete_department_with_users(self):
        """Cannot delete department that has assigned users."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/v1/admin/departments/{self.dept_er.id}/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DashboardViewTests(TestCase):
    """Tests for Dashboard API endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create departments
        self.dept_er = Department.objects.create(name="Emergency", code="ER")
        self.dept_cardio = Department.objects.create(name="Cardiology", code="CARDIO")
        
        # Create admin user with global dashboard access
        self.admin = User.objects.create_superuser(
            email="admin@pmc.edu.pk",
            password="admin123",
            first_name="Admin",
            last_name="User"
        )
        
        # Create HOD with department dashboard access
        self.hod = User.objects.create_user(
            email="hod@pmc.edu.pk",
            password="hod123",
            first_name="Head",
            last_name="Doctor",
            department=self.dept_cardio,
            role='HOD',
            can_view_department_dashboard=True
        )
        
        # Create regular doctor without dashboard access
        self.doctor = User.objects.create_user(
            email="doctor@pmc.edu.pk",
            password="doctor123",
            first_name="Regular",
            last_name="Doctor",
            department=self.dept_er,
            role='DOCTOR'
        )
        
        # Create patient and consult for testing
        self.patient = Patient.objects.create(
            name="Test Patient",
            mrn="MRN12345",
            age=45,
            gender="M",
            ward="General",
            bed_number="B1",
            primary_department=self.dept_er
        )
        
        self.consult = ConsultRequest.objects.create(
            patient=self.patient,
            requester=self.doctor,
            requesting_department=self.dept_er,
            target_department=self.dept_cardio,
            urgency='URGENT',
            reason_for_consult='Test consult'
        )
    
    def test_admin_can_view_global_dashboard(self):
        """Admin can view global dashboard."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/v1/admin/dashboards/global/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('global_kpis', response.data)
        self.assertIn('consults', response.data)
        self.assertIn('department_stats', response.data)
    
    def test_regular_user_cannot_view_global_dashboard(self):
        """Regular users cannot view global dashboard."""
        self.client.force_authenticate(user=self.doctor)
        response = self.client.get('/api/v1/admin/dashboards/global/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_hod_can_view_own_department_dashboard(self):
        """HOD can view their department's dashboard."""
        self.client.force_authenticate(user=self.hod)
        response = self.client.get('/api/v1/admin/dashboards/department/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['department']['id'], self.dept_cardio.id)
    
    def test_hod_cannot_view_other_department_dashboard(self):
        """HOD cannot view other department's dashboard."""
        self.client.force_authenticate(user=self.hod)
        response = self.client.get(f'/api/v1/admin/dashboards/department/?department_id={self.dept_er.id}')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_admin_can_view_any_department_dashboard(self):
        """Admin can view any department's dashboard."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f'/api/v1/admin/dashboards/department/?department_id={self.dept_er.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['department']['id'], self.dept_er.id)
    
    def test_department_dashboard_shows_correct_consults(self):
        """Department dashboard shows correct received/sent consults."""
        self.client.force_authenticate(user=self.admin)
        
        # Check cardiology (receiving department)
        response = self.client.get(f'/api/v1/admin/dashboards/department/?department_id={self.dept_cardio.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['received_consults']), 1)
        self.assertEqual(len(response.data['sent_consults']), 0)
        
        # Check ER (sending department)
        response = self.client.get(f'/api/v1/admin/dashboards/department/?department_id={self.dept_er.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['received_consults']), 0)
        self.assertEqual(len(response.data['sent_consults']), 1)


class ConsultManagementTests(TestCase):
    """Tests for consult reassignment and force close."""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create departments
        self.dept_er = Department.objects.create(name="Emergency", code="ER")
        self.dept_cardio = Department.objects.create(name="Cardiology", code="CARDIO")
        
        # Create admin with global consult management
        self.admin = User.objects.create_superuser(
            email="admin@pmc.edu.pk",
            password="admin123",
            first_name="Admin",
            last_name="User"
        )
        
        # Create regular doctor
        self.doctor = User.objects.create_user(
            email="doctor@pmc.edu.pk",
            password="doctor123",
            first_name="Regular",
            last_name="Doctor",
            department=self.dept_er,
            role='DOCTOR'
        )
        
        # Create target doctor
        self.cardio_doc = User.objects.create_user(
            email="cardio@pmc.edu.pk",
            password="cardio123",
            first_name="Cardio",
            last_name="Doctor",
            department=self.dept_cardio,
            role='DOCTOR'
        )
        
        # Create patient and consult
        self.patient = Patient.objects.create(
            name="Test Patient",
            mrn="MRN12345",
            age=45,
            gender="M",
            ward="General",
            bed_number="B1",
            primary_department=self.dept_er
        )
        
        self.consult = ConsultRequest.objects.create(
            patient=self.patient,
            requester=self.doctor,
            requesting_department=self.dept_er,
            target_department=self.dept_cardio,
            urgency='URGENT',
            reason_for_consult='Test consult'
        )
    
    def test_admin_can_reassign_consult(self):
        """Admin can reassign consult to another doctor."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(f'/api/v1/admin/consults/{self.consult.id}/reassign/', {
            'assigned_to': self.cardio_doc.id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.consult.refresh_from_db()
        self.assertEqual(self.consult.assigned_to, self.cardio_doc)
    
    def test_regular_user_cannot_reassign_consult(self):
        """Regular users cannot reassign consults."""
        self.client.force_authenticate(user=self.doctor)
        response = self.client.post(f'/api/v1/admin/consults/{self.consult.id}/reassign/', {
            'assigned_to': self.cardio_doc.id
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_admin_can_force_close_consult(self):
        """Admin can force close a consult with reason."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(f'/api/v1/admin/consults/{self.consult.id}/force-close/', {
            'reason': 'Patient transferred to another hospital',
            'action': 'cancel'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.consult.refresh_from_db()
        self.assertEqual(self.consult.status, 'CANCELLED')
    
    def test_force_close_requires_reason(self):
        """Force closing a consult requires a reason."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(f'/api/v1/admin/consults/{self.consult.id}/force-close/', {
            'action': 'complete'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
