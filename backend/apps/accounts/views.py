"""
Views for Accounts app.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model

from .serializers import UserSerializer, UserListSerializer, UserProfileSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User model.
    Provides user management operations.
    """
    
    permission_classes = [IsAuthenticated]
    queryset = User.objects.select_related('department')
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        """
        if self.action == 'list':
            return UserListSerializer
        elif self.action in ['update_profile', 'partial_update']:
            return UserProfileSerializer
        return UserSerializer
    
    def get_queryset(self):
        """
        Filter users based on parameters.
        """
        queryset = User.objects.filter(is_active=True).select_related('department')
        
        # Filter by department
        department_id = self.request.query_params.get('department', None)
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        
        # Filter by role
        role = self.request.query_params.get('role', None)
        if role:
            queryset = queryset.filter(role=role)
        
        # Filter by on-call status
        on_call = self.request.query_params.get('on_call', None)
        if on_call is not None:
            queryset = queryset.filter(is_on_call=on_call.lower() == 'true')
        
        return queryset.order_by('department', '-seniority_level')
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get current user profile.
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['patch'])
    def update_profile(self, request):
        """
        Update current user profile.
        """
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserSerializer(request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
