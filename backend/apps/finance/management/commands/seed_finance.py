"""
Management command to seed finance demo data.
"""

from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from apps.academics.models import Program, Term
from apps.students.models import Student
from apps.finance.models import FeeType, FeePlan, FinancePolicy
from apps.finance.services import FinanceService

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with finance demo data (programs, terms, students, fee plans, vouchers, payments).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--students',
            type=int,
            default=20,
            help='Number of students to create'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('FINANCE MODULE - DEMO DATA SETUP'))
        self.stdout.write(self.style.SUCCESS('='*60))

        num_students = options['students']
        
        # Create programs
        programs = self._create_programs()
        
        # Create terms
        terms = self._create_terms()
        
        # Create fee types
        fee_types = self._create_fee_types()
        
        # Create fee plans
        self._create_fee_plans(programs, terms, fee_types)
        
        # Create students
        students = self._create_students(programs, num_students)
        
        # Create finance user
        finance_user = self._create_finance_user()
        
        # Create finance policies
        self._create_finance_policies(fee_types)
        
        # Generate vouchers
        self._generate_vouchers(students, terms[0], finance_user)
        
        # Create payments
        self._create_payments(students, terms[0], finance_user)
        
        self._print_summary(programs, terms, students, fee_types)

    def _create_programs(self):
        """Create academic programs."""
        self.stdout.write('\n=== Creating Programs ===')
        
        programs = {}
        program_configs = [
            ('MBBS', 'Bachelor of Medicine and Bachelor of Surgery', 5),
            ('BDS', 'Bachelor of Dental Surgery', 4),
        ]
        
        for code, name, duration in program_configs:
            program, created = Program.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'duration_years': duration,
                    'is_active': True
                }
            )
            programs[code] = program
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f'  {status}: {code} - {name}')
        
        return programs

    def _create_terms(self):
        """Create academic terms."""
        self.stdout.write('\n=== Creating Terms ===')
        
        terms = []
        today = timezone.now().date()
        
        term_configs = [
            ('T1-2024', 'Term 1 - 2024', '2024-2025', today, today + timedelta(days=180)),
            ('T2-2024', 'Term 2 - 2024', '2024-2025', today + timedelta(days=180), today + timedelta(days=360)),
        ]
        
        for code, name, academic_year, start_date, end_date in term_configs:
            term, created = Term.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'academic_year': academic_year,
                    'start_date': start_date,
                    'end_date': end_date,
                    'is_active': True
                }
            )
            terms.append(term)
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f'  {status}: {code} - {academic_year}')
        
        return terms

    def _create_fee_types(self):
        """Create fee types."""
        self.stdout.write('\n=== Creating Fee Types ===')
        
        fee_types = {}
        fee_type_configs = [
            ('TUITION', 'Tuition Fee'),
            ('EXAM', 'Examination Fee'),
            ('LIBRARY', 'Library Fee'),
            ('ADMISSION', 'Admission Fee'),
            ('HOSTEL', 'Hostel Fee'),
            ('FINE', 'Fine'),
            ('MISC', 'Miscellaneous'),
        ]
        
        for code, name in fee_type_configs:
            fee_type, created = FeeType.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'is_active': True
                }
            )
            fee_types[code] = fee_type
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f'  {status}: {code} - {name}')
        
        return fee_types

    def _create_fee_plans(self, programs, terms, fee_types):
        """Create fee plans."""
        self.stdout.write('\n=== Creating Fee Plans ===')
        
        fee_plan_configs = [
            ('MBBS', 'T1-2024', 'TUITION', Decimal('50000.00')),
            ('MBBS', 'T1-2024', 'EXAM', Decimal('5000.00')),
            ('MBBS', 'T1-2024', 'LIBRARY', Decimal('2000.00')),
            ('MBBS', 'T2-2024', 'TUITION', Decimal('50000.00')),
            ('MBBS', 'T2-2024', 'EXAM', Decimal('5000.00')),
            ('MBBS', 'T2-2024', 'LIBRARY', Decimal('2000.00')),
            ('BDS', 'T1-2024', 'TUITION', Decimal('45000.00')),
            ('BDS', 'T1-2024', 'EXAM', Decimal('5000.00')),
            ('BDS', 'T1-2024', 'LIBRARY', Decimal('2000.00')),
        ]
        
        for program_code, term_code, fee_type_code, amount in fee_plan_configs:
            program = programs.get(program_code)
            term = Term.objects.get(code=term_code)
            fee_type = fee_types.get(fee_type_code)
            
            if not all([program, term, fee_type]):
                continue
            
            fee_plan, created = FeePlan.objects.get_or_create(
                program=program,
                term=term,
                fee_type=fee_type,
                defaults={
                    'amount': amount,
                    'is_mandatory': True,
                    'frequency': 'per_term',
                    'is_active': True
                }
            )
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f'  {status}: {program_code} - {term_code} - {fee_type_code}: {amount}')

    def _create_students(self, programs, num_students):
        """Create students."""
        self.stdout.write(f'\n=== Creating {num_students} Students ===')
        
        students = []
        mbbs = programs.get('MBBS')
        bds = programs.get('BDS')
        
        if not mbbs or not bds:
            self.stdout.write(self.style.WARNING('  Programs not found, skipping student creation'))
            return students
        
        # Get or create existing students
        existing_students = list(Student.objects.filter(is_active=True)[:num_students])
        
        if len(existing_students) >= num_students:
            students = existing_students[:num_students]
            self.stdout.write(f'  Using {len(students)} existing students')
            return students
        
        # Create new students
        for i in range(num_students - len(existing_students)):
            student_num = len(existing_students) + i + 1
            program = mbbs if i % 2 == 0 else bds
            
            student = Student.objects.create(
                student_id=f'STU-2024-{student_num:03d}',
                full_name=f'Student {student_num}',
                father_name=f'Father {student_num}',
                gender='M' if student_num % 2 == 0 else 'F',
                date_of_birth=timezone.now().date() - timedelta(days=365*20),
                cnic_or_bform=f'1234567890{student_num:03d}',
                mobile=f'0300{student_num:07d}',
                email=f'student{student_num}@test.com',
                address=f'Address {student_num}',
                program=program,
                is_active=True
            )
            students.append(student)
            self.stdout.write(self.style.SUCCESS(f'  ✓ Student created: {student.student_id}'))
        
        students.extend(existing_students)
        return students[:num_students]

    def _create_finance_user(self):
        """Create finance user."""
        self.stdout.write('\n=== Creating Finance User ===')
        
        if not User.objects.filter(email='finance@pmc.edu.pk').exists():
            user = User.objects.create_user(
                email='finance@pmc.edu.pk',
                username='finance',
                password='finance123',
                first_name='Finance',
                last_name='Manager',
                role='ADMIN',
                is_staff=True
            )
            self.stdout.write(self.style.SUCCESS('  ✓ Finance user created: finance@pmc.edu.pk'))
            return user
        else:
            self.stdout.write('  Finance user already exists: finance@pmc.edu.pk')
            return User.objects.get(email='finance@pmc.edu.pk')

    def _create_finance_policies(self, fee_types):
        """Create finance policies."""
        self.stdout.write('\n=== Creating Finance Policies ===')
        
        policies = [
            ('BLOCK_TRANSCRIPT_IF_DUES', Decimal('0.01'), None, 'Block transcript generation if any outstanding dues'),
            ('BLOCK_RESULTS_IF_EXAM_FEE_DUE', Decimal('0.01'), 'EXAM', 'Block results view if exam fee outstanding'),
        ]
        
        for rule_key, threshold, fee_type_code, description in policies:
            fee_type = fee_types.get(fee_type_code) if fee_type_code else None
            
            policy, created = FinancePolicy.objects.get_or_create(
                rule_key=rule_key,
                defaults={
                    'threshold_amount': threshold,
                    'fee_type_scope': fee_type,
                    'is_active': True,
                    'description': description
                }
            )
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f'  {status}: {rule_key}')

    def _generate_vouchers(self, students, term, created_by):
        """Generate vouchers for students."""
        self.stdout.write(f'\n=== Generating Vouchers for {len(students)} Students ===')
        
        due_date = timezone.now().date() + timedelta(days=30)
        created_count = 0
        skipped_count = 0
        
        for student in students:
            try:
                voucher = FinanceService.create_voucher_from_feeplan(
                    student=student,
                    term=term,
                    created_by=created_by,
                    due_date=due_date
                )
                created_count += 1
                if created_count <= 5:  # Only print first 5
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Voucher created: {voucher.voucher_no}'))
            except ValueError as e:
                skipped_count += 1
                if skipped_count <= 5:
                    self.stdout.write(self.style.WARNING(f'  ⚠ Skipped: {student.student_id} - {str(e)}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Error: {student.student_id} - {str(e)}'))
        
        self.stdout.write(f'  Created: {created_count}, Skipped: {skipped_count}')

    def _create_payments(self, students, term, received_by):
        """Create payments for students."""
        self.stdout.write(f'\n=== Creating Payments ===')
        
        from apps.finance.models import Voucher, Payment
        
        vouchers = Voucher.objects.filter(
            student__in=students,
            term=term,
            status__in=['generated', 'partially_paid', 'overdue']
        )[:len(students)]
        
        # Make 10 fully paid, 5 partially paid, rest unpaid
        fully_paid = vouchers[:10] if len(vouchers) >= 10 else vouchers[:len(vouchers)//2]
        partially_paid = vouchers[10:15] if len(vouchers) >= 15 else []
        
        payment_count = 0
        
        # Fully paid
        for voucher in fully_paid:
            try:
                payment = FinanceService.post_payment(
                    student=voucher.student,
                    term=term,
                    amount=voucher.total_amount,
                    method='cash',
                    received_by=received_by,
                    voucher=voucher
                )
                payment_count += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  Error creating payment: {e}'))
        
        # Partially paid
        for voucher in partially_paid:
            try:
                payment = FinanceService.post_payment(
                    student=voucher.student,
                    term=term,
                    amount=voucher.total_amount * Decimal('0.5'),  # 50% payment
                    method='bank_transfer',
                    received_by=received_by,
                    voucher=voucher
                )
                payment_count += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  Error creating payment: {e}'))
        
        self.stdout.write(f'  Created {payment_count} payments')

    def _print_summary(self, programs, terms, students, fee_types):
        """Print summary."""
        from apps.finance.models import Voucher, Payment, LedgerEntry
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write('FINANCE DATA SUMMARY')
        self.stdout.write('='*60)
        self.stdout.write(f'  Programs: {len(programs)}')
        self.stdout.write(f'  Terms: {len(terms)}')
        self.stdout.write(f'  Fee Types: {len(fee_types)}')
        self.stdout.write(f'  Students: {len(students)}')
        self.stdout.write(f'  Vouchers: {Voucher.objects.count()}')
        self.stdout.write(f'    - Paid: {Voucher.objects.filter(status="paid").count()}')
        self.stdout.write(f'    - Partially Paid: {Voucher.objects.filter(status="partially_paid").count()}')
        self.stdout.write(f'    - Overdue: {Voucher.objects.filter(status="overdue").count()}')
        self.stdout.write(f'  Payments: {Payment.objects.count()}')
        self.stdout.write(f'  Ledger Entries: {LedgerEntry.objects.count()}')
        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS('\nFinance demo data seeding completed successfully!'))
        self.stdout.write('\nDemo Credentials:')
        self.stdout.write('  Finance User: finance@pmc.edu.pk / finance123')
        self.stdout.write('  Admin: admin@pmc.edu.pk / adminpassword123')
