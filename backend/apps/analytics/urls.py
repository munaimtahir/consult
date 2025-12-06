from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    DepartmentStatsView,
    DoctorAnalyticsViewSet,
    GlobalStatsView,
    MyPerformanceView,
)

router = DefaultRouter()
router.register(r'doctors', DoctorAnalyticsViewSet, basename='doctor-analytics')

urlpatterns = [
    path('doctor-performance/', MyPerformanceView.as_view(), name='doctor-performance'),
    path('department-stats/', DepartmentStatsView.as_view(), name='department-stats'),
    path('global-stats/', GlobalStatsView.as_view(), name='global-stats'),
    path('', include(router.urls)),
]
