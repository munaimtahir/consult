"""
Core URL configuration.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .core_views import (
    HealthCheckView,
    APIRootView,
    FilterPresetViewSet,
    AuditLogView,
    OnCallScheduleViewSet,
    AssignmentPolicyViewSet
)
from apps.core.views.email_reply_views import process_email_reply

# Create router for viewsets
router = DefaultRouter()
router.register(r'filter-presets', FilterPresetViewSet, basename='filter-preset')
router.register(r'on-call-schedules', OnCallScheduleViewSet, basename='on-call-schedule')
router.register(r'assignment-policies', AssignmentPolicyViewSet, basename='assignment-policy')

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('', APIRootView.as_view(), name='api-root'),
    path('auth/', include('apps.accounts.urls')),
    path('departments/', include('apps.departments.urls')),
    path('patients/', include('apps.patients.urls')),
    path('consults/', include('apps.consults.urls')),
    path('analytics/', include('apps.analytics.urls')),
    path('admin/', include('apps.core.admin_urls')),
    path('devices/', include('apps.notifications.urls')),
    path('audit-logs/', AuditLogView.as_view(), name='audit-logs'),
    path('email-reply/', process_email_reply, name='email-reply'),
    # Include router URLs
    path('', include(router.urls)),
]
