"""
Tests for Finance app.
"""

from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from apps.students.models import Student
from apps.academics.models import Program, Term
from apps.finance.models import (
    FeeType, FeePlan, Voucher, VoucherItem, LedgerEntry,
    Payment, Adjustment, FinancePolicy
)
from apps.finance.services import FinanceService

User = get_user_model()


class FinanceModelsTestCase(TestCase):
    """Test finance models."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='finance@pmc.edu.pk',
            password='testpass123',
            first_name='Finance',
            last_name='User',
            role='ADMIN'
        )
        
        self.program = Program.objects.create(
            code='MBBS',
            name='Bachelor of Medicine and Bachelor of Surgery',
            duration_years=5
        )
        
        self.term = Term.objects.create(
            code='T1-2024',
            name='Term 1 - 2024',
            academic_year='2024-2025',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=180)
        )
        
        self.student = Student.objects.create(
            student_id='STU-2024-001',
            full_name='Test Student',
            father_name='Test Father',
            gender='M',
            date_of_birth=timezone.now().date() - timedelta(days=365*20),
            cnic_or_bform='1234567890123',
            mobile='03001234567',
            email='student@test.com',
            address='Test Address',
            program=self.program
        )
        
        self.fee_type = FeeType.objects.create(
            code='TUITION',
            name='Tuition Fee'
        )
    
    def test_fee_type_creation(self):
        """Test FeeType creation."""
        fee_type = FeeType.objects.create(
            code='EXAM',
            name='Examination Fee'
        )
        self.assertEqual(fee_type.code, 'EXAM')
        self.assertTrue(fee_type.is_active)
    
    def test_fee_plan_creation(self):
        """Test FeePlan creation."""
        fee_plan = FeePlan.objects.create(
            program=self.program,
            term=self.term,
            fee_type=self.fee_type,
            amount=Decimal('50000.00')
        )
        self.assertEqual(fee_plan.amount, Decimal('50000.00'))
        self.assertTrue(fee_plan.is_mandatory)
    
    def test_voucher_creation(self):
        """Test Voucher creation."""
        voucher = Voucher.objects.create(
            voucher_no='VCH-20240101-0001',
            student=self.student,
            term=self.term,
            due_date=timezone.now().date() + timedelta(days=30),
            total_amount=Decimal('50000.00'),
            created_by=self.user
        )
        self.assertEqual(voucher.status, 'generated')
        self.assertEqual(voucher.total_amount, Decimal('50000.00'))


class FinanceServiceTestCase(TestCase):
    """Test finance services."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='finance@pmc.edu.pk',
            password='testpass123',
            first_name='Finance',
            last_name='User',
            role='ADMIN'
        )
        
        self.program = Program.objects.create(
            code='MBBS',
            name='Bachelor of Medicine and Bachelor of Surgery',
            duration_years=5
        )
        
        self.term = Term.objects.create(
            code='T1-2024',
            name='Term 1 - 2024',
            academic_year='2024-2025',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=180)
        )
        
        self.student = Student.objects.create(
            student_id='STU-2024-001',
            full_name='Test Student',
            father_name='Test Father',
            gender='M',
            date_of_birth=timezone.now().date() - timedelta(days=365*20),
            cnic_or_bform='1234567890123',
            mobile='03001234567',
            email='student@test.com',
            address='Test Address',
            program=self.program
        )
        
        self.fee_type = FeeType.objects.create(
            code='TUITION',
            name='Tuition Fee'
        )
        
        self.fee_plan = FeePlan.objects.create(
            program=self.program,
            term=self.term,
            fee_type=self.fee_type,
            amount=Decimal('50000.00')
        )
    
    def test_create_voucher_from_feeplan(self):
        """Test voucher creation from fee plan."""
        due_date = timezone.now().date() + timedelta(days=30)
        
        voucher = FinanceService.create_voucher_from_feeplan(
            student=self.student,
            term=self.term,
            created_by=self.user,
            due_date=due_date
        )
        
        self.assertIsNotNone(voucher)
        self.assertEqual(voucher.student, self.student)
        self.assertEqual(voucher.term, self.term)
        self.assertEqual(voucher.total_amount, Decimal('50000.00'))
        self.assertEqual(voucher.items.count(), 1)
        
        # Check ledger entry created
        ledger_entry = LedgerEntry.objects.filter(
            student=self.student,
            term=self.term,
            reference_type='voucher',
            reference_id=str(voucher.id)
        ).first()
        self.assertIsNotNone(ledger_entry)
        self.assertEqual(ledger_entry.entry_type, 'debit')
        self.assertEqual(ledger_entry.amount, Decimal('50000.00'))
    
    def test_post_payment(self):
        """Test payment posting."""
        # First create a voucher
        due_date = timezone.now().date() + timedelta(days=30)
        voucher = FinanceService.create_voucher_from_feeplan(
            student=self.student,
            term=self.term,
            created_by=self.user,
            due_date=due_date
        )
        
        # Post payment
        payment = FinanceService.post_payment(
            student=self.student,
            term=self.term,
            amount=Decimal('50000.00'),
            method='cash',
            received_by=self.user,
            voucher=voucher
        )
        
        self.assertIsNotNone(payment)
        self.assertEqual(payment.amount, Decimal('50000.00'))
        self.assertEqual(payment.status, 'verified')  # Auto-verified for admin
        
        # Check ledger entry created
        ledger_entry = LedgerEntry.objects.filter(
            student=self.student,
            term=self.term,
            reference_type='payment',
            reference_id=str(payment.id)
        ).first()
        self.assertIsNotNone(ledger_entry)
        self.assertEqual(ledger_entry.entry_type, 'credit')
        self.assertEqual(ledger_entry.amount, Decimal('50000.00'))
    
    def test_compute_student_balance(self):
        """Test balance computation."""
        # Create voucher (debit)
        due_date = timezone.now().date() + timedelta(days=30)
        voucher = FinanceService.create_voucher_from_feeplan(
            student=self.student,
            term=self.term,
            created_by=self.user,
            due_date=due_date
        )
        
        # Post payment (credit)
        payment = FinanceService.post_payment(
            student=self.student,
            term=self.term,
            amount=Decimal('30000.00'),
            method='cash',
            received_by=self.user,
            voucher=voucher
        )
        
        # Compute balance
        balance_info = FinanceService.compute_student_balance(self.student, self.term)
        
        self.assertEqual(balance_info['total_debits'], Decimal('50000.00'))
        self.assertEqual(balance_info['total_credits'], Decimal('30000.00'))
        self.assertEqual(balance_info['outstanding'], Decimal('20000.00'))
    
    def test_finance_gate_checks(self):
        """Test finance gating."""
        # Create policy
        policy = FinancePolicy.objects.create(
            rule_key='BLOCK_TRANSCRIPT_IF_DUES',
            threshold_amount=Decimal('0.01'),
            is_active=True
        )
        
        # Create voucher with outstanding
        due_date = timezone.now().date() + timedelta(days=30)
        voucher = FinanceService.create_voucher_from_feeplan(
            student=self.student,
            term=self.term,
            created_by=self.user,
            due_date=due_date
        )
        
        # Check gating
        flags = FinanceService.finance_gate_checks(self.student, self.term)
        
        self.assertFalse(flags['can_generate_transcript'])
        self.assertTrue(len(flags['blocking_reasons']) > 0)
