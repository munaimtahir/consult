from django.contrib import admin
from .models import (
    FeeType, FeePlan, Voucher, VoucherItem, LedgerEntry,
    Payment, Adjustment, FinancePolicy
)


@admin.register(FeeType)
class FeeTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['code', 'name']
    ordering = ['code']


@admin.register(FeePlan)
class FeePlanAdmin(admin.ModelAdmin):
    list_display = ['program', 'term', 'fee_type', 'amount', 'is_mandatory', 'frequency', 'is_active']
    list_filter = ['is_active', 'is_mandatory', 'frequency', 'program', 'term']
    search_fields = ['program__code', 'program__name', 'term__code', 'fee_type__code']
    raw_id_fields = ['program', 'term', 'fee_type']


class VoucherItemInline(admin.TabularInline):
    model = VoucherItem
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ['voucher_no', 'student', 'term', 'total_amount', 'status', 'due_date', 'created_at']
    list_filter = ['status', 'term', 'created_at']
    search_fields = ['voucher_no', 'student__student_id', 'student__full_name']
    raw_id_fields = ['student', 'term', 'created_by']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [VoucherItemInline]


@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = ['student', 'term', 'entry_type', 'amount', 'reference_type', 'created_at']
    list_filter = ['entry_type', 'reference_type', 'created_at']
    search_fields = ['student__student_id', 'student__full_name', 'reference_id']
    raw_id_fields = ['student', 'term', 'created_by']
    readonly_fields = ['id', 'created_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['receipt_no', 'student', 'term', 'amount', 'method', 'status', 'received_at']
    list_filter = ['status', 'method', 'term', 'received_at']
    search_fields = ['receipt_no', 'student__student_id', 'student__full_name', 'reference_no']
    raw_id_fields = ['student', 'term', 'voucher', 'received_by', 'verified_by']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Adjustment)
class AdjustmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'term', 'kind', 'amount', 'status', 'requested_by', 'created_at']
    list_filter = ['status', 'kind', 'term', 'created_at']
    search_fields = ['student__student_id', 'student__full_name']
    raw_id_fields = ['student', 'term', 'requested_by', 'approved_by']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(FinancePolicy)
class FinancePolicyAdmin(admin.ModelAdmin):
    list_display = ['rule_key', 'threshold_amount', 'fee_type_scope', 'is_active']
    list_filter = ['is_active', 'rule_key']
    raw_id_fields = ['fee_type_scope']
