"""
Comprehensive seed data script for Hospital Consult System demo.

This script creates:
- 1 Superuser
- 1 Admin user with all permissions
- Users for each role (Doctor, Department User, HOD) across departments
- Multiple patients for analytics demonstration
- Sample consult requests at various states

DEMO CREDENTIALS:
=================
Superuser:
  Email: admin@pmc.edu.pk
  Password: adminpassword123

Admin User:
  Email: sysadmin@pmc.edu.pk
  Password: password123

Head of Departments (HOD):
  Email: cardio.hod@pmc.edu.pk / neuro.hod@pmc.edu.pk / ortho.hod@pmc.edu.pk
  Password: password123

Department Users (Professors):
  Email: cardio.prof@pmc.edu.pk / neuro.prof@pmc.edu.pk / ortho.prof@pmc.edu.pk
  Password: password123

Doctors (Residents):
  Email: cardio.doc@pmc.edu.pk / neuro.doc@pmc.edu.pk / ortho.doc@pmc.edu.pk
  Password: password123
"""

import os
import django
import sys
from datetime import timedelta

# Add the project directory to the sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.departments.models import Department
from apps.patients.models import Patient
from apps.consults.models import ConsultRequest, ConsultNote

User = get_user_model()


def create_departments():
    """Create departments with SLA configuration."""
    print("\n=== Creating Departments ===")
    
    departments = {}
    
    # Cardiology
    cardio, created = Department.objects.get_or_create(
        name='Cardiology',
        defaults={
            'code': 'CARDIO',
            'contact_number': '101',
            'department_type': 'CLINICAL',
            'emergency_sla': 30,  # 30 minutes for emergency
            'urgent_sla': 120,    # 2 hours for urgent
            'routine_sla': 1440,  # 24 hours for routine
        }
    )
    departments['cardio'] = cardio
    print(f"{'Created' if created else 'Already exists'}: Cardiology (SLA: Emergency 30m, Urgent 2h, Routine 24h)")
    
    # Neurology
    neuro, created = Department.objects.get_or_create(
        name='Neurology',
        defaults={
            'code': 'NEURO',
            'contact_number': '102',
            'department_type': 'CLINICAL',
            'emergency_sla': 15,  # 15 minutes for emergency (stroke time-critical)
            'urgent_sla': 60,     # 1 hour for urgent
            'routine_sla': 720,   # 12 hours for routine
        }
    )
    departments['neuro'] = neuro
    print(f"{'Created' if created else 'Already exists'}: Neurology (SLA: Emergency 15m, Urgent 1h, Routine 12h)")
    
    # Orthopedics
    ortho, created = Department.objects.get_or_create(
        name='Orthopedics',
        defaults={
            'code': 'ORTHO',
            'contact_number': '103',
            'department_type': 'CLINICAL',
            'emergency_sla': 60,
            'urgent_sla': 240,
            'routine_sla': 1440,
        }
    )
    departments['ortho'] = ortho
    print(f"{'Created' if created else 'Already exists'}: Orthopedics")
    
    # General Medicine
    medicine, created = Department.objects.get_or_create(
        name='General Medicine',
        defaults={
            'code': 'MED',
            'contact_number': '104',
            'department_type': 'CLINICAL',
            'emergency_sla': 60,
            'urgent_sla': 180,
            'routine_sla': 1440,
        }
    )
    departments['medicine'] = medicine
    print(f"{'Created' if created else 'Already exists'}: General Medicine")
    
    # Emergency
    emergency, created = Department.objects.get_or_create(
        name='Emergency',
        defaults={
            'code': 'ER',
            'contact_number': '100',
            'department_type': 'CLINICAL',
            'emergency_sla': 10,
            'urgent_sla': 30,
            'routine_sla': 60,
        }
    )
    departments['emergency'] = emergency
    print(f"{'Created' if created else 'Already exists'}: Emergency")
    
    return departments


def create_superuser():
    """Create superuser account."""
    print("\n=== Creating Superuser ===")
    
    if not User.objects.filter(email='admin@pmc.edu.pk').exists():
        user = User.objects.create_superuser(
            email='admin@pmc.edu.pk',
            username='admin',
            password='adminpassword123',
            first_name='Super',
            last_name='Admin'
        )
        print(f"✓ Superuser created: admin@pmc.edu.pk / adminpassword123")
        return user
    else:
        user = User.objects.get(email='admin@pmc.edu.pk')
        print("  Superuser already exists: admin@pmc.edu.pk")
        return user


