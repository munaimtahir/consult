"""
Analytics URL configuration.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Doctor performance
    path(
        'doctor-performance/',
        views.DoctorPerformanceView.as_view(),
        name='my-performance'
    ),
    path(
        'doctor-performance/<int:doctor_id>/',
        views.DoctorPerformanceView.as_view(),
        name='doctor-performance'
    ),
    
    # Department stats
    path(
        'department-stats/',
        views.DepartmentStatsView.as_view(),
        name='my-department-stats'
    ),
    path(
        'department-stats/<int:department_id>/',
        views.DepartmentStatsView.as_view(),
        name='department-stats'
    ),
    
    # Global stats
    path(
        'global-stats/',
        views.GlobalStatsView.as_view(),
        name='global-stats'
    ),
    
    # Consult timeline
    path(
        'consult-timeline/<int:consult_id>/',
        views.ConsultTimelineView.as_view(),
        name='consult-timeline'
    ),
    
    # Load balance
    path(
        'load-balance/',
        views.LoadBalanceStatsView.as_view(),
        name='load-balance'
    ),
    path(
        'load-balance/<int:department_id>/',
        views.LoadBalanceStatsView.as_view(),
        name='department-load-balance'
    ),
    
    # Overdue consults
    path(
        'overdue-consults/',
        views.OverdueConsultsView.as_view(),
        name='overdue-consults'
    ),
    path(
        'overdue-consults/<int:department_id>/',
        views.OverdueConsultsView.as_view(),
        name='department-overdue-consults'
    ),
]
