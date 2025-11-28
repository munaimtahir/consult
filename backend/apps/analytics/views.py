"""
Analytics Views
API endpoints for analytics and dashboard data.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from datetime import datetime, timedelta

from apps.analytics.services import AnalyticsService
from apps.analytics.serializers import (
    DoctorPerformanceSerializer,
    DepartmentStatsSerializer,
    TimelineEventSerializer
)


class DoctorPerformanceView(APIView):
    """API endpoint for doctor performance metrics."""
    
    permission_classes = [IsAuthenticated]

    def get(self, request, doctor_id=None):
        """Gets performance metrics for a doctor.

        If no doctor_id is provided, returns metrics for the current user.

        Query params:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Performance metrics for the doctor.
        """
        from apps.accounts.models import User

        if doctor_id:
            try:
                doctor = User.objects.get(id=doctor_id)
            except User.DoesNotExist:
                return Response(
                    {'error': 'Doctor not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check permissions - only self, HOD, or admin can view
            if (request.user.id != doctor_id and 
                not request.user.is_admin_user and
                request.user.department != doctor.department):
                return Response(
                    {'error': 'You do not have permission to view this doctor\'s performance'},
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            doctor = request.user

        # Parse date range
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        metrics = AnalyticsService.get_doctor_performance(doctor, start_date, end_date)
        return Response(metrics)


class DepartmentStatsView(APIView):
    """API endpoint for department statistics."""
    
    permission_classes = [IsAuthenticated]

    def get(self, request, department_id=None):
        """Gets statistics for a department.

        If no department_id is provided, returns stats for user's department.

        Query params:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Statistics for the department.
        """
        from apps.departments.models import Department

        if department_id:
            try:
                department = Department.objects.get(id=department_id)
            except Department.DoesNotExist:
                return Response(
                    {'error': 'Department not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check permissions
            if (not request.user.can_view_department_dashboard_for(department) and
                not request.user.is_admin_user):
                return Response(
                    {'error': 'You do not have permission to view this department\'s stats'},
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            department = request.user.department
            if not department:
                return Response(
                    {'error': 'No department associated with user'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Parse date range
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        stats = AnalyticsService.get_department_stats(department, start_date, end_date)
        return Response(stats)


class GlobalStatsView(APIView):
    """API endpoint for system-wide statistics."""
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Gets global system statistics.

        Only available to users with global dashboard access.

        Query params:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            System-wide statistics.
        """
        # Check permissions
        if not request.user.can_view_global_dashboard and not request.user.is_admin_user:
            return Response(
                {'error': 'You do not have permission to view global statistics'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Parse date range
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        stats = AnalyticsService.get_global_stats(start_date, end_date)
        return Response(stats)


class ConsultTimelineView(APIView):
    """API endpoint for consult timeline."""
    
    permission_classes = [IsAuthenticated]

    def get(self, request, consult_id):
        """Gets the timeline for a specific consult.

        Args:
            consult_id: The ID of the consult.

        Returns:
            List of timeline events.
        """
        from apps.consults.models import ConsultRequest

        try:
            consult = ConsultRequest.objects.select_related(
                'patient',
                'requester',
                'target_department',
                'assigned_to'
            ).get(id=consult_id)
        except ConsultRequest.DoesNotExist:
            return Response(
                {'error': 'Consult not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check permissions
        if (request.user.department != consult.target_department and
            request.user.department != consult.requesting_department and
            request.user != consult.requester and
            request.user != consult.assigned_to and
            not request.user.is_admin_user):
            return Response(
                {'error': 'You do not have permission to view this consult\'s timeline'},
                status=status.HTTP_403_FORBIDDEN
            )

        timeline = AnalyticsService.get_consult_timeline(consult)
        return Response(timeline)


class LoadBalanceStatsView(APIView):
    """API endpoint for load balance statistics."""
    
    permission_classes = [IsAuthenticated]

    def get(self, request, department_id=None):
        """Gets load balance stats for department doctors.

        Args:
            department_id: Optional department ID.

        Returns:
            Load balance statistics for each doctor.
        """
        from apps.departments.models import Department
        from apps.core.services.assignment_service import AssignmentService

        if department_id:
            try:
                department = Department.objects.get(id=department_id)
            except Department.DoesNotExist:
                return Response(
                    {'error': 'Department not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            department = request.user.department
            if not department:
                return Response(
                    {'error': 'No department associated with user'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Check permissions - only HOD or admin
        if (request.user.role not in ['HOD', 'ADMIN'] and 
            not request.user.is_admin_user):
            return Response(
                {'error': 'Only HOD or admin can view load balance stats'},
                status=status.HTTP_403_FORBIDDEN
            )

        stats = AssignmentService.get_load_balance_stats(department)
        return Response(stats)


class OverdueConsultsView(APIView):
    """API endpoint for overdue consults."""
    
    permission_classes = [IsAuthenticated]

    def get(self, request, department_id=None):
        """Gets overdue consults.

        Args:
            department_id: Optional department ID to filter by.

        Returns:
            List of overdue consults.
        """
        from apps.departments.models import Department
        from apps.core.services.escalation_service import EscalationService
        from apps.consults.serializers import ConsultRequestListSerializer

        department = None
        if department_id:
            try:
                department = Department.objects.get(id=department_id)
            except Department.DoesNotExist:
                return Response(
                    {'error': 'Department not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        elif request.user.department:
            department = request.user.department

        overdue = EscalationService.get_overdue_consults(department)
        approaching = EscalationService.get_approaching_deadline_consults(department)

        return Response({
            'overdue': ConsultRequestListSerializer(overdue, many=True).data,
            'approaching_deadline': ConsultRequestListSerializer(approaching, many=True).data
        })
