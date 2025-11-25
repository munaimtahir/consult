"""
Serializers for Consults app.
"""

from rest_framework import serializers
from .models import ConsultRequest, ConsultNote
from apps.patients.serializers import PatientSerializer
from apps.accounts.serializers import UserSerializer
from apps.departments.serializers import DepartmentSerializer


class ConsultNoteSerializer(serializers.ModelSerializer):
    """Serializer for ConsultNote model."""
    
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    author_designation = serializers.CharField(source='author.designation_display', read_only=True)
    
    class Meta:
        model = ConsultNote
        fields = [
            'id',
            'consult',
            'author',
            'author_name',
            'author_designation',
            'note_type',
            'content',
            'recommendations',
            'follow_up_required',
            'follow_up_instructions',
            'is_final',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ConsultRequestListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    patient_mrn = serializers.CharField(source='patient.mrn', read_only=True)
    patient_location = serializers.CharField(source='patient.location', read_only=True)
    requester_name = serializers.CharField(source='requester.get_full_name', read_only=True)
    requesting_department_name = serializers.CharField(source='requesting_department.name', read_only=True)
    target_department_name = serializers.CharField(source='target_department.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    notes_count = serializers.IntegerField(source='notes.count', read_only=True)
    
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
            'status',
            'urgency',
            'reason_for_consult',
            'is_overdue',
            'notes_count',
            'created_at',
            'acknowledged_at',
            'completed_at',
            'expected_response_time'
        ]


class ConsultRequestDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer with nested relationships."""
    
    patient = PatientSerializer(read_only=True)
    requester = UserSerializer(read_only=True)
    requesting_department = DepartmentSerializer(read_only=True)
    target_department = DepartmentSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    notes = ConsultNoteSerializer(many=True, read_only=True)
    
    # Calculated fields
    time_elapsed = serializers.SerializerMethodField()
    time_to_acknowledgement = serializers.SerializerMethodField()
    time_to_completion = serializers.SerializerMethodField()
    sla_compliance = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ConsultRequest
        fields = [
            'id',
            'patient',
            'requester',
            'requesting_department',
            'target_department',
            'assigned_to',
            'status',
            'urgency',
            'reason_for_consult',
            'clinical_question',
            'relevant_history',
            'current_medications',
            'vital_signs',
            'lab_results',
            'is_overdue',
            'escalation_level',
            'created_at',
            'updated_at',
            'acknowledged_at',
            'completed_at',
            'expected_response_time',
            'time_elapsed',
            'time_to_acknowledgement',
            'time_to_completion',
            'sla_compliance',
            'notes'
        ]
        read_only_fields = [
            'created_at',
            'updated_at',
            'acknowledged_at',
            'completed_at',
            'expected_response_time',
            'is_overdue'
        ]
    
    def get_time_elapsed(self, obj):
        """Get time elapsed in seconds."""
        delta = obj.time_elapsed
        return int(delta.total_seconds()) if delta else None
    
    def get_time_to_acknowledgement(self, obj):
        """Get time to acknowledgement in seconds."""
        delta = obj.time_to_acknowledgement
        return int(delta.total_seconds()) if delta else None
    
    def get_time_to_completion(self, obj):
        """Get time to completion in seconds."""
        delta = obj.time_to_completion
        return int(delta.total_seconds()) if delta else None


class ConsultRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new consult requests."""
    
    class Meta:
        model = ConsultRequest
        fields = [
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
    
    def validate(self, data):
        """Validate that requesting and target departments are different."""
        if data['requesting_department'] == data['target_department']:
            raise serializers.ValidationError(
                "Requesting and target departments must be different."
            )
        return data
