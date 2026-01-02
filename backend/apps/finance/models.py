"""
Finance models for SIMS - Fee management, vouchers, payments, and ledger.
"""

import uuid
from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Sum, Q

User = get_user_model()


class FeeType(models.Model):
    """Reference table for fee types (Tuition, Exam, Library, etc.)."""
    
    code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fee_types'
        ordering = ['code']
        verbose_name = 'Fee Type'
        verbose_name_plural = 'Fee Types'
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class FeePlan(models.Model):
    """Defines fee structure for a program and term."""
    
    FREQUENCY_CHOICES = [
        ('one_time', 'One Time'),
        ('per_term', 'Per Term'),
    ]
    
    program = models.ForeignKey(
        'academics.Program',
        on_delete=models.CASCADE,
        related_name='fee_plans'
    )
    term = models.ForeignKey(
        'academics.Term',
        on_delete=models.CASCADE,
        related_name='fee_plans'
    )
    fee_type = models.ForeignKey(
        FeeType,
        on_delete=models.PROTECT,
        related_name='fee_plans'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_mandatory = models.BooleanField(default=True)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='per_term')
    effective_from = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fee_plans'
        unique_together = [['program', 'term', 'fee_type']]
        indexes = [
            models.Index(fields=['program', 'term', 'is_active']),
            models.Index(fields=['fee_type', 'is_active']),
        ]
        verbose_name = 'Fee Plan'
        verbose_name_plural = 'Fee Plans'
    
    def __str__(self):
        return f"{self.program.code} - {self.term.code} - {self.fee_type.code}: {self.amount}"


class Voucher(models.Model):
    """Human-facing payment request document."""
    
    STATUS_CHOICES = [
        ('generated', 'Generated'),
        ('partially_paid', 'Partially Paid'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    voucher_no = models.CharField(max_length=50, unique=True, db_index=True)
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.PROTECT,
        related_name='vouchers'
    )
    term = models.ForeignKey(
        'academics.Term',
        on_delete=models.PROTECT,
        related_name='vouchers'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='generated')
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_vouchers'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'vouchers'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['voucher_no']),
            models.Index(fields=['student', 'term', 'status']),
            models.Index(fields=['status', 'due_date']),
        ]
        verbose_name = 'Voucher'
        verbose_name_plural = 'Vouchers'
    
    def __str__(self):
        return f"{self.voucher_no} - {self.student.full_name} - {self.total_amount}"
    
    def clean(self):
        """Validate that total_amount matches sum of items."""
        if self.pk:
            items_total = self.items.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            if abs(self.total_amount - items_total) > Decimal('0.01'):
                raise ValidationError({
                    'total_amount': f'Total amount ({self.total_amount}) does not match sum of items ({items_total})'
                })
    
    def get_paid_amount(self):
        """Calculate total paid amount from ledger entries."""
        from .models import LedgerEntry
        return LedgerEntry.objects.filter(
            student=self.student,
            term=self.term,
            entry_type='credit',
            reference_type='payment',
            reference_id=str(self.id)
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    def get_outstanding_amount(self):
        """Calculate outstanding amount."""
        return max(Decimal('0.00'), self.total_amount - self.get_paid_amount())


class VoucherItem(models.Model):
    """Line items on a voucher."""
    
    voucher = models.ForeignKey(
        Voucher,
        on_delete=models.CASCADE,
        related_name='items'
    )
    fee_type = models.ForeignKey(
        FeeType,
        on_delete=models.PROTECT,
        related_name='voucher_items'
    )
    description = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'voucher_items'
        ordering = ['id']
        verbose_name = 'Voucher Item'
        verbose_name_plural = 'Voucher Items'
    
    def __str__(self):
        return f"{self.voucher.voucher_no} - {self.fee_type.code}: {self.amount}"


class LedgerEntry(models.Model):
    """Source of truth for all financial transactions."""
    
    ENTRY_TYPE_CHOICES = [
        ('debit', 'Debit'),
        ('credit', 'Credit'),
    ]
    
    REFERENCE_TYPE_CHOICES = [
        ('voucher', 'Voucher'),
        ('payment', 'Payment'),
        ('adjustment', 'Adjustment'),
        ('waiver', 'Waiver'),
        ('scholarship', 'Scholarship'),
        ('reversal', 'Reversal'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.PROTECT,
        related_name='ledger_entries'
    )
    term = models.ForeignKey(
        'academics.Term',
        on_delete=models.PROTECT,
        related_name='ledger_entries'
    )
    entry_type = models.CharField(max_length=10, choices=ENTRY_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='PKR')
    reference_type = models.CharField(max_length=20, choices=REFERENCE_TYPE_CHOICES)
    reference_id = models.CharField(max_length=100, db_index=True)
    description = models.TextField()
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_ledger_entries'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    voided_at = models.DateTimeField(null=True, blank=True)
    void_reason = models.TextField(blank=True)
    
    class Meta:
        db_table = 'ledger_entries'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'term', 'entry_type']),
            models.Index(fields=['reference_type', 'reference_id']),
            models.Index(fields=['created_at']),
        ]
        verbose_name = 'Ledger Entry'
        verbose_name_plural = 'Ledger Entries'
    
    def __str__(self):
        return f"{self.student.student_id} - {self.entry_type} - {self.amount} - {self.reference_type}"


