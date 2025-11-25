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
    """
    ViewSet for Department model.
    Provides CRUD operations for departments.
    """
    
    permission_classes = [IsAuthenticated]
    queryset = Department.objects.select_related('head')
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        """
        if self.action == 'list':
            return DepartmentListSerializer
        return DepartmentSerializer
    
    def get_queryset(self):
        """
        Filter to active departments unless user is admin.
        """
        if self.request.user.is_admin_user:
            return Department.objects.all()
        return Department.objects.filter(is_active=True)
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """
        Get all users in a department.
        """
        department = self.get_object()
        from apps.accounts.serializers import UserListSerializer
        users = department.users.filter(is_active=True)
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def active_consults(self, request, pk=None):
        """
        Get active consults for a department.
        """
        department = self.get_object()
        from apps.consults.serializers import ConsultRequestListSerializer
        consults = department.incoming_consults.exclude(
            status__in=['COMPLETED', 'CANCELLED']
        )
        serializer = ConsultRequestListSerializer(consults, many=True)
        return Response(serializer.data)
