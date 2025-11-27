from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.accounts.models import User
from apps.departments.models import Department
from apps.patients.models import Patient
from apps.consults.models import ConsultRequest

class ConsultFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create Departments
        self.dept_er = Department.objects.create(name="Emergency", code="ER")
        self.dept_cardio = Department.objects.create(name="Cardiology", code="CARDIO")
        
        # Create Users
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
            role='DOCTOR'
        )
        
        self.receptionist = User.objects.create_user(
            email="reception@pmc.edu.pk",
            password="password123",
            first_name="Reception",
            last_name="Staff",
            department=self.dept_er,
            role='RECEPTIONIST'
        )
        
        # Create Patient
        self.patient = Patient.objects.create(
            name="John Doe",
            mrn="MRN12345",
            date_of_birth="1980-01-01",
            gender="M",
            contact_number="1234567890"
        )

    def test_full_consult_flow(self):
        # 1. Login as ER Doctor
        response = self.client.post('/api/accounts/token/', {
            'email': 'er_doc@pmc.edu.pk',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # 2. Create Consult Request
        consult_data = {
            'patient': self.patient.id,
            'target_department': self.dept_cardio.id,
            'urgency': 'URGENT',
            'reason_for_consult': 'Chest pain',
            'requesting_department': self.dept_er.id
        }
        response = self.client.post('/api/consults/requests/', consult_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        consult_id = response.data['id']
        
        # 3. Switch to Cardio Doctor
        response = self.client.post('/api/accounts/token/', {
            'email': 'cardio_doc@pmc.edu.pk',
            'password': 'password123'
        })
        cardio_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {cardio_token}')
        
        # 4. Acknowledge Consult
        response = self.client.post(f'/api/consults/requests/{consult_id}/acknowledge/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'ACKNOWLEDGED')
        
        # 5. Assign to Self (or another doc)
        response = self.client.post(f'/api/consults/requests/{consult_id}/assign/', {
            'assigned_to': self.doctor_cardio.id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['assigned_to'], self.doctor_cardio.id)
        
        # 6. Add Progress Note
        note_data = {
            'content': 'Patient examined. ECG normal.',
            'note_type': 'PROGRESS'
        }
        response = self.client.post(f'/api/consults/requests/{consult_id}/add_note/', note_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 7. Add Final Note (Complete Consult)
        final_note_data = {
            'content': 'Discharge. No cardiac issue.',
            'note_type': 'FINAL',
            'is_final': True
        }
        response = self.client.post(f'/api/consults/requests/{consult_id}/add_note/', final_note_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify Consult is Completed
        response = self.client.get(f'/api/consults/requests/{consult_id}/')
        self.assertEqual(response.data['status'], 'COMPLETED')
        self.assertIsNotNone(response.data['completed_at'])

    def test_permissions(self):
        # Create a consult
        consult = ConsultRequest.objects.create(
            patient=self.patient,
            requester=self.doctor_er,
            requesting_department=self.dept_er,
            target_department=self.dept_cardio,
            urgency='ROUTINE',
            reason_for_consult='Checkup'
        )
        
        # Create unrelated doctor
        dept_neuro = Department.objects.create(name="Neurology", code="NEURO")
        doctor_neuro = User.objects.create_user(
            email="neuro@pmc.edu.pk",
            password="password123",
            department=dept_neuro,
            role='DOCTOR'
        )
        
        # Login as unrelated doctor
        self.client.force_authenticate(user=doctor_neuro)
        
        # Try to access consult
        response = self.client.get(f'/api/consults/requests/{consult.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Try to add note
        response = self.client.post(f'/api/consults/requests/{consult.id}/add_note/', {
            'content': 'Hacking in'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
