"""
Analytics Serializers
Serializers for analytics models and data.
"""

from rest_framework import serializers
from apps.analytics.models import (
    DoctorPerformanceMetric,
    DepartmentDailyStats,
    ConsultTimeline
)


class DoctorPerformanceSerializer(serializers.ModelSerializer):
    """Serializer for DoctorPerformanceMetric model."""
    
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)
    doctor_email = serializers.EmailField(source='doctor.email', read_only=True)
    
    class Meta:
        model = DoctorPerformanceMetric
        fields = [
            'id',
            'doctor',
            'doctor_name',
            'doctor_email',
            'date',
            'consults_assigned',
            'consults_completed',
            'avg_response_time_minutes',
            'sla_compliance_rate',
            'notes_added',
            'escalations_received',
            'escalations_sent',
            'created_at',
            'updated_at'
        ]
        read_only_fields = fields


class DepartmentStatsSerializer(serializers.ModelSerializer):
    """Serializer for DepartmentDailyStats model."""
    
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_code = serializers.CharField(source='department.code', read_only=True)
    
    class Meta:
        model = DepartmentDailyStats
        fields = [
            'id',
            'department',
            'department_name',
            'department_code',
            'date',
            'consults_received',
            'consults_completed',
            'consults_escalated',
            'consults_pending',
            'consults_overdue',
            'avg_response_time_minutes',
            'sla_compliance_rate',
            'created_at',
            'updated_at'
        ]
        read_only_fields = fields


class TimelineEventSerializer(serializers.ModelSerializer):
    """Serializer for ConsultTimeline model."""
    
    event_display = serializers.CharField(source='get_event_type_display', read_only=True)
    actor_name = serializers.SerializerMethodField()
    timestamp_human = serializers.SerializerMethodField()
    
    class Meta:
        model = ConsultTimeline
        fields = [
            'id',
            'consult',
            'event_type',
            'event_display',
            'actor',
            'actor_name',
            'description',
            'metadata',
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
