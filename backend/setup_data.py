import os
import django
import sys

# Add the project directory to the sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.departments.models import Department
from apps.patients.models import Patient

User = get_user_model()

def create_data():
    print("Starting data population...")
    
    # Create Superuser
    if not User.objects.filter(email='admin@pmc.edu.pk').exists():
        User.objects.create_superuser(
            email='admin@pmc.edu.pk',
            username='admin',
            password='adminpassword123',
            first_name='Admin',
            last_name='User'
        )
        print("Superuser created: admin@pmc.edu.pk / adminpassword123")
    else:
        print("Superuser already exists.")

    # Create Departments
    cardio, _ = Department.objects.get_or_create(
        name='Cardiology',
        defaults={'code': 'CARDIO', 'contact_number': '101'}
    )
    neuro, _ = Department.objects.get_or_create(
        name='Neurology',
        defaults={'code': 'NEURO', 'contact_number': '102'}
    )
    ortho, _ = Department.objects.get_or_create(
        name='Orthopedics',
        defaults={'code': 'ORTHO', 'contact_number': '103'}
    )
    print("Departments created: Cardiology, Neurology, Orthopedics")

    # Create Users
    # Cardio HOD
    if not User.objects.filter(email='cardio.hod@pmc.edu.pk').exists():
        User.objects.create_user(
            email='cardio.hod@pmc.edu.pk',
            username='cardio_hod',
            password='password123',
            first_name='Cardio',
            last_name='HOD',
            role='HOD',
            designation='HOD',
            department=cardio
        )
        print("Created user: cardio.hod@pmc.edu.pk")
    
    # Cardio Doctor
    if not User.objects.filter(email='cardio.doc@pmc.edu.pk').exists():
        User.objects.create_user(
            email='cardio.doc@pmc.edu.pk',
            username='cardio_doc',
            password='password123',
            first_name='Cardio',
            last_name='Doctor',
            role='DOCTOR',
            designation='RESIDENT_3',
            department=cardio
        )
        print("Created user: cardio.doc@pmc.edu.pk")

    # Create Patients
    if not Patient.objects.filter(mrn='MRN001').exists():
        Patient.objects.create(
            mrn='MRN001',
            name='John Doe',
            age=45,
            gender='M',
            ward='General Ward',
            bed_number='101',
            primary_department=ortho,
            primary_diagnosis='Fracture'
        )
        print("Created patient: John Doe (MRN001)")
    
    print("Data population completed successfully.")

if __name__ == '__main__':
    create_data()
