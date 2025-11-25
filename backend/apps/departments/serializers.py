"""
Serializers for Departments app.
"""

from rest_framework import serializers
from .models import Department


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department model."""
    
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
    """Lightweight serializer for list views."""
    
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
