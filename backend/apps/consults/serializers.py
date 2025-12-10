"""
Serializers for Consults app.
"""

from rest_framework import serializers
from django.utils import timezone
from .models import ConsultRequest, ConsultNote
from apps.patients.serializers import PatientSerializer
from apps.accounts.serializers import UserSerializer
from apps.departments.serializers import DepartmentSerializer
from apps.core.constants import get_urgency_color, get_status_color


def humanize_timestamp(timestamp):
    """Converts a timestamp to a human-friendly format."""
    if not timestamp:
        return None
    
    now = timezone.now()
    diff = now - timestamp

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
        return timestamp.strftime('%b %d, %Y at %I:%M %p')


class ConsultNoteSerializer(serializers.ModelSerializer):
    """Serializes `ConsultNote` model instances.

    Includes the author's full name and designation for easy display in
    the frontend.
    """
    
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    author_designation = serializers.CharField(source='author.designation_display', read_only=True)
    created_at_human = serializers.SerializerMethodField()
    note_type_display = serializers.CharField(source='get_note_type_display', read_only=True)
    
    class Meta:
        model = ConsultNote
        fields = [
            'id',
            'consult',
            'author',
            'author_name',
            'author_designation',
            'note_type',
            'note_type_display',
            'content',
            'recommendations',
            'follow_up_required',
            'follow_up_instructions',
            'is_final',
            'created_at',
            'created_at_human',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'consult', 'author']

    def get_created_at_human(self, obj):
        """Returns a human-friendly created_at timestamp."""
        return humanize_timestamp(obj.created_at)


class ConsultRequestListSerializer(serializers.ModelSerializer):
    """A lightweight serializer for listing consult requests.

    This serializer provides a condensed view of a consult request,
    suitable for list displays. It includes key denormalized fields like
    patient and department names to reduce the number of database queries.
    """
    
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    patient_mrn = serializers.CharField(source='patient.mrn', read_only=True)
    patient_location = serializers.CharField(source='patient.location', read_only=True)
    requester_name = serializers.CharField(source='requester.get_full_name', read_only=True)
    requesting_department_name = serializers.CharField(source='requesting_department.name', read_only=True)
    target_department_name = serializers.CharField(source='target_department.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.get_full_name', read_only=True)
    received_by_name = serializers.CharField(source='received_by.get_full_name', read_only=True)
    notes_count = serializers.IntegerField(source='notes.count', read_only=True)
    
    # Human-friendly fields
    created_at_human = serializers.SerializerMethodField()
    acknowledged_at_human = serializers.SerializerMethodField()
    completed_at_human = serializers.SerializerMethodField()
    urgency_color = serializers.SerializerMethodField()
    status_color = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    urgency_display = serializers.CharField(source='get_urgency_display', read_only=True)
    time_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = ConsultRequest
        fields = [
            'id',
            'patient',
            'patient_name',
            'patient_mrn',
            'patient_location',
            'requester',
            'requester_name',
            'requesting_department',
            'requesting_department_name',
            'target_department',
            'target_department_name',
            'assigned_to',
            'assigned_to_name',
            'assigned_by',
            'assigned_by_name',
            'assigned_at',
            'assigned_at_human',
            'assignment_type',
            'received_by',
            'received_by_name',
            'received_at',
            'received_at_human',
            'status',
            'status_display',
            'status_color',
            'urgency',
            'urgency_display',
            'urgency_color',
            'reason_for_consult',
            'is_overdue',
            'escalation_level',
            'notes_count',
            'created_at',
            'created_at_human',
            'acknowledged_at',
            'acknowledged_at_human',
            'completed_at',
            'completed_at_human',
            'expected_response_time',
            'time_remaining'
        ]

    def get_created_at_human(self, obj):
        """Returns a human-friendly created_at timestamp."""
        return humanize_timestamp(obj.created_at)

    def get_acknowledged_at_human(self, obj):
        """Returns a human-friendly acknowledged_at timestamp."""
        return humanize_timestamp(obj.acknowledged_at)

    def get_completed_at_human(self, obj):
        """Returns a human-friendly completed_at timestamp."""
        return humanize_timestamp(obj.completed_at)

    def get_urgency_color(self, obj):
        """Returns the color for the urgency level."""
        return get_urgency_color(obj.urgency)

    def get_status_color(self, obj):
        """Returns the color for the status."""
        return get_status_color(obj.status)

    def get_time_remaining(self, obj):
        """Returns the time remaining until SLA deadline."""
        if obj.status in ['COMPLETED', 'CANCELLED']:
            return None
        
        if not obj.expected_response_time:
            return None
        
        now = timezone.now()
        diff = obj.expected_response_time - now
        
        if diff.total_seconds() < 0:
            # Overdue
            overdue_seconds = abs(diff.total_seconds())
            if overdue_seconds < 3600:
                minutes = int(overdue_seconds / 60)
                return f'{minutes}m overdue'
            else:
                hours = int(overdue_seconds / 3600)
                return f'{hours}h overdue'
        else:
            # Time remaining
            if diff.total_seconds() < 3600:
                minutes = int(diff.total_seconds() / 60)
                return f'{minutes}m remaining'
            else:
                hours = int(diff.total_seconds() / 3600)
                return f'{hours}h remaining'


