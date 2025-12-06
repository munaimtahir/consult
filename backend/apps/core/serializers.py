"""
Core serializers for system-wide settings.
"""

from rest_framework import serializers
from .models import (
    EmailNotificationSettings, 
    SMTPConfiguration,
    FilterPreset,
    AuditLog,
    OnCallSchedule,
    AssignmentPolicy
)
from apps.departments.serializers import DepartmentSerializer


class EmailNotificationSettingsSerializer(serializers.ModelSerializer):
    """Serializer for email notification settings."""
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = EmailNotificationSettings
        fields = [
            'id',
            'department',
            'department_id',
            'notify_on_consult_generated',
            'notify_on_consult_acknowledged',
            'notify_on_note_added',
            'notify_on_consult_closed',
            'notify_on_sla_breach',
            'notify_on_reassignment',
            'send_to_hod',
            'send_to_assigned_doctor',
            'send_to_requester',
            'additional_recipients',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class SMTPConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for SMTP configuration."""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    # Don't expose password in list view
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = SMTPConfiguration
        fields = [
            'id',
            'name',
            'host',
            'port',
            'use_tls',
            'username',
            'password',
            'from_email',
            'from_name',
            'reply_to_email',
            'is_active',
            'is_test_mode',
            'created_at',
            'updated_at',
            'created_by',
            'created_by_name',
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']
    
    def validate(self, data):
        """Validate that password is provided when creating new config."""
        if self.instance is None and not data.get('password'):
            raise serializers.ValidationError({'password': 'Password is required when creating a new configuration'})
        return data
    
    def create(self, validated_data):
        """Create SMTP configuration with current user as creator."""
        validated_data['created_by'] = self.context['request'].user
        # If password is not provided in update, keep existing password
        if 'password' in validated_data and not validated_data['password']:
            validated_data.pop('password')
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update SMTP configuration, preserving password if not provided."""
        # If password is not provided, don't update it
        if 'password' in validated_data and not validated_data['password']:
            validated_data.pop('password')
        return super().update(instance, validated_data)


class SMTPConfigurationListSerializer(serializers.ModelSerializer):
    """Serializer for SMTP configuration list (without password)."""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = SMTPConfiguration
        fields = [
            'id',
            'name',
            'host',
            'port',
            'use_tls',
            'username',
            'from_email',
            'from_name',
            'is_active',
            'is_test_mode',
            'created_at',
            'updated_at',
            'created_by_name',
        ]


class FilterPresetSerializer(serializers.ModelSerializer):
    """Serializer for filter presets."""
    
    class Meta:
        model = FilterPreset
        fields = [
            'id',
            'name',
            'filters',
            'is_default',
            'created_at',
            'updated_at',
            'user',
        ]
        read_only_fields = ['created_at', 'updated_at', 'user']


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for audit logs."""
    actor_name = serializers.CharField(source='actor.get_full_name', read_only=True)
    actor_email = serializers.CharField(source='actor.email', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id',
            'action',
            'details',
            'ip_address',
            'user_agent',
            'timestamp',
            'actor',
            'actor_name',
            'actor_email',
            'consult',
            'department',
            'target_user',
        ]
        read_only_fields = ['timestamp']


class OnCallScheduleSerializer(serializers.ModelSerializer):
    """Serializer for on-call schedules."""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = OnCallSchedule
        fields = [
            'id',
            'start_time',
            'end_time',
            'is_active',
            'created_at',
            'updated_at',
            'department',
            'department_name',
            'user',
            'user_name',
            'user_email',
        ]
        read_only_fields = ['created_at', 'updated_at']


class AssignmentPolicySerializer(serializers.ModelSerializer):
    """Serializer for assignment policies."""
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = AssignmentPolicy
        fields = [
            'id',
            'urgency',
            'assignment_mode',
            'min_seniority',
            'escalation_minutes',
            'notify_hod',
            'is_active',
            'created_at',
            'updated_at',
            'department',
            'department_name',
        ]
        read_only_fields = ['created_at', 'updated_at']