def create_admin_user():
    """Create system admin user with all permissions."""
    print("\n=== Creating Admin User ===")
    
    if not User.objects.filter(email='sysadmin@pmc.edu.pk').exists():
        user = User.objects.create_user(
            email='sysadmin@pmc.edu.pk',
            username='sysadmin',
            password='password123',
            first_name='System',
            last_name='Administrator',
            role='ADMIN',
            is_staff=True,
            can_manage_users=True,
            can_manage_departments=True,
            can_view_department_dashboard=True,
            can_view_global_dashboard=True,
            can_manage_consults_globally=True,
            can_manage_permissions=True,
        )
        print(f"✓ Admin user created: sysadmin@pmc.edu.pk / password123")
        return user
    else:
        user = User.objects.get(email='sysadmin@pmc.edu.pk')
        print("  Admin user already exists: sysadmin@pmc.edu.pk")
        return user


def create_department_users(departments):
    """Create HOD, Department User (Professor), and Doctor for each department."""
    print("\n=== Creating Department Users ===")
    
    users = {}
    
    dept_configs = [
        ('cardio', 'Cardiology', 'Dr. Ahmed', 'Khan', 'Dr. Sarah', 'Ali', 'Dr. Omar', 'Hassan'),
        ('neuro', 'Neurology', 'Dr. Fatima', 'Malik', 'Dr. Bilal', 'Sheikh', 'Dr. Zara', 'Ahmed'),
        ('ortho', 'Orthopedics', 'Dr. Imran', 'Qureshi', 'Dr. Ayesha', 'Mirza', 'Dr. Usman', 'Raza'),
        ('medicine', 'Medicine', 'Dr. Rashid', 'Butt', 'Dr. Saima', 'Farooq', 'Dr. Kamran', 'Siddiqui'),
        ('emergency', 'Emergency', 'Dr. Tariq', 'Mehmood', 'Dr. Nadia', 'Iqbal', 'Dr. Asif', 'Javed'),
    ]
    
    for dept_key, dept_name, hod_first, hod_last, prof_first, prof_last, doc_first, doc_last in dept_configs:
        if dept_key not in departments:
            continue
            
        dept = departments[dept_key]
        prefix = dept_key.replace('medicine', 'med').replace('emergency', 'er')
        
        # Create HOD
        hod_email = f'{prefix}.hod@pmc.edu.pk'
        if not User.objects.filter(email=hod_email).exists():
            hod = User.objects.create_user(
                email=hod_email,
                password='password123',
                first_name=hod_first,
                last_name=hod_last,
                designation='HOD',
                department=dept,
                can_view_department_dashboard=True,
                can_manage_consults_globally=False,
            )
            # Update department head
            dept.head = hod
            dept.save()
            print(f"✓ HOD created: {hod_email}")
        else:
            hod = User.objects.get(email=hod_email)
            print(f"  HOD already exists: {hod_email}")
        users[f'{dept_key}_hod'] = hod
        
        # Create Professor (Department User)
        prof_email = f'{prefix}.prof@pmc.edu.pk'
        if not User.objects.filter(email=prof_email).exists():
            prof = User.objects.create_user(
                email=prof_email,
                password='password123',
                first_name=prof_first,
                last_name=prof_last,
                designation='PROFESSOR',
                department=dept,
            )
            print(f"✓ Professor created: {prof_email}")
        else:
            prof = User.objects.get(email=prof_email)
            print(f"  Professor already exists: {prof_email}")
        users[f'{dept_key}_prof'] = prof
        
        # Create Doctor (Resident)
        doc_email = f'{prefix}.doc@pmc.edu.pk'
        if not User.objects.filter(email=doc_email).exists():
            doc = User.objects.create_user(
                email=doc_email,
                password='password123',
                first_name=doc_first,
                last_name=doc_last,
                designation='RESIDENT_3',
                department=dept,
            )
            print(f"✓ Doctor created: {doc_email}")
        else:
            doc = User.objects.get(email=doc_email)
            print(f"  Doctor already exists: {doc_email}")
        users[f'{dept_key}_doc'] = doc
    
    return users


