from django.urls import path
from .views import DeviceRegistrationView, DeviceTokenUpdateView, DeviceUnregisterView

urlpatterns = [
    path('register/', DeviceRegistrationView.as_view(), name='device-register'),
    path('update-token/', DeviceTokenUpdateView.as_view(), name='device-update-token'),
    path('unregister/', DeviceUnregisterView.as_view(), name='device-unregister'),
]
