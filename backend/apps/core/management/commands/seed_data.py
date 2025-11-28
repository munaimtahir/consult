"""
Management command to seed the database with demo data.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from apps.departments.models import Department
from apps.patients.models import Patient
from apps.consults.models import ConsultRequest, ConsultNote

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with comprehensive demo data for departments, users, patients, and consults.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('HOSPITAL CONSULT SYSTEM - DEMO DATA SETUP'))
        self.stdout.write(self.style.SUCCESS('='*60))

        departments = self._create_departments()
        superuser = self._create_superuser()
        admin = self._create_admin_user()
        users = self._create_department_users(departments)
        patients = self._create_patients(departments)
        self._create_sample_consults(departments, users, patients)
        
        self._print_summary()
        self._print_credentials()

    def _create_departments(self):
        """Create departments with SLA configuration."""
        self.stdout.write('\n=== Creating Departments ===')
        
        departments = {}
        
        dept_configs = [
            ('Cardiology', 'CARDIO', '101', 30, 120, 1440),
            ('Neurology', 'NEURO', '102', 15, 60, 720),
            ('Orthopedics', 'ORTHO', '103', 60, 240, 1440),
            ('General Medicine', 'MED', '104', 60, 180, 1440),
            ('Emergency', 'ER', '100', 10, 30, 60),
        ]
        
        for name, code, contact, emergency_sla, urgent_sla, routine_sla in dept_configs:
            dept, created = Department.objects.get_or_create(
                name=name,
                defaults={
                    'code': code,
                    'contact_number': contact,
                    'department_type': 'CLINICAL',
                    'emergency_sla': emergency_sla,
                    'urgent_sla': urgent_sla,
                    'routine_sla': routine_sla,
                }
            )
            key = code.lower().replace('med', 'medicine').replace('er', 'emergency')
            if key == 'med':
                key = 'medicine'
            elif key == 'er':
                key = 'emergency'
            departments[key] = dept
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f'  {status}: {name}')
        
        return departments

    def _create_superuser(self):
        """Create superuser account."""
        self.stdout.write('\n=== Creating Superuser ===')
        
        if not User.objects.filter(email='admin@pmc.edu.pk').exists():
            user = User.objects.create_superuser(
                email='admin@pmc.edu.pk',
                username='admin',
                password='adminpassword123',
                first_name='Super',
                last_name='Admin'
            )
            self.stdout.write(self.style.SUCCESS('  ✓ Superuser created: admin@pmc.edu.pk'))
            return user
        else:
            self.stdout.write('  Superuser already exists: admin@pmc.edu.pk')
            return User.objects.get(email='admin@pmc.edu.pk')

    def _create_admin_user(self):
        """Create system admin user with all permissions."""
        self.stdout.write('\n=== Creating Admin User ===')
        
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
            self.stdout.write(self.style.SUCCESS('  ✓ Admin user created: sysadmin@pmc.edu.pk'))
            return user
        else:
            self.stdout.write('  Admin user already exists: sysadmin@pmc.edu.pk')
            return User.objects.get(email='sysadmin@pmc.edu.pk')

    def _create_department_users(self, departments):
        """Create HOD, Professor, and Doctor for each department."""
        self.stdout.write('\n=== Creating Department Users ===')
        
        users = {}
        
        dept_configs = [
            ('cardio', 'Dr. Ahmed', 'Khan', 'Dr. Sarah', 'Ali', 'Dr. Omar', 'Hassan'),
            ('neuro', 'Dr. Fatima', 'Malik', 'Dr. Bilal', 'Sheikh', 'Dr. Zara', 'Ahmed'),
            ('ortho', 'Dr. Imran', 'Qureshi', 'Dr. Ayesha', 'Mirza', 'Dr. Usman', 'Raza'),
            ('medicine', 'Dr. Rashid', 'Butt', 'Dr. Saima', 'Farooq', 'Dr. Kamran', 'Siddiqui'),
            ('emergency', 'Dr. Tariq', 'Mehmood', 'Dr. Nadia', 'Iqbal', 'Dr. Asif', 'Javed'),
        ]
        
        for dept_key, hod_first, hod_last, prof_first, prof_last, doc_first, doc_last in dept_configs:
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
                )
                dept.head = hod
                dept.save()
                self.stdout.write(self.style.SUCCESS(f'  ✓ HOD created: {hod_email}'))
            else:
                hod = User.objects.get(email=hod_email)
            users[f'{dept_key}_hod'] = hod
            
            # Create Professor
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
                self.stdout.write(self.style.SUCCESS(f'  ✓ Professor created: {prof_email}'))
            else:
                prof = User.objects.get(email=prof_email)
            users[f'{dept_key}_prof'] = prof
            
            # Create Doctor
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
                self.stdout.write(self.style.SUCCESS(f'  ✓ Doctor created: {doc_email}'))
            else:
                doc = User.objects.get(email=doc_email)
            users[f'{dept_key}_doc'] = doc
        
        return users

    def _create_patients(self, departments):
        """Create sample patients for demo."""
        self.stdout.write('\n=== Creating Patients ===')
        
        patients = []
        
        patient_data = [
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
                self.stdout.write(self.style.SUCCESS(f'  ✓ Patient created: {name} ({mrn})'))
            else:
                patient = Patient.objects.get(mrn=mrn)
            patients.append(patient)
        
        return patients

    def _create_sample_consults(self, departments, users, patients):
        """Create sample consult requests at various workflow stages."""
        self.stdout.write('\n=== Creating Sample Consults ===')
        
        if ConsultRequest.objects.count() > 0:
            self.stdout.write('  Sample consults already exist, skipping...')
            return
        
        now = timezone.now()
        
        consults_data = [
            ('MRN009', 'emergency', 'cardio', 'EMERGENCY', 'PENDING', 
             'Patient presenting with chest pain, elevated troponins. Please evaluate urgently for possible STEMI.', 
             0.5, None),
            ('MRN010', 'emergency', 'neuro', 'EMERGENCY', 'PENDING',
             'Severe headache with neck stiffness. CT pending. Please evaluate for possible subarachnoid hemorrhage.',
             0.25, None),
            ('MRN001', 'emergency', 'cardio', 'URGENT', 'ACKNOWLEDGED',
             'Known CAD patient with worsening angina. Please evaluate for cardiac catheterization.',
             2, None),
            ('MRN003', 'emergency', 'neuro', 'EMERGENCY', 'IN_PROGRESS',
             'Acute stroke symptoms. tPA administered. Please assume care for post-thrombolysis monitoring.',
             4, 'neuro_doc'),
            ('MRN005', 'emergency', 'ortho', 'URGENT', 'IN_PROGRESS',
             'Compound fracture right tibia from motor vehicle accident. Please evaluate for surgical fixation.',
             6, 'ortho_doc'),
            ('MRN007', 'emergency', 'medicine', 'URGENT', 'IN_PROGRESS',
             'DKA with altered mental status. Currently stabilizing in ER. Please assume care.',
             3, 'medicine_doc'),
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
             36, 'medicine_doc'),
            ('MRN011', 'emergency', 'cardio', 'URGENT', 'PENDING',
             'CHF exacerbation with pulmonary edema. Please evaluate urgently.',
             5, None),
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
                
                consult.save()
                ConsultRequest.objects.filter(pk=consult.pk).update(created_at=created_time)
                consult.refresh_from_db()
                
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
                    
                    if assigned_to:
                        ConsultNote.objects.create(
                            consult=consult,
                            author=assigned_to,
                            note_type='FINAL',
                            content='Patient evaluated and management plan established. Follow-up as needed.',
                            recommendations='Continue current management. Follow up in clinic in 1 week.',
                            is_final=True
                        )
                
                self.stdout.write(self.style.SUCCESS(
                    f'  ✓ Consult created: {patient.name} - {urgency} {status}'
                ))
                
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  Error creating consult for {mrn}: {e}'))

    def _print_summary(self):
        """Print data summary."""
        self.stdout.write('\n' + '='*60)
        self.stdout.write('DATA SUMMARY')
        self.stdout.write('='*60)
        self.stdout.write(f'  Departments: {Department.objects.count()}')
        self.stdout.write(f'  Users: {User.objects.count()}')
        self.stdout.write(f'  Patients: {Patient.objects.count()}')
        self.stdout.write(f'  Consults: {ConsultRequest.objects.count()}')
        self.stdout.write(f'    - Pending: {ConsultRequest.objects.filter(status="PENDING").count()}')
        self.stdout.write(f'    - Acknowledged: {ConsultRequest.objects.filter(status="ACKNOWLEDGED").count()}')
        self.stdout.write(f'    - In Progress: {ConsultRequest.objects.filter(status="IN_PROGRESS").count()}')
        self.stdout.write(f'    - Completed: {ConsultRequest.objects.filter(status="COMPLETED").count()}')

    def _print_credentials(self):
        """Print credentials summary."""
        self.stdout.write('\n' + '='*60)
        self.stdout.write('DEMO CREDENTIALS')
        self.stdout.write('='*60)
        self.stdout.write('  Superuser: admin@pmc.edu.pk / adminpassword123')
        self.stdout.write('  Admin: sysadmin@pmc.edu.pk / password123')
        self.stdout.write('  All other users: [dept].hod|prof|doc@pmc.edu.pk / password123')
        self.stdout.write('  Example: cardio.hod@pmc.edu.pk, neuro.doc@pmc.edu.pk')
        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS('\nDatabase seeding completed successfully!'))
