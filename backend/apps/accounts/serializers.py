"""
Serializers for Accounts app.
"""

from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
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
    """Lightweight serializer for list views."""
    
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
    """Serializer for user profile updates."""
    
    class Meta:
        model = User
        fields = [
            'phone_number',
            'is_on_call'
        ]
