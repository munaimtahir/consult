"""
URL configuration for intake app.
"""

from django.urls import path
from . import views

app_name = 'intake'

urlpatterns = [
    path('apply/student-intake/', views.student_intake_form, name='form'),
    path('apply/student-intake/success/<str:submission_id>/', views.student_intake_success, name='success'),
]
