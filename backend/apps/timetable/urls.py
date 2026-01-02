"""
URL configuration for Timetable app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WeekPlanViewSet, SessionOccurrenceViewSet

router = DefaultRouter()
router.register(r'weeks', WeekPlanViewSet, basename='week-plan')
router.register(r'sessions', SessionOccurrenceViewSet, basename='session-occurrence')

urlpatterns = [
    path('', include(router.urls)),
]