def create_patients(departments):
    """Create sample patients for demo."""
    print("\n=== Creating Patients ===")
    
    patients = []
    
    patient_data = [
        # (MRN, Name, Age, Gender, Ward, Bed, Dept Key, Diagnosis)
        ('MRN001', 'Muhammad Ali Khan', 65, 'M', 'CCU', 'C-101', 'cardio', 'Acute Myocardial Infarction'),
        ('MRN002', 'Fatima Bibi', 45, 'F', 'Cardio Ward', 'CW-205', 'cardio', 'Atrial Fibrillation'),
        ('MRN003', 'Ahmed Hassan', 72, 'M', 'Neuro ICU', 'N-001', 'neuro', 'Ischemic Stroke'),
        ('MRN004', 'Ayesha Siddiqui', 35, 'F', 'Neuro Ward', 'NW-112', 'neuro', 'Multiple Sclerosis'),
        ('MRN005', 'Imran Qureshi', 28, 'M', 'Ortho Ward', 'OW-301', 'ortho', 'Compound Fracture - Tibia'),
        ('MRN006', 'Zara Ahmed', 55, 'F', 'Ortho Ward', 'OW-305', 'ortho', 'Hip Replacement - Post Op'),
        ('MRN007', 'Rashid Mahmood', 60, 'M', 'General Ward', 'GW-401', 'medicine', 'Diabetic Ketoacidosis'),
        ('MRN008', 'Saima Farooq', 42, 'F', 'General Ward', 'GW-410', 'medicine', 'Community Acquired Pneumonia'),
        ('MRN009', 'Bilal Sheikh', 50, 'M', 'Emergency', 'ER-001', 'emergency', 'Chest Pain - Rule out MI'),
        ('MRN010', 'Nadia Iqbal', 38, 'F', 'Emergency', 'ER-005', 'emergency', 'Severe Headache - Rule out SAH'),
        ('MRN011', 'Kamran Ali', 70, 'M', 'CCU', 'C-103', 'cardio', 'Congestive Heart Failure'),
        ('MRN012', 'Hina Malik', 48, 'F', 'Cardio Ward', 'CW-208', 'cardio', 'Hypertensive Crisis'),
        ('MRN013', 'Tariq Butt', 58, 'M', 'Neuro Ward', 'NW-115', 'neuro', 'Parkinson Disease'),
        ('MRN014', 'Sara Khan', 32, 'F', 'General Ward', 'GW-412', 'medicine', 'Acute Pancreatitis'),
        ('MRN015', 'Usman Raza', 25, 'M', 'Ortho Ward', 'OW-310', 'ortho', 'ACL Tear - Pre Op'),
    ]
    
    for mrn, name, age, gender, ward, bed, dept_key, diagnosis in patient_data:
        if dept_key not in departments:
            continue
            
        dept = departments[dept_key]
        
        if not Patient.objects.filter(mrn=mrn).exists():
            patient = Patient.objects.create(
                mrn=mrn,
                name=name,
                age=age,
                gender=gender,
                ward=ward,
                bed_number=bed,
                primary_department=dept,
                primary_diagnosis=diagnosis
            )
            print(f"✓ Patient created: {name} ({mrn})")
        else:
            patient = Patient.objects.get(mrn=mrn)
            print(f"  Patient already exists: {name} ({mrn})")
        patients.append(patient)
    
    return patients


