"""
Core serializers for system-wide settings.
"""

from rest_framework import serializers
from .models import EmailNotificationSettings, SMTPConfiguration
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