class Payment(models.Model):
    """Payment record."""
    
    METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('online', 'Online Payment'),
        ('scholarship', 'Scholarship'),
        ('waiver', 'Waiver'),
    ]
    
    STATUS_CHOICES = [
        ('received', 'Received'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    
    receipt_no = models.CharField(max_length=50, unique=True, db_index=True)
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.PROTECT,
        related_name='payments'
    )
    term = models.ForeignKey(
        'academics.Term',
        on_delete=models.PROTECT,
        related_name='payments'
    )
    voucher = models.ForeignKey(
        Voucher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    reference_no = models.CharField(max_length=100, blank=True, help_text='Bank reference number')
    received_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='received_payments'
    )
    received_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='received')
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_payments'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['receipt_no']),
            models.Index(fields=['student', 'term', 'status']),
            models.Index(fields=['status', 'received_at']),
        ]
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
    
    def __str__(self):
        return f"{self.receipt_no} - {self.student.full_name} - {self.amount}"


class Adjustment(models.Model):
    """Waiver, scholarship, or other adjustment."""
    
    KIND_CHOICES = [
        ('waiver', 'Waiver'),
        ('scholarship', 'Scholarship'),
        ('adjustment', 'Adjustment'),
        ('fine_reversal', 'Fine Reversal'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.PROTECT,
        related_name='adjustments'
    )
    term = models.ForeignKey(
        'academics.Term',
        on_delete=models.PROTECT,
        related_name='adjustments'
    )
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField()
    requested_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='requested_adjustments'
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_adjustments'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'adjustments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'term', 'status']),
            models.Index(fields=['status', 'kind']),
        ]
        verbose_name = 'Adjustment'
        verbose_name_plural = 'Adjustments'
    
    def __str__(self):
        return f"{self.student.student_id} - {self.kind} - {self.amount} - {self.status}"


class FinancePolicy(models.Model):
    """Finance gating rules."""
    
    RULE_KEY_CHOICES = [
        ('BLOCK_TRANSCRIPT_IF_DUES', 'Block Transcript if Outstanding Dues'),
        ('BLOCK_RESULTS_IF_EXAM_FEE_DUE', 'Block Results if Exam Fee Due'),
        ('BLOCK_EXAM_ELIGIBILITY_IF_TUITION_DUE', 'Block Exam Eligibility if Tuition Due'),
        ('BLOCK_ENROLLMENT_IF_DUES', 'Block Enrollment if Outstanding Dues'),
    ]
    
    rule_key = models.CharField(max_length=100, choices=RULE_KEY_CHOICES, unique=True)
    threshold_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.01'),
        help_text='Minimum outstanding amount to trigger the rule'
    )
    fee_type_scope = models.ForeignKey(
        FeeType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='If set, rule applies only to this fee type'
    )
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'finance_policies'
        verbose_name = 'Finance Policy'
        verbose_name_plural = 'Finance Policies'
    
    def __str__(self):
        return f"{self.get_rule_key_display()} (Threshold: {self.threshold_amount})"
