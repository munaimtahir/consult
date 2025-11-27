"""
Serializers for Patients app.
"""

from rest_framework import serializers
from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    """Serializes the `Patient` model for detailed views.

    This serializer includes detailed information about a patient,
    including their location, primary department name, and the number of
    consults they have.
    """
    
    location = serializers.CharField(read_only=True)
    primary_department_name = serializers.CharField(source='primary_department.name', read_only=True)
    consults_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Patient
        fields = [
            'id',
            'mrn',
            'name',
            'age',
            'gender',
            'ward',
            'bed_number',
            'location',
            'primary_department',
            'primary_department_name',
            'primary_diagnosis',
            'consults_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class PatientListSerializer(serializers.ModelSerializer):
    """A lightweight serializer for listing patients.

    This serializer provides a minimal set of patient fields, optimized for
    use in list views.
    """
    
    location = serializers.CharField(read_only=True)
    primary_department_name = serializers.CharField(source='primary_department.name', read_only=True)
    
    class Meta:
        model = Patient
        fields = [
            'id',
            'mrn',
            'name',
            'age',
            'gender',
            'location',
            'primary_department_name',
            'created_at'
        ]
