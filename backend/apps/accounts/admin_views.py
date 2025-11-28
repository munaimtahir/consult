"""
Admin ViewSets for user and department management.
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db.models import Q

from .serializers import (
    AdminUserSerializer,
    AdminUserCreateSerializer,
    UserPermissionsUpdateSerializer,
    UserListSerializer,
)
from .permissions import CanManageUsers, CanManagePermissions

User = get_user_model()


class AdminUserViewSet(viewsets.ModelViewSet):
    """Admin ViewSet for managing users.
    
    Provides endpoints for listing, creating, updating, and managing users.
    Only accessible to users with can_manage_users permission or admins.
    """
    
    permission_classes = [IsAuthenticated, CanManageUsers]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'first_name', 'last_name', 'phone_number']
    ordering_fields = ['email', 'first_name', 'last_name', 'date_joined', 'department']
    ordering = ['-date_joined']
    
    def get_serializer_class(self):
        """Returns the appropriate serializer based on action."""
        if self.action == 'create':
            return AdminUserCreateSerializer
        if self.action == 'list':
            return UserListSerializer
        if self.action == 'update_permissions':
            return UserPermissionsUpdateSerializer
        return AdminUserSerializer
    
    def get_queryset(self):
        """Returns the queryset with optional filters."""
        queryset = User.objects.select_related('department').order_by('-date_joined')
        
        # Filter by department
        department_id = self.request.query_params.get('department')
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        
        # Filter by role
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by admin permissions
        has_admin_access = self.request.query_params.get('has_admin_access')
        if has_admin_access is not None:
            if has_admin_access.lower() == 'true':
                queryset = queryset.filter(
                    Q(role='ADMIN') | 
                    Q(is_superuser=True) |
                    Q(can_manage_users=True) |
                    Q(can_manage_departments=True) |
                    Q(can_view_department_dashboard=True) |
                    Q(can_view_global_dashboard=True) |
                    Q(can_manage_consults_globally=True) |
                    Q(can_manage_permissions=True)
                )
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Create a new user."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Return the full user data
        return Response(
            AdminUserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a user account."""
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response(AdminUserSerializer(user).data)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a user account."""
        user = self.get_object()
        
        # Prevent self-deactivation
        if user == request.user:
            return Response(
                {'error': 'You cannot deactivate your own account'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.is_active = False
        user.save()
        return Response(AdminUserSerializer(user).data)
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, CanManagePermissions])
    def update_permissions(self, request, pk=None):
        """Update a user's admin permissions.
        
        Only accessible to users with can_manage_permissions or superusers.
        """
        user = self.get_object()
        
        # Prevent modifying superuser permissions unless you're also a superuser
        if user.is_superuser and not request.user.is_superuser:
            return Response(
                {'error': 'Only superusers can modify superuser permissions'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = UserPermissionsUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(AdminUserSerializer(user).data)
    
    @action(detail=True, methods=['post'])
    def set_password(self, request, pk=None):
        """Set a new password for a user."""
        user = self.get_object()
        password = request.data.get('password')
        
        if not password:
            return Response(
                {'error': 'Password is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(password)
        user.save()
        
        return Response({'message': 'Password updated successfully'})
