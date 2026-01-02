"""
Serializers for Finance app.
"""

from rest_framework import serializers
from .models import (
    FeeType, FeePlan, Voucher, VoucherItem, LedgerEntry,
    Payment, Adjustment, FinancePolicy
)
from apps.students.serializers import StudentSerializer
from apps.academics.serializers import ProgramSerializer, TermSerializer


class FeeTypeSerializer(serializers.ModelSerializer):
    """Serializer for FeeType."""
    
    class Meta:
        model = FeeType
        fields = ['id', 'code', 'name', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class FeePlanSerializer(serializers.ModelSerializer):
    """Serializer for FeePlan."""
    
    program_name = serializers.CharField(source='program.name', read_only=True)
    program_code = serializers.CharField(source='program.code', read_only=True)
    term_name = serializers.CharField(source='term.name', read_only=True)
    term_code = serializers.CharField(source='term.code', read_only=True)
    fee_type_name = serializers.CharField(source='fee_type.name', read_only=True)
    fee_type_code = serializers.CharField(source='fee_type.code', read_only=True)
    
    class Meta:
        model = FeePlan
        fields = [
            'id', 'program', 'program_name', 'program_code',
            'term', 'term_name', 'term_code',
            'fee_type', 'fee_type_name', 'fee_type_code',
            'amount', 'is_mandatory', 'frequency', 'effective_from',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class VoucherItemSerializer(serializers.ModelSerializer):
    """Serializer for VoucherItem."""
    
    fee_type_name = serializers.CharField(source='fee_type.name', read_only=True)
    fee_type_code = serializers.CharField(source='fee_type.code', read_only=True)
    
    class Meta:
        model = VoucherItem
        fields = [
            'id', 'voucher', 'fee_type', 'fee_type_name', 'fee_type_code',
            'description', 'amount', 'metadata', 'created_at'
        ]
        read_only_fields = ['created_at']


class VoucherSerializer(serializers.ModelSerializer):
    """Serializer for Voucher."""
    
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    term_name = serializers.CharField(source='term.name', read_only=True)
    term_code = serializers.CharField(source='term.code', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    items = VoucherItemSerializer(many=True, read_only=True)
    paid_amount = serializers.SerializerMethodField()
    outstanding_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Voucher
        fields = [
            'id', 'voucher_no', 'student', 'student_id', 'student_name',
            'term', 'term_code', 'term_name',
            'status', 'issue_date', 'due_date', 'total_amount',
            'paid_amount', 'outstanding_amount',
            'notes', 'created_by', 'created_by_name',
            'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['voucher_no', 'created_at', 'updated_at', 'status']
    
    def get_paid_amount(self, obj):
        return obj.get_paid_amount()
    
    def get_outstanding_amount(self, obj):
        return obj.get_outstanding_amount()


class VoucherCreateSerializer(serializers.Serializer):
    """Serializer for bulk voucher generation."""
    
    student_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text='List of student IDs. If not provided, generates for all students in program+term'
    )
    program_id = serializers.IntegerField(required=True)
    term_id = serializers.IntegerField(required=True)
    due_date = serializers.DateField(required=True)
    selected_fee_types = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text='Optional list of fee type codes to include'
    )


class LedgerEntrySerializer(serializers.ModelSerializer):
    """Serializer for LedgerEntry."""
    
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    term_name = serializers.CharField(source='term.name', read_only=True)
    term_code = serializers.CharField(source='term.code', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = LedgerEntry
        fields = [
            'id', 'student', 'student_id', 'student_name',
            'term', 'term_code', 'term_name',
            'entry_type', 'amount', 'currency',
            'reference_type', 'reference_id', 'description',
            'created_by', 'created_by_name',
            'created_at', 'voided_at', 'void_reason'
        ]
        read_only_fields = ['id', 'created_at']


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment."""
    
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    term_name = serializers.CharField(source='term.name', read_only=True)
    term_code = serializers.CharField(source='term.code', read_only=True)
    voucher_no = serializers.CharField(source='voucher.voucher_no', read_only=True)
    received_by_name = serializers.CharField(source='received_by.get_full_name', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.get_full_name', read_only=True)
    method_display = serializers.CharField(source='get_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'receipt_no', 'student', 'student_id', 'student_name',
            'term', 'term_code', 'term_name',
            'voucher', 'voucher_no',
            'amount', 'method', 'method_display',
            'reference_no', 'received_by', 'received_by_name',
            'received_at', 'status', 'status_display',
            'verified_by', 'verified_by_name', 'verified_at',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['receipt_no', 'created_at', 'updated_at', 'verified_by', 'verified_at']


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a payment."""
    
    class Meta:
        model = Payment
        fields = [
            'student', 'term', 'voucher', 'amount', 'method',
            'reference_no', 'notes'
        ]


class AdjustmentSerializer(serializers.ModelSerializer):
    """Serializer for Adjustment."""
    
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    term_name = serializers.CharField(source='term.name', read_only=True)
    term_code = serializers.CharField(source='term.code', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    kind_display = serializers.CharField(source='get_kind_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Adjustment
        fields = [
            'id', 'student', 'student_id', 'student_name',
            'term', 'term_code', 'term_name',
            'kind', 'kind_display', 'amount', 'reason',
            'requested_by', 'requested_by_name',
            'approved_by', 'approved_by_name', 'approved_at',
            'status', 'status_display', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'approved_by', 'approved_at']


class FinancePolicySerializer(serializers.ModelSerializer):
    """Serializer for FinancePolicy."""
    
    fee_type_name = serializers.CharField(source='fee_type_scope.name', read_only=True)
    rule_key_display = serializers.CharField(source='get_rule_key_display', read_only=True)
    
    class Meta:
        model = FinancePolicy
        fields = [
            'id', 'rule_key', 'rule_key_display',
            'threshold_amount', 'fee_type_scope', 'fee_type_name',
            'is_active', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class StudentFinanceSummarySerializer(serializers.Serializer):
    """Serializer for student finance summary."""
    
    student_id = serializers.CharField()
    student_name = serializers.CharField()
    term_id = serializers.IntegerField(required=False, allow_null=True)
    term_name = serializers.CharField(required=False, allow_null=True)
    total_debits = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_credits = serializers.DecimalField(max_digits=12, decimal_places=2)
    outstanding = serializers.DecimalField(max_digits=12, decimal_places=2)
    vouchers_count = serializers.IntegerField()
    vouchers_paid = serializers.IntegerField()
    vouchers_pending = serializers.IntegerField()
    vouchers_overdue = serializers.IntegerField()
    gating_flags = serializers.DictField()
    recent_payments = PaymentSerializer(many=True, required=False)
    recent_vouchers = VoucherSerializer(many=True, required=False)