def create_sample_consults(departments, users, patients):
    """Create sample consult requests at various workflow stages."""
    print("\n=== Creating Sample Consults ===")
    
    if ConsultRequest.objects.count() > 0:
        print("  Sample consults already exist, skipping...")
        return
    
    now = timezone.now()
    
    consults_data = [
        # (Patient MRN, From Dept, To Dept, Urgency, Status, Reason, Hours Ago, Assigned To)
        
        # Pending consults (new, not acknowledged)
        ('MRN009', 'emergency', 'cardio', 'EMERGENCY', 'PENDING', 
         'Patient presenting with chest pain, elevated troponins. Please evaluate urgently for possible STEMI.', 
         0.5, None),
        
        ('MRN010', 'emergency', 'neuro', 'EMERGENCY', 'PENDING',
         'Severe headache with neck stiffness. CT pending. Please evaluate for possible subarachnoid hemorrhage.',
         0.25, None),
        
        # Acknowledged consults (received but not assigned)
        ('MRN001', 'emergency', 'cardio', 'URGENT', 'ACKNOWLEDGED',
         'Known CAD patient with worsening angina. Please evaluate for cardiac catheterization.',
         2, None),
        
        # In Progress consults (assigned and being worked on)
        ('MRN003', 'emergency', 'neuro', 'EMERGENCY', 'IN_PROGRESS',
         'Acute stroke symptoms. tPA administered. Please assume care for post-thrombolysis monitoring.',
         4, 'neuro_doc'),
        
        ('MRN005', 'emergency', 'ortho', 'URGENT', 'IN_PROGRESS',
         'Compound fracture right tibia from motor vehicle accident. Please evaluate for surgical fixation.',
         6, 'ortho_doc'),
        
        ('MRN007', 'emergency', 'medicine', 'URGENT', 'IN_PROGRESS',
         'DKA with altered mental status. Currently stabilizing in ER. Please assume care.',
         3, 'med_doc'),
        
        # Completed consults (for analytics)
        ('MRN002', 'medicine', 'cardio', 'ROUTINE', 'COMPLETED',
         'New onset palpitations. ECG shows AF with RVR. Please evaluate and manage.',
         48, 'cardio_doc'),
        
        ('MRN004', 'medicine', 'neuro', 'ROUTINE', 'COMPLETED',
         'Progressive weakness and visual disturbances. MRI shows demyelinating lesions. Please evaluate.',
         72, 'neuro_doc'),
        
        ('MRN006', 'medicine', 'ortho', 'ROUTINE', 'COMPLETED',
         'Post hip replacement day 3. Ready for rehab evaluation.',
         24, 'ortho_doc'),
        
        ('MRN008', 'emergency', 'medicine', 'URGENT', 'COMPLETED',
         'Community acquired pneumonia with hypoxia. Stabilized on BiPAP. Please assume care.',
         36, 'med_doc'),
        
        # More pending for overdue demonstration
        ('MRN011', 'emergency', 'cardio', 'URGENT', 'PENDING',
         'CHF exacerbation with pulmonary edema. Please evaluate urgently.',
         5, None),  # Will be overdue
         
        ('MRN012', 'emergency', 'cardio', 'ROUTINE', 'ACKNOWLEDGED',
         'Hypertensive crisis controlled with IV medication. Please assume ongoing management.',
         8, None),
    ]
    
    for mrn, from_dept, to_dept, urgency, status, reason, hours_ago, assigned_key in consults_data:
        try:
            patient = Patient.objects.get(mrn=mrn)
            from_department = departments.get(from_dept)
            to_department = departments.get(to_dept)
            
            if not from_department or not to_department:
                continue
            
            # Get requester (use ER doctor for emergency, med doctor for medicine)
            requester_key = f'{from_dept}_doc'
            if requester_key not in users:
                requester_key = 'emergency_doc'
            requester = users.get(requester_key)
            
            if not requester:
                continue
            
            assigned_to = users.get(assigned_key) if assigned_key else None
            
            created_time = now - timedelta(hours=hours_ago)
            
            consult = ConsultRequest(
                patient=patient,
                requester=requester,
                requesting_department=from_department,
                target_department=to_department,
                status=status,
                urgency=urgency,
                reason_for_consult=reason,
                clinical_question=f'Please evaluate and advise on management of {patient.primary_diagnosis}.',
                relevant_history=f'Patient is a {patient.age} year old {"male" if patient.gender == "M" else "female"} with {patient.primary_diagnosis}.',
                assigned_to=assigned_to,
            )
            
            # Manually set created_at by saving first then updating
            consult.save()
            ConsultRequest.objects.filter(pk=consult.pk).update(created_at=created_time)
            consult.refresh_from_db()
            
            # Update SLA and status timestamps
            if status == 'ACKNOWLEDGED':
                consult.acknowledged_at = created_time + timedelta(minutes=15)
                consult.save()
            elif status == 'IN_PROGRESS':
                consult.acknowledged_at = created_time + timedelta(minutes=10)
                consult.save()
            elif status == 'COMPLETED':
                consult.acknowledged_at = created_time + timedelta(minutes=10)
                consult.completed_at = now - timedelta(hours=1)
                consult.save()
                
                # Add completion note
                if assigned_to:
                    ConsultNote.objects.create(
                        consult=consult,
                        author=assigned_to,
                        note_type='FINAL',
                        content=f'Patient evaluated and management plan established. Follow-up as needed.',
                        recommendations='Continue current management. Follow up in clinic in 1 week.',
                        is_final=True
                    )
            
            print(f"✓ Consult created: {patient.name} - {urgency} {status} ({from_dept} → {to_dept})")
            
        except Exception as e:
            print(f"  Error creating consult for {mrn}: {e}")


