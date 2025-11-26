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
    """Provides API endpoints for managing users.

    This ViewSet allows for listing, retrieving, creating, updating, and
    deleting users. It also includes custom actions for managing the
    currently authenticated user's profile.

    Filtering is available for 'department', 'role', and 'on_call' status.
    """
    
    permission_classes = [IsAuthenticated]
    queryset = User.objects.select_related('department')
    
    def get_serializer_class(self):
        """Selects the appropriate serializer for the current action.

        Uses `UserListSerializer` for the 'list' action to provide a more
        concise user representation. For profile updates, it uses
        `UserProfileSerializer`. For all other actions, it defaults to the
        full `UserSerializer`.

        Returns:
            The serializer class to be used for the request.
        """
        if self.action == 'list':
            return UserListSerializer
        elif self.action in ['update_profile', 'partial_update']:
            return UserProfileSerializer
        return UserSerializer
    
    def get_queryset(self):
        """Constructs the queryset for the view, with optional filtering.

        This method retrieves all active users and allows filtering by
        department, role, and on-call status via query parameters in the URL.

        Returns:
            A Django QuerySet of User objects.
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
        """Retrieves the profile of the currently authenticated user.

        Args:
            request: The Django HttpRequest object.

        Returns:
            A DRF Response object containing the serialized user data.
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['patch'])
    def update_profile(self, request):
        """Updates the profile of the currently authenticated user.

        Args:
            request: The Django HttpRequest object, containing the update
                     data.

        Returns:
            A DRF Response object with the updated user data, or an error
            response if the data is invalid.
        """
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserSerializer(request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
