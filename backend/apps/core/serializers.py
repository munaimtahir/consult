"""
Core Serializers
Serializers for core models.
"""

from rest_framework import serializers
from apps.core.models import (
    AuditLog,
    UnauthorizedAccessLog,
    FilterPreset,
    OnCallSchedule,
    AssignmentPolicy,
    DelayedConsultPolicy
)


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for AuditLog model."""
    
    actor_name = serializers.SerializerMethodField()
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    timestamp_human = serializers.SerializerMethodField()
    
    class Meta:
        model = AuditLog
        fields = [
            'id',
            'action',
            'action_display',
            'actor',
            'actor_name',
            'consult',
            'target_user',
            'department',
            'details',
            'ip_address',
            'timestamp',
            'timestamp_human'
        ]
        read_only_fields = fields

    def get_actor_name(self, obj):
        """Returns the actor's full name."""
        return obj.actor.get_full_name() if obj.actor else 'System'

    def get_timestamp_human(self, obj):
        """Returns a human-friendly timestamp."""
        from django.utils import timezone
        
        now = timezone.now()
        diff = now - obj.timestamp

        if diff.total_seconds() < 60:
            return 'just now'
        elif diff.total_seconds() < 3600:
            minutes = int(diff.total_seconds() / 60)
            return f'{minutes} minute{"s" if minutes != 1 else ""} ago'
        elif diff.total_seconds() < 86400:
            hours = int(diff.total_seconds() / 3600)
            return f'{hours} hour{"s" if hours != 1 else ""} ago'
        elif diff.days == 1:
            return 'yesterday'
        elif diff.days < 7:
            return f'{diff.days} days ago'
        else:
            return obj.timestamp.strftime('%b %d, %Y at %I:%M %p')


class UnauthorizedAccessLogSerializer(serializers.ModelSerializer):
    """Serializer for UnauthorizedAccessLog model."""
    
    user_name = serializers.SerializerMethodField()
    resource_type_display = serializers.CharField(source='get_resource_type_display', read_only=True)
    
    class Meta:
        model = UnauthorizedAccessLog
        fields = [
            'id',
            'user',
            'user_name',
            'resource_type',
            'resource_type_display',
            'resource_id',
            'action_attempted',
            'ip_address',
            'timestamp'
        ]
        read_only_fields = fields

    def get_user_name(self, obj):
        """Returns the user's full name."""
        return obj.user.get_full_name() if obj.user else 'Unknown'


class FilterPresetSerializer(serializers.ModelSerializer):
    """Serializer for FilterPreset model."""
    
    class Meta:
        model = FilterPreset
        fields = [
            'id',
            'name',
            'filters',
            'is_default',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_filters(self, value):
        """Validates the filters JSON structure."""
        if not isinstance(value, dict):
            raise serializers.ValidationError('Filters must be a JSON object')
        
        # Validate allowed filter keys
        allowed_keys = {
            'status', 'urgency', 'is_overdue', 'view',
            'target_department', 'requesting_department',
            'assigned_to', 'requester', 'date_range'
        }
        
        for key in value.keys():
            if key not in allowed_keys:
                raise serializers.ValidationError(f'Invalid filter key: {key}')
        
        return value


class OnCallScheduleSerializer(serializers.ModelSerializer):
    """Serializer for OnCallSchedule model."""
    
    user_name = serializers.SerializerMethodField()
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = OnCallSchedule
        fields = [
            'id',
            'department',
            'department_name',
            'user',
            'user_name',
            'start_time',
            'end_time',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_user_name(self, obj):
        """Returns the user's full name."""
        return obj.user.get_full_name()

    def validate(self, data):
        """Validates the schedule times."""
        if data.get('start_time') and data.get('end_time'):
            if data['start_time'] >= data['end_time']:
                raise serializers.ValidationError(
                    'End time must be after start time'
                )
        return data


class AssignmentPolicySerializer(serializers.ModelSerializer):
    """Serializer for AssignmentPolicy model."""
    
    department_name = serializers.CharField(source='department.name', read_only=True)
    assignment_mode_display = serializers.CharField(
        source='get_assignment_mode_display',
        read_only=True
    )
    
    class Meta:
        model = AssignmentPolicy
        fields = [
            'id',
            'department',
            'department_name',
            'urgency',
            'assignment_mode',
            'assignment_mode_display',
            'min_seniority',
            'escalation_minutes',
            'notify_hod',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DelayedConsultPolicySerializer(serializers.ModelSerializer):
    """Serializer for DelayedConsultPolicy model."""
    
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = DelayedConsultPolicy
        fields = [
            'id',
            'department',
            'department_name',
            'warning_threshold_percent',
            'escalation_levels',
            'auto_escalate',
            'notify_requester',
            'notify_hod',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_escalation_levels(self, value):
        """Validates the escalation levels structure."""
        if not isinstance(value, list):
            raise serializers.ValidationError('Escalation levels must be a list')
        
        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError(
                    'Each escalation level must be an object'
                )
            if 'minutes' not in item or 'level' not in item:
                raise serializers.ValidationError(
                    'Each escalation level must have minutes and level'
                )
        
        return value
