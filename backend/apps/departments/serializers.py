"""
Serializers for Departments app.
"""

from rest_framework import serializers
from .models import Department
from apps.accounts.models import User


class DepartmentMemberSerializer(serializers.ModelSerializer):
    """Serializer for department members in the overview table."""

    role = serializers.CharField(source='get_role_display')
    active_consults = serializers.IntegerField(read_only=True)
    completed_consults = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'full_name',
            'role',
            'hierarchy_number',
            'active_consults',
            'completed_consults'
        ]


class ParentDepartmentSerializer(serializers.ModelSerializer):
    """Lightweight serializer for parent department representation."""
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'code']


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializes the `Department` model for detailed views.

    This serializer includes detailed information about a department,
    including calculated fields for the head's name, user count, and
    active consults count.
    """
    
    head_name = serializers.CharField(source='head.get_full_name', read_only=True)
    delegated_receiver_name = serializers.CharField(source='delegated_receiver.get_full_name', read_only=True)
    user_count = serializers.IntegerField(read_only=True)
    active_consults_count = serializers.IntegerField(read_only=True)
    parent_info = ParentDepartmentSerializer(source='parent', read_only=True)
    is_subdepartment = serializers.BooleanField(read_only=True)
    subdepartments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = [
            'id',
            'name',
            'code',
            'department_type',
            'parent',
            'parent_info',
            'is_subdepartment',
            'subdepartments_count',
            'head',
            'head_name',
            'delegated_receiver',
            'delegated_receiver_name',
            'contact_number',
            'is_active',
            'emergency_sla',
            'urgent_sla',
            'routine_sla',
            'user_count',
            'active_consults_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_subdepartments_count(self, obj):
        """Returns the count of active subdepartments."""
        return obj.subdepartments.filter(is_active=True).count()


class DepartmentListSerializer(serializers.ModelSerializer):
    """A lightweight serializer for listing departments.

    This serializer provides a minimal set of department fields, optimized
    for use in list views.
    """
    
    head_name = serializers.CharField(source='head.get_full_name', read_only=True)
    parent_info = ParentDepartmentSerializer(source='parent', read_only=True)
    is_subdepartment = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Department
        fields = [
            'id',
            'name',
            'code',
            'department_type',
            'parent',
            'parent_info',
            'is_subdepartment',
            'head_name',
            'is_active'
        ]


class AdminDepartmentSerializer(serializers.ModelSerializer):
    """Serializer for admin department management.
    
    Used by AdminDepartmentViewSet for creating and updating departments.
    """
    
    head_name = serializers.CharField(source='head.get_full_name', read_only=True)
    head_email = serializers.CharField(source='head.email', read_only=True)
    delegated_receiver_name = serializers.CharField(source='delegated_receiver.get_full_name', read_only=True)
    parent_info = ParentDepartmentSerializer(source='parent', read_only=True)
    is_subdepartment = serializers.BooleanField(read_only=True)
    user_count = serializers.IntegerField(read_only=True)
    active_consults_count = serializers.IntegerField(read_only=True)
    subdepartments = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = [
            'id',
            'name',
            'code',
            'department_type',
            'parent',
            'parent_info',
            'is_subdepartment',
            'subdepartments',
            'head',
            'head_name',
            'head_email',
            'delegated_receiver',
            'delegated_receiver_name',
            'contact_number',
            'is_active',
            'emergency_sla',
            'urgent_sla',
            'routine_sla',
            'user_count',
            'active_consults_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_subdepartments(self, obj):
        """Returns serialized subdepartments."""
        subdepts = obj.subdepartments.filter(is_active=True)
        return ParentDepartmentSerializer(subdepts, many=True).data
    
    def validate_parent(self, value):
        """Validate that a department cannot be its own parent."""
        if self.instance and value and self.instance.id == value.id:
            raise serializers.ValidationError("A department cannot be its own parent.")
        return value
