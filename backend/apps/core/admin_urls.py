"""
URL configuration for Admin API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.accounts.admin_views import AdminUserViewSet
from apps.departments.admin_views import AdminDepartmentViewSet
from apps.analytics.dashboard_views import (
    DepartmentDashboardView,
    GlobalDashboardView,
    ConsultReassignView,
    ConsultForceCloseView,
)
from apps.analytics.views import DoctorAnalyticsViewSet
from apps.core.admin_views import (
    EmailNotificationSettingsViewSet,
    SMTPConfigurationViewSet,
)

router = DefaultRouter()
router.register(r'users', AdminUserViewSet, basename='admin-user')
router.register(r'departments', AdminDepartmentViewSet, basename='admin-department')
router.register(r'email-notification-settings', EmailNotificationSettingsViewSet, basename='email-notification-settings')
router.register(r'smtp-configurations', SMTPConfigurationViewSet, basename='smtp-configurations')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboards/department/', DepartmentDashboardView.as_view(), name='department-dashboard'),
    path('dashboards/global/', GlobalDashboardView.as_view(), name='global-dashboard'),
    path('analytics/doctors/', DoctorAnalyticsViewSet.as_view({'get': 'list'}), name='admin-doctor-analytics'),
    path('consults/<int:consult_id>/reassign/', ConsultReassignView.as_view(), name='consult-reassign'),
    path('consults/<int:consult_id>/force-close/', ConsultForceCloseView.as_view(), name='consult-force-close'),
]
