"""
Core Views
API endpoints for core functionality including filter presets.
"""

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from apps.core.models import FilterPreset, AuditLog, OnCallSchedule, AssignmentPolicy
from apps.core.serializers import (
    FilterPresetSerializer,
    AuditLogSerializer,
    OnCallScheduleSerializer,
    AssignmentPolicySerializer
)


class APIRootView(APIView):
    """API root endpoint for the Hospital Consult System.

    This view provides a basic entry point to the API, returning a
    simple JSON response with links to the main API endpoints.
    """

    def get(self, request):
        """Handles GET requests to the API root.

        Args:
            request: The Django HttpRequest object.

        Returns:
            A DRF Response object with API information.
        """
        return Response({
            "message": "Hospital Consult System API",
            "version": "1.0.0",
            "endpoints": {
                "auth": "/api/v1/auth/",
                "departments": "/api/v1/departments/",
                "patients": "/api/v1/patients/",
                "consults": "/api/v1/consults/",
                "analytics": "/api/v1/analytics/",
                "filter-presets": "/api/v1/filter-presets/",
            }
        })


class FilterPresetViewSet(viewsets.ModelViewSet):
    """Viewset for managing user filter presets."""
    
    serializer_class = FilterPresetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Returns filter presets for the current user."""
        return FilterPreset.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Sets the user to the current user on creation."""
        serializer.save(user=self.request.user)


class AuditLogView(APIView):
    """API endpoint for viewing audit logs."""
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Gets audit logs.

        Query params:
            consult_id: Filter by consult
            action: Filter by action type
            actor_id: Filter by actor
            limit: Number of records to return (default 50)

        Returns:
            List of audit log entries.
        """
        # Only admins can view audit logs
        if not request.user.is_admin_user:
            return Response(
                {'error': 'Only administrators can view audit logs'},
                status=status.HTTP_403_FORBIDDEN
            )

        queryset = AuditLog.objects.select_related(
            'actor',
            'consult',
            'target_user',
            'department'
        )

        # Apply filters
        consult_id = request.query_params.get('consult_id')
        if consult_id:
            queryset = queryset.filter(consult_id=consult_id)

        action = request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)

        actor_id = request.query_params.get('actor_id')
        if actor_id:
            queryset = queryset.filter(actor_id=actor_id)

        limit = int(request.query_params.get('limit', 50))
        queryset = queryset.order_by('-timestamp')[:limit]

        serializer = AuditLogSerializer(queryset, many=True)
        return Response(serializer.data)


class OnCallScheduleViewSet(viewsets.ModelViewSet):
    """Viewset for managing on-call schedules."""
    
    serializer_class = OnCallScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Returns on-call schedules.

        Admins and HODs can see all schedules for their department.
        Regular users can only see their own schedules.
        """
        user = self.request.user
        
        if user.is_admin_user:
            return OnCallSchedule.objects.all()
        elif user.role == 'HOD' and user.department:
            return OnCallSchedule.objects.filter(department=user.department)
        else:
            return OnCallSchedule.objects.filter(user=user)

    def perform_create(self, serializer):
        """Validates permissions before creating schedule."""
        user = self.request.user
        
        # Only HOD or admin can create schedules
        if not user.is_admin_user and user.role != 'HOD':
            raise PermissionDenied('Only HOD or admin can create on-call schedules')
        
        # HOD can only create for their department
        department = serializer.validated_data.get('department')
        if user.role == 'HOD' and department != user.department:
            raise PermissionDenied('HOD can only create schedules for their department')
        
        serializer.save()


class AssignmentPolicyViewSet(viewsets.ModelViewSet):
    """Viewset for managing assignment policies."""
    
    serializer_class = AssignmentPolicySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Returns assignment policies.

        Admins can see all policies.
        HODs can see policies for their department.
        """
        user = self.request.user
        
        if user.is_admin_user:
            return AssignmentPolicy.objects.all()
        elif user.department:
            return AssignmentPolicy.objects.filter(department=user.department)
        return AssignmentPolicy.objects.none()

    def perform_create(self, serializer):
        """Validates permissions before creating policy."""
        user = self.request.user
        
        # Only HOD or admin can create policies
        if not user.is_admin_user and user.role != 'HOD':
            raise PermissionDenied('Only HOD or admin can create assignment policies')
        
        # HOD can only create for their department
        department = serializer.validated_data.get('department')
        if user.role == 'HOD' and department != user.department:
            raise PermissionDenied('HOD can only create policies for their department')
        
        serializer.save()
