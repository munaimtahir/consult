"""
URL configuration for Consults app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConsultRequestViewSet, ConsultNoteViewSet

router = DefaultRouter()
router.register(r'requests', ConsultRequestViewSet, basename='consult-request')
router.register(r'notes', ConsultNoteViewSet, basename='consult-note')

urlpatterns = [
    path('', include(router.urls)),
]
