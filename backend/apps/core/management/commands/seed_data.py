from django.core.management.base import BaseCommand
from django.db import transaction
from apps.accounts.models import User
from apps.departments.models import Department


class Command(BaseCommand):
    help = 'Seeds the database with initial data for departments and users.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))

        self._create_departments()
        self._create_users()

    def _create_departments(self):
        self.stdout.write('Creating departments...')
        departments_data = [
            {'name': 'Cardiology', 'code': 'CARD'},
            {'name': 'Neurology', 'code': 'NEURO'},
            {'name': 'Orthopedics', 'code': 'ORTHO'},
            {'name': 'General Surgery', 'code': 'GENSURG'},
            {'name': 'Pediatrics', 'code': 'PEDS'},
        ]

        for data in departments_data:
            Department.objects.get_or_create(code=data['code'], defaults=data)

        self.stdout.write(self.style.SUCCESS('Departments created.'))

    def _create_users(self):
        self.stdout.write('Creating users...')

        # Superuser
        if not User.objects.filter(email='superuser@pmc.edu.pk').exists():
            User.objects.create_superuser('superuser@pmc.edu.pk', 'password')

        # Admin
        admin, created = User.objects.get_or_create(
            email='admin@pmc.edu.pk',
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'ADMIN',
                'is_staff': True
            }
        )
        if created:
            admin.set_password('password')
            admin.save()

        # HODs
        cardiology = Department.objects.get(code='CARD')
        hod_cardiology, created = User.objects.get_or_create(
            email='hod.cardiology@pmc.edu.pk',
            defaults={
                'first_name': 'Head',
                'last_name': 'Cardiology',
                'designation': 'HOD',
                'department': cardiology
            }
        )
        if created:
            hod_cardiology.set_password('password')
            hod_cardiology.save()
        cardiology.head = hod_cardiology
        cardiology.save()

        neurology = Department.objects.get(code='NEURO')
        hod_neurology, created = User.objects.get_or_create(
            email='hod.neurology@pmc.edu.pk',
            defaults={
                'first_name': 'Head',
                'last_name': 'Neurology',
                'designation': 'HOD',
                'department': neurology
            }
        )
        if created:
            hod_neurology.set_password('password')
            hod_neurology.save()
        neurology.head = hod_neurology
        neurology.save()

        orthopedics = Department.objects.get(code='ORTHO')
        hod_orthopedics, created = User.objects.get_or_create(
            email='hod.orthopedics@pmc.edu.pk',
            defaults={
                'first_name': 'Head',
                'last_name': 'Orthopedics',
                'designation': 'HOD',
                'department': orthopedics
            }
        )
        if created:
            hod_orthopedics.set_password('password')
            hod_orthopedics.save()
        orthopedics.head = hod_orthopedics
        orthopedics.save()

        # Other users
        doctor, created = User.objects.get_or_create(
            email='doctor.cardiology@pmc.edu.pk',
            defaults={
                'first_name': 'Doctor',
                'last_name': 'Cardiology',
                'designation': 'RESIDENT_1',
                'department': cardiology
            }
        )
        if created:
            doctor.set_password('password')
            doctor.save()

        user, created = User.objects.get_or_create(
            email='user.neurology@pmc.edu.pk',
            defaults={
                'first_name': 'User',
                'last_name': 'Neurology',
                'designation': 'ASSISTANT_PROFESSOR',
                'department': neurology
            }
        )
        if created:
            user.set_password('password')
            user.save()

        self.stdout.write(self.style.SUCCESS('Users created.'))

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully.'))
