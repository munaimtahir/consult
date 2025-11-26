import os
import django
import sys
import json

# Add the project directory to the sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.departments.models import Department
from apps.patients.models import Patient

User = get_user_model()

def test_api():
    print("Starting API verification...")
    client = APIClient()
    
    # 1. Login / Get Token
    print("\n1. Testing Authentication...")
    response = client.post('/api/v1/auth/token/', {
        'email': 'admin@pmc.edu.pk',
        'password': 'adminpassword123'
    }, format='json')
    
    if response.status_code == 200:
        print("✅ Login successful")
        token = response.data['access']
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    else:
        print(f"❌ Login failed: {response.status_code} - {response.data}")
        return

    # 2. List Departments
    print("\n2. Testing Departments API...")
    response = client.get('/api/v1/departments/')
    if response.status_code == 200:
        count = len(response.data)
        print(f"✅ Departments list successful. Found {count} departments.")
    else:
        print(f"❌ Departments list failed: {response.status_code} - {response.data}")

    # 3. List Patients
    print("\n3. Testing Patients API...")
    response = client.get('/api/v1/patients/')
    if response.status_code == 200:
        count = len(response.data)
        print(f"✅ Patients list successful. Found {count} patients.")
    else:
        print(f"❌ Patients list failed: {response.status_code} - {response.data}")

    # 4. Create Consult Request
    print("\n4. Testing Consult Creation...")
    
    # Get necessary IDs
    patient = Patient.objects.first()
    target_dept = Department.objects.get(name='Cardiology')
    requester = User.objects.get(email='admin@pmc.edu.pk') # Admin is requester
    
    # Ensure requester has a department (admin might not)
    if not requester.department:
        ortho = Department.objects.get(name='Orthopedics')
        requester.department = ortho
        requester.save()

    data = {
        'patient': patient.id,
        'requesting_department': requester.department.id,
        'target_department': target_dept.id,
        'urgency': 'ROUTINE',
        'reason_for_consult': 'Routine checkup',
        'clinical_question': 'Please evaluate heart condition.',
        'relevant_history': 'History of hypertension.',
        'current_medications': 'Aspirin',
        'vital_signs': 'BP 120/80',
        'lab_results': 'Normal'
    }
    
    response = client.post('/api/v1/consults/requests/', data, format='json')
    if response.status_code == 201:
        print(f"✅ Consult creation successful. ID: {response.data['id']}")
    else:
        print(f"❌ Consult creation failed: {response.status_code} - {response.data}")

if __name__ == '__main__':
    test_api()
