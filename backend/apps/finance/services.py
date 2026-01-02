"""
Finance Service
Business logic for finance operations.
"""

from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .models import (
    FeeType, FeePlan, Voucher, VoucherItem, LedgerEntry,
    Payment, Adjustment, FinancePolicy
)
from apps.students.models import Student
from apps.academics.models import Program, Term


class FinanceService:
    """Encapsulates business logic for finance operations."""
    
    @staticmethod
    def generate_voucher_number():
        """Generate a unique voucher number."""
        today = timezone.now().date()
        date_str = today.strftime('%Y%m%d')
        
        last_voucher = Voucher.objects.filter(
            voucher_no__startswith=f'VCH-{date_str}-'
        ).order_by('-voucher_no').first()
        
        if last_voucher:
            try:
                last_num = int(last_voucher.voucher_no.split('-')[-1])
                next_num = last_num + 1
            except (ValueError, IndexError):
                next_num = 1
        else:
            next_num = 1
        
        return f'VCH-{date_str}-{next_num:04d}'
    
    @staticmethod
    def generate_receipt_number():
        """Generate a unique receipt number."""
        today = timezone.now().date()
        date_str = today.strftime('%Y%m%d')
        
        last_payment = Payment.objects.filter(
            receipt_no__startswith=f'RCP-{date_str}-'
        ).order_by('-receipt_no').first()
        
        if last_payment:
            try:
                last_num = int(last_payment.receipt_no.split('-')[-1])
                next_num = last_num + 1
            except (ValueError, IndexError):
                next_num = 1
        else:
            next_num = 1
        
        return f'RCP-{date_str}-{next_num:04d}'
    
    @staticmethod
    @transaction.atomic
    def create_voucher_from_feeplan(student, term, created_by, due_date, selected_fee_types=None):
        """Create a voucher from active fee plans for a student and term.
        
        Args:
            student: Student instance
            term: Term instance
            created_by: User creating the voucher
            due_date: Due date for the voucher
            selected_fee_types: Optional list of FeeType codes to include
        
        Returns:
            Voucher instance
        """
        # Get student's program
        if not student.program:
            raise ValueError(f"Student {student.student_id} has no program assigned")
        
        # Get active fee plans for program and term
        fee_plans = FeePlan.objects.filter(
            program=student.program,
            term=term,
            is_active=True
        )
        
        if selected_fee_types:
            fee_plans = fee_plans.filter(fee_type__code__in=selected_fee_types)
        
        if not fee_plans.exists():
            raise ValueError(f"No active fee plans found for {student.program.code} - {term.code}")
        
        # Check if voucher already exists
        existing_voucher = Voucher.objects.filter(
            student=student,
            term=term,
            status__in=['generated', 'partially_paid', 'overdue']
        ).first()
        
        if existing_voucher:
            raise ValueError(f"Active voucher already exists: {existing_voucher.voucher_no}")
        
        # Create voucher
        voucher = Voucher.objects.create(
            voucher_no=FinanceService.generate_voucher_number(),
            student=student,
            term=term,
            due_date=due_date,
            total_amount=Decimal('0.00'),  # Will be updated after items
            created_by=created_by
        )
        
        total_amount = Decimal('0.00')
        
        # Create voucher items and ledger debits
        for fee_plan in fee_plans:
            item = VoucherItem.objects.create(
                voucher=voucher,
                fee_type=fee_plan.fee_type,
                description=f"{fee_plan.fee_type.name} for {term.code}",
                amount=fee_plan.amount
            )
            total_amount += fee_plan.amount
            
            # Create ledger debit entry
            LedgerEntry.objects.create(
                student=student,
                term=term,
                entry_type='debit',
                amount=fee_plan.amount,
                reference_type='voucher',
                reference_id=str(voucher.id),
                description=f"Voucher {voucher.voucher_no} - {fee_plan.fee_type.name}",
                created_by=created_by
            )
        
        # Update voucher total
        voucher.total_amount = total_amount
        voucher.save()
        
        # Set initial status
        FinanceService.reconcile_voucher_status(voucher)
        
        return voucher
    
    @staticmethod
    @transaction.atomic
    def post_payment(student, term, amount, method, received_by, voucher=None, reference_no=None):
        """Record and verify a payment.
        
        Args:
            student: Student instance
            term: Term instance
            amount: Payment amount
            method: Payment method
            received_by: User receiving the payment
            voucher: Optional voucher to link
            reference_no: Optional bank reference number
        
        Returns:
            Payment instance
        """
        payment = Payment.objects.create(
            receipt_no=FinanceService.generate_receipt_number(),
            student=student,
            term=term,
            voucher=voucher,
            amount=amount,
            method=method,
            reference_no=reference_no or '',
            received_by=received_by,
            status='received'
        )
        
        # Auto-verify if received by finance/admin user
        if received_by.role in ['ADMIN', 'SUPER_ADMIN'] or received_by.is_superuser:
            FinanceService.verify_payment(payment.id, received_by)
        
        return payment
    
    @staticmethod
    @transaction.atomic
    def verify_payment(payment_id, verifier):
        """Verify a payment and create ledger credit entry.
        
        Args:
            payment_id: Payment ID
            verifier: User verifying the payment
        
        Returns:
            Payment instance
        """
        payment = Payment.objects.get(id=payment_id)
        
        if payment.status == 'verified':
            raise ValueError("Payment already verified")
        
        if payment.status == 'rejected':
            raise ValueError("Cannot verify a rejected payment")
        
        # Create ledger credit entry
        LedgerEntry.objects.create(
            student=payment.student,
            term=payment.term,
            entry_type='credit',
            amount=payment.amount,
            reference_type='payment',
            reference_id=str(payment.id),
            description=f"Payment {payment.receipt_no} - {payment.method}",
            created_by=verifier
        )
        
        # Update payment status
        payment.status = 'verified'
        payment.verified_by = verifier
        payment.verified_at = timezone.now()
        payment.save()
        
        # Reconcile voucher status if linked
        if payment.voucher:
            FinanceService.reconcile_voucher_status(payment.voucher)
        
        return payment
    
    @staticmethod
    @transaction.atomic
    def approve_adjustment(adjustment_id, approver):
        """Approve an adjustment and create ledger credit entry.
        
        Args:
            adjustment_id: Adjustment ID
            approver: User approving the adjustment
        
        Returns:
            Adjustment instance
        """
        adjustment = Adjustment.objects.get(id=adjustment_id)
        
        if adjustment.status == 'approved':
            raise ValueError("Adjustment already approved")
        
        if adjustment.status == 'rejected':
            raise ValueError("Cannot approve a rejected adjustment")
        
        # Create ledger credit entry
        LedgerEntry.objects.create(
            student=adjustment.student,
            term=adjustment.term,
            entry_type='credit',
            amount=adjustment.amount,
            reference_type=adjustment.kind,
            reference_id=str(adjustment.id),
            description=f"{adjustment.get_kind_display()}: {adjustment.reason}",
            created_by=approver
        )
        
        # Update adjustment status
        adjustment.status = 'approved'
        adjustment.approved_by = approver
        adjustment.approved_at = timezone.now()
        adjustment.save()
        
        return adjustment
    
    @staticmethod
    def compute_student_balance(student, term=None):
        """Compute student balance from ledger entries.
        
        Args:
            student: Student instance
            term: Optional term to filter by
        
        Returns:
            dict with 'total_debits', 'total_credits', 'outstanding'
        """
        queryset = LedgerEntry.objects.filter(
            student=student,
            voided_at__isnull=True
        )
        
        if term:
            queryset = queryset.filter(term=term)
        
        debits = queryset.filter(entry_type='debit').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        credits = queryset.filter(entry_type='credit').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        outstanding = max(Decimal('0.00'), debits - credits)
        
        return {
            'total_debits': debits,
            'total_credits': credits,
            'outstanding': outstanding
        }
    
    @staticmethod
    def reconcile_voucher_status(voucher):
        """Update voucher status based on ledger entries.
        
        Args:
            voucher: Voucher instance
        """
        paid_amount = voucher.get_paid_amount()
        outstanding = voucher.get_outstanding_amount()
        
        if outstanding <= Decimal('0.01'):
            voucher.status = 'paid'
        elif paid_amount > Decimal('0.00'):
            voucher.status = 'partially_paid'
        else:
            voucher.status = 'generated'
        
        # Check if overdue
        if voucher.due_date < timezone.now().date() and voucher.status != 'paid':
            voucher.status = 'overdue'
        
        voucher.save()
    
    @staticmethod
    def finance_gate_checks(student, term=None):
        """Check finance gating rules for a student.
        
        Args:
            student: Student instance
            term: Optional term to check
        
        Returns:
            dict with gating flags
        """
        balance_info = FinanceService.compute_student_balance(student, term)
        outstanding = balance_info['outstanding']
        
        # Get active policies
        policies = FinancePolicy.objects.filter(is_active=True)
        
        flags = {
            'can_sit_exam': True,
            'can_view_results': True,
            'can_generate_transcript': True,
            'can_enroll_next_term': True,
            'blocking_reasons': []
        }
        
        for policy in policies:
            # Check if policy applies
            if policy.fee_type_scope:
                # Check outstanding for specific fee type
                fee_outstanding = FinanceService.compute_fee_type_outstanding(
                    student, term, policy.fee_type_scope
                )
                if fee_outstanding >= policy.threshold_amount:
                    # Apply blocking rule
                    if policy.rule_key == 'BLOCK_EXAM_ELIGIBILITY_IF_TUITION_DUE':
                        flags['can_sit_exam'] = False
                        flags['blocking_reasons'].append(
                            f"Tuition fee outstanding: {fee_outstanding} PKR"
                        )
                    elif policy.rule_key == 'BLOCK_RESULTS_IF_EXAM_FEE_DUE':
                        flags['can_view_results'] = False
                        flags['blocking_reasons'].append(
                            f"Exam fee outstanding: {fee_outstanding} PKR"
                        )
            else:
                # Check total outstanding
                if outstanding >= policy.threshold_amount:
                    if policy.rule_key == 'BLOCK_TRANSCRIPT_IF_DUES':
                        flags['can_generate_transcript'] = False
                        flags['blocking_reasons'].append(
                            f"Outstanding dues: {outstanding} PKR"
                        )
                    elif policy.rule_key == 'BLOCK_ENROLLMENT_IF_DUES':
                        flags['can_enroll_next_term'] = False
                        flags['blocking_reasons'].append(
                            f"Outstanding dues: {outstanding} PKR"
                        )
        
        return flags
    
    @staticmethod
    def compute_fee_type_outstanding(student, term, fee_type):
        """Compute outstanding amount for a specific fee type.
        
        Args:
            student: Student instance
            term: Term instance
            fee_type: FeeType instance
        
        Returns:
            Decimal outstanding amount
        """
        # Get vouchers with this fee type
        vouchers = Voucher.objects.filter(
            student=student,
            term=term,
            status__in=['generated', 'partially_paid', 'overdue']
        )
        
        total_debit = Decimal('0.00')
        total_credit = Decimal('0.00')
        
        for voucher in vouchers:
            # Get items for this fee type
            items = voucher.items.filter(fee_type=fee_type)
            for item in items:
                total_debit += item.amount
            
            # Get payments linked to this voucher
            payments = Payment.objects.filter(
                voucher=voucher,
                status='verified'
            )
            # Allocate payment proportionally (simplified)
            if payments.exists():
                voucher_total = voucher.total_amount
                if voucher_total > 0:
                    payment_ratio = sum(p.amount for p in payments) / voucher_total
                    for item in items:
                        total_credit += item.amount * payment_ratio
        
        return max(Decimal('0.00'), total_debit - total_credit)
    
    @staticmethod
    @transaction.atomic
    def cancel_voucher(voucher_id, cancelled_by, reason):
        """Cancel a voucher by creating reversal entries.
        
        Args:
            voucher_id: Voucher ID
            cancelled_by: User cancelling the voucher
            reason: Cancellation reason
        
        Returns:
            Voucher instance
        """
        voucher = Voucher.objects.get(id=voucher_id)
        
        if voucher.status == 'cancelled':
            raise ValueError("Voucher already cancelled")
        
        if voucher.status == 'paid':
            raise ValueError("Cannot cancel a fully paid voucher")
        
        # Create reversal ledger entries for each item
        for item in voucher.items.all():
            # Create reversal debit (negative of original debit)
            LedgerEntry.objects.create(
                student=voucher.student,
                term=voucher.term,
                entry_type='debit',
                amount=item.amount,
                reference_type='reversal',
                reference_id=str(voucher.id),
                description=f"Reversal: Voucher {voucher.voucher_no} - {item.fee_type.name} - {reason}",
                created_by=cancelled_by
            )
        
        voucher.status = 'cancelled'
        voucher.notes = f"{voucher.notes}\nCancelled: {reason}".strip()
        voucher.save()
        
        return voucher
