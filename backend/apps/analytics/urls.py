from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DoctorAnalyticsViewSet

router = DefaultRouter()
router.register(r'doctors', DoctorAnalyticsViewSet, basename='doctor-analytics')

urlpatterns = [
    path('', include(router.urls)),
]