def print_credentials_summary():
    """Print a summary of all demo credentials."""
    print("\n" + "="*60)
    print("DEMO CREDENTIALS SUMMARY")
    print("="*60)
    print("""
╔════════════════════════════════════════════════════════════╗
║  ROLE          │  EMAIL                    │  PASSWORD     ║
╠════════════════════════════════════════════════════════════╣
║  Superuser     │  admin@pmc.edu.pk         │  adminpassword123 ║
║  System Admin  │  sysadmin@pmc.edu.pk      │  password123  ║
╠════════════════════════════════════════════════════════════╣
║  CARDIOLOGY                                                 ║
║  HOD           │  cardio.hod@pmc.edu.pk    │  password123  ║
║  Professor     │  cardio.prof@pmc.edu.pk   │  password123  ║
║  Doctor        │  cardio.doc@pmc.edu.pk    │  password123  ║
╠════════════════════════════════════════════════════════════╣
║  NEUROLOGY                                                  ║
║  HOD           │  neuro.hod@pmc.edu.pk     │  password123  ║
║  Professor     │  neuro.prof@pmc.edu.pk    │  password123  ║
║  Doctor        │  neuro.doc@pmc.edu.pk     │  password123  ║
╠════════════════════════════════════════════════════════════╣
║  ORTHOPEDICS                                                ║
║  HOD           │  ortho.hod@pmc.edu.pk     │  password123  ║
║  Professor     │  ortho.prof@pmc.edu.pk    │  password123  ║
║  Doctor        │  ortho.doc@pmc.edu.pk     │  password123  ║
╠════════════════════════════════════════════════════════════╣
║  GENERAL MEDICINE                                           ║
║  HOD           │  med.hod@pmc.edu.pk       │  password123  ║
║  Professor     │  med.prof@pmc.edu.pk      │  password123  ║
║  Doctor        │  med.doc@pmc.edu.pk       │  password123  ║
╠════════════════════════════════════════════════════════════╣
║  EMERGENCY                                                  ║
║  HOD           │  er.hod@pmc.edu.pk        │  password123  ║
║  Professor     │  er.prof@pmc.edu.pk       │  password123  ║
║  Doctor        │  er.doc@pmc.edu.pk        │  password123  ║
╚════════════════════════════════════════════════════════════╝
    """)
    print("="*60 + "\n")


def create_data():
    """Main function to create all seed data."""
    print("\n" + "="*60)
    print("HOSPITAL CONSULT SYSTEM - DEMO DATA SETUP")
    print("="*60)
    
    # Create departments first
    departments = create_departments()
    
    # Create superuser
    superuser = create_superuser()
    
    # Create admin user
    admin = create_admin_user()
    
    # Create department users
    users = create_department_users(departments)
    
    # Create patients
    patients = create_patients(departments)
    
    # Create sample consults
    create_sample_consults(departments, users, patients)
    
    # Print summary
    print_credentials_summary()
    
    # Print statistics
    print("="*60)
    print("DATA SUMMARY")
    print("="*60)
    print(f"  Departments: {Department.objects.count()}")
    print(f"  Users: {User.objects.count()}")
    print(f"  Patients: {Patient.objects.count()}")
    print(f"  Consults: {ConsultRequest.objects.count()}")
    print(f"    - Pending: {ConsultRequest.objects.filter(status='PENDING').count()}")
    print(f"    - Acknowledged: {ConsultRequest.objects.filter(status='ACKNOWLEDGED').count()}")
    print(f"    - In Progress: {ConsultRequest.objects.filter(status='IN_PROGRESS').count()}")
    print(f"    - Completed: {ConsultRequest.objects.filter(status='COMPLETED').count()}")
    print(f"    - Overdue: {ConsultRequest.objects.filter(is_overdue=True).count()}")
    print("="*60)
    print("\nData setup completed successfully!")
    print("You can now login at http://localhost:3000/login")
    print("="*60 + "\n")


if __name__ == '__main__':
    create_data()
