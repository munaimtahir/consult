"""
Serializers for Accounts app.
"""

from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializes the `User` model for detailed views.

    This serializer includes comprehensive information about a user,
    including their role, department, and calculated properties like
    `is_hod` and `can_assign_consults`. It's used for retrieving, creating,
    and updating user instances.

    Attributes:
        department_name: The name of the user's department.
        designation_display: The human-readable designation of the user.
        is_hod: A boolean indicating if the user is a Head of Department.
        can_assign_consults: A boolean indicating if the user can assign
                             consults.
    """
    
    department_name = serializers.CharField(source='department.name', read_only=True)
    designation_display = serializers.CharField(read_only=True)
    is_hod = serializers.BooleanField(read_only=True)
    can_assign_consults = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'role',
            'designation',
            'designation_display',
            'department',
            'department_name',
            'seniority_level',
            'phone_number',
            'profile_photo',
            'is_on_call',
            'is_hod',
            'can_assign_consults',
            'is_active',
            'date_joined'
        ]
        read_only_fields = ['date_joined', 'seniority_level']


class UserListSerializer(serializers.ModelSerializer):
    """A lightweight serializer for listing users.

    This serializer provides a minimal set of user fields, optimized for
    use in list views where a full user representation is not required.

    Attributes:
        department_name: The name of the user's department.
    """
    
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'role',
            'designation',
            'department_name',
            'is_on_call'
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializes a user's profile for updates.

    This serializer is specifically for updating a user's own profile, and
    only exposes a limited set of fields that are safe for a user to
    modify.
    """
    
    class Meta:
        model = User
        fields = [
            'phone_number',
            'is_on_call'
        ]
