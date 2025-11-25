"""
Serializers for Patients app.
"""

from rest_framework import serializers
from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    """Serializer for Patient model."""
    
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
    """Lightweight serializer for list views."""
    
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
