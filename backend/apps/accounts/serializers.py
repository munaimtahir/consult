"""
Serializers for Accounts app.
"""

from rest_framework import serializers
from .models import User


class UserPermissionsSerializer(serializers.Serializer):
    """Serializes user permission flags for the frontend."""
    
    can_manage_users = serializers.BooleanField(read_only=True)
    can_manage_departments = serializers.BooleanField(read_only=True)
    can_view_department_dashboard = serializers.BooleanField(read_only=True)
    can_view_global_dashboard = serializers.BooleanField(read_only=True)
    can_manage_consults_globally = serializers.BooleanField(read_only=True)
    can_manage_permissions = serializers.BooleanField(read_only=True)


class DepartmentNestedSerializer(serializers.Serializer):
    """Lightweight department serializer for nesting in user responses."""
    
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    code = serializers.CharField(read_only=True)


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
        permissions: A nested object containing all permission flags.
        has_admin_panel_access: Whether the user can access the Admin Panel.
    """
    
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_info = DepartmentNestedSerializer(source='department', read_only=True)
    designation_display = serializers.CharField(read_only=True)
    is_hod = serializers.BooleanField(read_only=True)
    is_admin_user = serializers.BooleanField(read_only=True)
    can_assign_consults = serializers.BooleanField(read_only=True)
    has_admin_panel_access = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    
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
            'department_info',
            'seniority_level',
            'phone_number',
            'profile_photo',
            'is_on_call',
            'is_hod',
            'is_admin_user',
            'can_assign_consults',
            'has_admin_panel_access',
            'permissions',
            'is_active',
            'date_joined'
        ]
        read_only_fields = ['date_joined', 'seniority_level']
    
    def get_permissions(self, obj):
        """Returns the user's permission flags as a dictionary."""
        return obj.get_permissions_dict()
    
    def get_has_admin_panel_access(self, obj):
        """Returns whether the user can access the Admin Panel."""
        return obj.has_admin_panel_access()


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
            'department',
            'department_name',
            'is_on_call',
            'is_active'
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


class AdminUserSerializer(serializers.ModelSerializer):
    """Serializer for admin user management.
    
    Used by AdminUserViewSet for creating and updating users.
    Includes all user fields that an admin can modify.
    """
    
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_info = DepartmentNestedSerializer(source='department', read_only=True)
    designation_display = serializers.CharField(read_only=True)
    is_hod = serializers.BooleanField(read_only=True)
    is_admin_user = serializers.BooleanField(read_only=True)
    can_assign_consults = serializers.BooleanField(read_only=True)
    has_admin_panel_access = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    
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
            'department_info',
            'seniority_level',
            'phone_number',
            'profile_photo',
            'is_on_call',
            'is_hod',
            'is_admin_user',
            'can_assign_consults',
            'has_admin_panel_access',
            'permissions',
            'is_active',
            'is_staff',
            'date_joined',
            # Permission flags
            'can_manage_users',
            'can_manage_departments',
            'can_view_department_dashboard',
            'can_view_global_dashboard',
            'can_manage_consults_globally',
            'can_manage_permissions',
        ]
        read_only_fields = ['date_joined', 'seniority_level', 'is_hod', 'is_admin_user']
    
    def get_permissions(self, obj):
        """Returns the user's permission flags as a dictionary."""
        return obj.get_permissions_dict()
    
    def get_has_admin_panel_access(self, obj):
        """Returns whether the user can access the Admin Panel."""
        return obj.has_admin_panel_access()


class AdminUserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users via the admin panel."""
    
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = [
            'email',
            'password',
            'first_name',
            'last_name',
            'role',
            'designation',
            'department',
            'phone_number',
            'is_active',
            'is_staff',
            # Permission flags
            'can_manage_users',
            'can_manage_departments',
            'can_view_department_dashboard',
            'can_view_global_dashboard',
            'can_manage_consults_globally',
            'can_manage_permissions',
        ]
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            # Set an unusable password if none provided
            user.set_unusable_password()
        user.save()
        return user


class UserPermissionsUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user permissions only."""
    
    class Meta:
        model = User
        fields = [
            'can_manage_users',
            'can_manage_departments',
            'can_view_department_dashboard',
            'can_view_global_dashboard',
            'can_manage_consults_globally',
            'can_manage_permissions',
        ]

