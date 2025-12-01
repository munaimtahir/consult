"""
Admin ViewSets for department management.
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import ProtectedError

from .models import Department
from .serializers import (
    AdminDepartmentSerializer,
    DepartmentListSerializer,
    DepartmentMemberSerializer,
)
from apps.accounts.permissions import CanManageDepartments
from apps.accounts.serializers import UserListSerializer


class AdminDepartmentViewSet(viewsets.ModelViewSet):
    """Admin ViewSet for managing departments.
    
    Provides endpoints for listing, creating, updating, and managing departments.
    Only accessible to users with can_manage_departments permission or admins.
    """
    
    permission_classes = [IsAuthenticated, CanManageDepartments]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'contact_number']
    ordering_fields = ['name', 'code', 'created_at', 'department_type']
    ordering = ['name']
    
    def get_serializer_class(self):
        """Returns the appropriate serializer based on action."""
        if self.action == 'list':
            return DepartmentListSerializer
        return AdminDepartmentSerializer
    
    def get_queryset(self):
        """Returns the queryset with optional filters."""
        queryset = Department.objects.select_related('head', 'parent').order_by('name')
        
        # Filter by department type
        department_type = self.request.query_params.get('department_type')
        if department_type:
            queryset = queryset.filter(department_type=department_type)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by parent (top-level vs subdepartments)
        parent_filter = self.request.query_params.get('parent')
        if parent_filter == 'none':
            queryset = queryset.filter(parent__isnull=True)
        elif parent_filter:
            queryset = queryset.filter(parent_id=parent_filter)
        
        # Filter to show only top-level departments
        top_level = self.request.query_params.get('top_level')
        if top_level and top_level.lower() == 'true':
            queryset = queryset.filter(parent__isnull=True)
        
        return queryset
    
    def destroy(self, request, *args, **kwargs):
        """Delete a department with protection for related data."""
        department = self.get_object()
        
        # Check if department has users
        if department.users.exists():
            return Response(
                {'error': 'Cannot delete department with assigned users. Please reassign users first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if department has subdepartments
        if department.subdepartments.exists():
            return Response(
                {'error': 'Cannot delete department with subdepartments. Please delete or reassign subdepartments first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {'error': 'Cannot delete department due to related consults or other protected data.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """Get all users in this department."""
        department = self.get_object()
        users = department.users.filter(is_active=True).select_related('department')
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def subdepartments(self, request, pk=None):
        """Get all subdepartments of this department."""
        department = self.get_object()
        subdepts = department.subdepartments.all()
        serializer = DepartmentListSerializer(subdepts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a department."""
        department = self.get_object()
        department.is_active = True
        department.save()
        return Response(AdminDepartmentSerializer(department).data)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a department."""
        department = self.get_object()
        
        # Check for active consults
        active_consults = department.incoming_consults.exclude(
            status__in=['COMPLETED', 'CANCELLED']
        ).count()
        
        if active_consults > 0:
            return Response(
                {'error': f'Cannot deactivate department with {active_consults} active consults.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        department.is_active = False
        department.save()
        return Response(AdminDepartmentSerializer(department).data)
    
    @action(detail=False, methods=['get'])
    def hierarchy(self, request):
        """Get departments in a hierarchical structure."""
        queryset = Department.objects.filter(
            parent__isnull=True,
            is_active=True
        ).select_related('head').prefetch_related('subdepartments')
        
        result = []
        for dept in queryset:
            dept_data = AdminDepartmentSerializer(dept).data
            dept_data['children'] = AdminDepartmentSerializer(
                dept.subdepartments.filter(is_active=True),
                many=True
            ).data
            result.append(dept_data)
        
        return Response(result)

    @action(detail=True, methods=['get'])
    def overview(self, request, pk=None):
        """Get an overview of the department's members and their consult stats."""
        department = self.get_object()
        users = department.users.annotate(
            active_consults=Count('assigned_consults', filter=Q(assigned_consults__status__in=['SUBMITTED', 'IN_PROGRESS'])),
            completed_consults=Count('assigned_consults', filter=Q(assigned_consults__status='COMPLETED'))
        ).order_by('hierarchy_number')

        serializer = DepartmentMemberSerializer(users, many=True)
        return Response(serializer.data)