class ConsultRequestDetailSerializer(serializers.ModelSerializer):
    """A detailed serializer for a single consult request.

    This serializer provides a comprehensive view of a consult request,
    including nested representations of related objects like the patient,
    requester, and notes. It also includes calculated fields for time
    tracking and SLA compliance.
    """
    
    patient = PatientSerializer(read_only=True)
    requester = UserSerializer(read_only=True)
    requesting_department = DepartmentSerializer(read_only=True)
    target_department = DepartmentSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    assigned_by = UserSerializer(read_only=True)
    received_by = UserSerializer(read_only=True)
    notes = ConsultNoteSerializer(many=True, read_only=True)
    
    # Calculated fields
    time_elapsed = serializers.SerializerMethodField()
    time_elapsed_human = serializers.SerializerMethodField()
    time_to_acknowledgement = serializers.SerializerMethodField()
    time_to_acknowledgement_human = serializers.SerializerMethodField()
    time_to_completion = serializers.SerializerMethodField()
    time_to_completion_human = serializers.SerializerMethodField()
    sla_compliance = serializers.BooleanField(read_only=True)
    
    # Human-friendly fields
    created_at_human = serializers.SerializerMethodField()
    acknowledged_at_human = serializers.SerializerMethodField()
    received_at_human = serializers.SerializerMethodField()
    assigned_at_human = serializers.SerializerMethodField()
    completed_at_human = serializers.SerializerMethodField()
    urgency_color = serializers.SerializerMethodField()
    status_color = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    urgency_display = serializers.CharField(source='get_urgency_display', read_only=True)
    time_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = ConsultRequest
        fields = [
            'id',
            'patient',
            'requester',
            'requesting_department',
            'target_department',
            'assigned_to',
            'assigned_by',
            'assigned_at',
            'assigned_at_human',
            'assignment_type',
            'received_by',
            'received_at',
            'received_at_human',
            'status',
            'status_display',
            'status_color',
            'urgency',
            'urgency_display',
            'urgency_color',
            'reason_for_consult',
            'clinical_question',
            'relevant_history',
            'current_medications',
            'vital_signs',
            'lab_results',
            'is_overdue',
            'escalation_level',
            'created_at',
            'created_at_human',
            'updated_at',
            'acknowledged_at',
            'acknowledged_at_human',
            'received_at',
            'received_at_human',
            'assigned_at',
            'assigned_at_human',
            'completed_at',
            'completed_at_human',
            'expected_response_time',
            'time_remaining',
            'time_elapsed',
            'time_elapsed_human',
            'time_to_acknowledgement',
            'time_to_acknowledgement_human',
            'time_to_completion',
            'time_to_completion_human',
            'sla_compliance',
            'notes'
        ]
        read_only_fields = [
            'created_at',
            'updated_at',
            'acknowledged_at',
            'received_at',
            'assigned_at',
            'completed_at',
            'expected_response_time',
            'is_overdue'
        ]
    
    def get_time_elapsed(self, obj):
        """Returns the total time elapsed in seconds."""
        delta = obj.time_elapsed
        return int(delta.total_seconds()) if delta else None
    
    def get_time_elapsed_human(self, obj):
        """Returns the time elapsed in human-friendly format."""
        delta = obj.time_elapsed
        if not delta:
            return None
        
        seconds = int(delta.total_seconds())
        if seconds < 60:
            return 'less than a minute'
        elif seconds < 3600:
            minutes = seconds // 60
            return f'{minutes} minute{"s" if minutes != 1 else ""}'
        elif seconds < 86400:
            hours = seconds // 3600
            return f'{hours} hour{"s" if hours != 1 else ""}'
        else:
            days = seconds // 86400
            return f'{days} day{"s" if days != 1 else ""}'
    
    def get_time_to_acknowledgement(self, obj):
        """Returns the time to acknowledgement in seconds."""
        delta = obj.time_to_acknowledgement
        return int(delta.total_seconds()) if delta else None
    
    def get_time_to_acknowledgement_human(self, obj):
        """Returns the time to acknowledgement in human-friendly format."""
        delta = obj.time_to_acknowledgement
        if not delta:
            return None
        
        seconds = int(delta.total_seconds())
        if seconds < 60:
            return 'less than a minute'
        elif seconds < 3600:
            minutes = seconds // 60
            return f'{minutes} minute{"s" if minutes != 1 else ""}'
        else:
            hours = seconds // 3600
            return f'{hours} hour{"s" if hours != 1 else ""}'
    
    def get_time_to_completion(self, obj):
        """Returns the time to completion in seconds."""
        delta = obj.time_to_completion
        return int(delta.total_seconds()) if delta else None
    
    def get_time_to_completion_human(self, obj):
        """Returns the time to completion in human-friendly format."""
        delta = obj.time_to_completion
        if not delta:
            return None
        
        seconds = int(delta.total_seconds())
        if seconds < 60:
            return 'less than a minute'
        elif seconds < 3600:
            minutes = seconds // 60
            return f'{minutes} minute{"s" if minutes != 1 else ""}'
        elif seconds < 86400:
            hours = seconds // 3600
            return f'{hours} hour{"s" if hours != 1 else ""}'
        else:
            days = seconds // 86400
            return f'{days} day{"s" if days != 1 else ""}'

    def get_created_at_human(self, obj):
        """Returns a human-friendly created_at timestamp."""
        return humanize_timestamp(obj.created_at)

    def get_acknowledged_at_human(self, obj):
        """Returns a human-friendly acknowledged_at timestamp."""
        return humanize_timestamp(obj.acknowledged_at)
    
    def get_received_at_human(self, obj):
        """Returns a human-friendly received_at timestamp."""
        return humanize_timestamp(obj.received_at)
    
    def get_assigned_at_human(self, obj):
        """Returns a human-friendly assigned_at timestamp."""
        return humanize_timestamp(obj.assigned_at)

    def get_completed_at_human(self, obj):
        """Returns a human-friendly completed_at timestamp."""
        return humanize_timestamp(obj.completed_at)

    def get_urgency_color(self, obj):
        """Returns the color for the urgency level."""
        return get_urgency_color(obj.urgency)

    def get_status_color(self, obj):
        """Returns the color for the status."""
        return get_status_color(obj.status)

    def get_time_remaining(self, obj):
        """Returns the time remaining until SLA deadline."""
        if obj.status in ['COMPLETED', 'CANCELLED']:
            return None
        
        if not obj.expected_response_time:
            return None
        
        now = timezone.now()
        diff = obj.expected_response_time - now
        
        if diff.total_seconds() < 0:
            # Overdue
            overdue_seconds = abs(diff.total_seconds())
            if overdue_seconds < 3600:
                minutes = int(overdue_seconds / 60)
                return f'{minutes}m overdue'
            else:
                hours = int(overdue_seconds / 3600)
                return f'{hours}h overdue'
        else:
            # Time remaining
            if diff.total_seconds() < 3600:
                minutes = int(diff.total_seconds() / 60)
                return f'{minutes}m remaining'
            else:
                hours = int(diff.total_seconds() / 3600)
                return f'{hours}h remaining'


class ConsultRequestCreateSerializer(serializers.ModelSerializer):
    """A serializer for creating new consult requests.

    This serializer is used specifically for the 'create' action. It
    includes validation to ensure that the requesting and target
    departments are not the same.
    """
    
    class Meta:
        model = ConsultRequest
        fields = [
            'id',
            'patient',
            'requester',
            'requesting_department',
            'target_department',
            'urgency',
            'reason_for_consult',
            'clinical_question',
            'relevant_history',
            'current_medications',
            'vital_signs',
            'lab_results'
        ]
        read_only_fields = ['requester']
    
    def validate(self, data):
        """Ensures the requesting and target departments are different.

        Args:
            data: The data to be validated.

        Returns:
            The validated data.

        Raises:
            serializers.ValidationError: If the departments are the same.
        """
        if data['requesting_department'] == data['target_department']:
            raise serializers.ValidationError(
                "Requesting and target departments must be different."
            )
        return data
