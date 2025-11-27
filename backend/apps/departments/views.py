"""
Views for Departments app.
"""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q

from .models import Department
from .serializers import DepartmentSerializer, DepartmentListSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    """Provides API endpoints for managing departments.

    This ViewSet allows for the listing, retrieving, creating, updating, and
    deleting of departments. It also includes custom actions for retrieving
    the users and active consults within a department.
    """
    
    permission_classes = [IsAuthenticated]
    queryset = Department.objects.select_related('head')
    
    def get_serializer_class(self):
        """Selects the appropriate serializer for the current action.

        Uses `DepartmentListSerializer` for the 'list' action to provide a
        more concise representation. For all other actions, it defaults to
        the full `DepartmentSerializer`.

        Returns:
            The serializer class to be used for the request.
        """
        if self.action == 'list':
            return DepartmentListSerializer
        return DepartmentSerializer
    
    def get_queryset(self):
        """Constructs the queryset for the view.

        Admins can see all departments, while other users can only see
        active departments.

        Returns:
            A Django QuerySet of `Department` objects.
        """
        if self.request.user.is_admin_user:
            return Department.objects.all()
        return Department.objects.filter(is_active=True)
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """Retrieves all active users in a specific department.

        Args:
            request: The Django HttpRequest object.
            pk: The primary key of the `Department`.

        Returns:
            A DRF Response object containing the serialized user data.
        """
        department = self.get_object()
        from apps.accounts.serializers import UserListSerializer
        users = department.users.filter(is_active=True)
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def active_consults(self, request, pk=None):
        """Retrieves all active consults for a specific department.

        Args:
            request: The Django HttpRequest object.
            pk: The primary key of the `Department`.

        Returns:
            A DRF Response object containing the serialized consult data.
        """
        department = self.get_object()
        from apps.consults.serializers import ConsultRequestListSerializer
        consults = department.incoming_consults.exclude(
            status__in=['COMPLETED', 'CANCELLED']
        )
        serializer = ConsultRequestListSerializer(consults, many=True)
        return Response(serializer.data)
