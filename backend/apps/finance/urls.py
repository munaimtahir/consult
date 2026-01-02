"""
URL configuration for Finance app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    FeeTypeViewSet, FeePlanViewSet, VoucherViewSet, PaymentViewSet,
    LedgerEntryViewSet, AdjustmentViewSet, FinancePolicyViewSet,
    StudentFinanceSummaryView, FinanceReportsView, FinanceCollectionReportView
)

router = DefaultRouter()
router.register(r'fee-types', FeeTypeViewSet, basename='fee-type')
router.register(r'fee-plans', FeePlanViewSet, basename='fee-plan')
router.register(r'vouchers', VoucherViewSet, basename='voucher')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'ledger', LedgerEntryViewSet, basename='ledger-entry')
router.register(r'adjustments', AdjustmentViewSet, basename='adjustment')
router.register(r'policies', FinancePolicyViewSet, basename='finance-policy')

urlpatterns = [
    path('', include(router.urls)),
    path('students/<int:student_id>/summary/', StudentFinanceSummaryView.as_view(), name='student-finance-summary'),
    path('reports/defaulters/', FinanceReportsView.as_view(), name='finance-defaulters'),
    path('reports/collection/', FinanceCollectionReportView.as_view(), name='finance-collection'),
]
