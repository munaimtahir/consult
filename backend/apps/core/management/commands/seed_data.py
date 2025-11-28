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
        User.objects.create_superuser('superuser@pmc.edu.pk', 'password')

        # Admin
        User.objects.create_user(
            email='admin@pmc.edu.pk',
            password='password',
            first_name='Admin',
            last_name='User',
            role='ADMIN',
            is_staff=True
        )

        # HODs
        cardiology = Department.objects.get(code='CARD')
        hod_cardiology = User.objects.create_user(
            email='hod.cardiology@pmc.edu.pk',
            password='password',
            first_name='Head',
            last_name='Cardiology',
            designation='HOD',
            department=cardiology
        )
        cardiology.head = hod_cardiology
        cardiology.save()

        neurology = Department.objects.get(code='NEURO')
        hod_neurology = User.objects.create_user(
            email='hod.neurology@pmc.edu.pk',
            password='password',
            first_name='Head',
            last_name='Neurology',
            designation='HOD',
            department=neurology
        )
        neurology.head = hod_neurology
        neurology.save()

        orthopedics = Department.objects.get(code='ORTHO')
        hod_orthopedics = User.objects.create_user(
            email='hod.orthopedics@pmc.edu.pk',
            password='password',
            first_name='Head',
            last_name='Orthopedics',
            designation='HOD',
            department=orthopedics
        )
        orthopedics.head = hod_orthopedics
        orthopedics.save()

        # Other users
        User.objects.create_user(
            email='doctor.cardiology@pmc.edu.pk',
            password='password',
            first_name='Doctor',
            last_name='Cardiology',
            designation='RESIDENT_1',
            department=cardiology
        )

        User.objects.create_user(
            email='user.neurology@pmc.edu.pk',
            password='password',
            first_name='User',
            last_name='Neurology',
            designation='ASSISTANT_PROFESSOR',
            department=neurology
        )

        self.stdout.write(self.style.SUCCESS('Users created.'))

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully.'))
