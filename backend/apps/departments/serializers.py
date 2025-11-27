"""
Serializers for Departments app.
"""

from rest_framework import serializers
from .models import Department


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializes the `Department` model for detailed views.

    This serializer includes detailed information about a department,
    including calculated fields for the head's name, user count, and
    active consults count.
    """
    
    head_name = serializers.CharField(source='head.get_full_name', read_only=True)
    user_count = serializers.IntegerField(read_only=True)
    active_consults_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Department
        fields = [
            'id',
            'name',
            'code',
            'head',
            'head_name',
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


class DepartmentListSerializer(serializers.ModelSerializer):
    """A lightweight serializer for listing departments.

    This serializer provides a minimal set of department fields, optimized
    for use in list views.
    """
    
    head_name = serializers.CharField(source='head.get_full_name', read_only=True)
    
    class Meta:
        model = Department
        fields = [
            'id',
            'name',
            'code',
            'head_name',
            'is_active'
        ]
