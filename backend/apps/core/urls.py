from django.urls import path, include
from .views import APIRootView

urlpatterns = [
    path('', APIRootView.as_view(), name='api-root'),
    path('auth/', include('apps.accounts.urls')),
    path('departments/', include('apps.departments.urls')),
    path('patients/', include('apps.patients.urls')),
    path('consults/', include('apps.consults.urls')),
    path('admin/', include('apps.core.admin_urls')),
]
