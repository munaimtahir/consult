from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Avg, Count, F, Q, DurationField
from django.db.models.functions import Extract

from apps.accounts.models import User
from apps.accounts.permissions import CanViewGlobalDashboard
from apps.analytics.services import AnalyticsService
from apps.consults.models import ConsultRequest

class DoctorAnalyticsViewSet(viewsets.ViewSet):
    """
    Provides analytics data for doctors.
    """
    permission_classes = [IsAuthenticated, CanViewGlobalDashboard]

    def list(self, request):
        """
        Returns a list of analytics for each doctor.
        """
        analytics_data = User.objects.filter(role='DOCTOR').annotate(
            total_consults=Count('assigned_consults'),
            avg_acknowledgment_time=Avg(
                Extract(F('assigned_consults__acknowledged_at') - F('assigned_consults__created_at'), 'epoch'),
                output_field=DurationField()
            ),
            avg_completion_time=Avg(
                Extract(F('assigned_consults__completed_at') - F('assigned_consults__created_at'), 'epoch'),
                output_field=DurationField()
            ),
            pending_workload=Count('assigned_consults', filter=Q(assigned_consults__status__in=['SUBMITTED', 'ACKNOWLEDGED', 'IN_PROGRESS'])),
            escalations_handled=Count('assigned_consults', filter=Q(assigned_consults__escalation_level__gt > 0)),
            delayed_consults=Count('assigned_consults', filter=Q(assigned_consults__is_overdue=True))
        ).values(
            'id',
            'first_name',
            'last_name',
            'total_consults',
            'avg_acknowledgment_time',
            'avg_completion_time',
            'pending_workload',
            'escalations_handled',
            'delayed_consults'
        )

        return Response(list(analytics_data))


class MyPerformanceView(APIView):
    """Return performance metrics for the authenticated doctor."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = AnalyticsService.get_doctor_performance(request.user)
        return Response(data, status=status.HTTP_200_OK)


class DepartmentStatsView(APIView):
    """Return department-level analytics for HODs or admins."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not (
            request.user.role in ["HOD", "ADMIN", "SUPER_ADMIN"]
            or request.user.can_view_department_dashboard
        ):
            raise PermissionDenied("You do not have permission to view department analytics.")

        if not request.user.department:
            return Response(
                {"detail": "User is not assigned to a department."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = AnalyticsService.get_department_stats(request.user.department)
        return Response(data, status=status.HTTP_200_OK)


class GlobalStatsView(APIView):
    """Return system-wide analytics for admins."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not (
            request.user.role in ["ADMIN", "SUPER_ADMIN"]
            or request.user.can_view_global_dashboard
        ):
            raise PermissionDenied("You do not have permission to view global analytics.")

        data = AnalyticsService.get_global_stats()
        return Response(data, status=status.HTTP_200_OK)
