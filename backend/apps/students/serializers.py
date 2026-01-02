"""
Serializers for Students app.
"""

from rest_framework import serializers
from .models import Student


class StudentSerializer(serializers.ModelSerializer):
    """Serializer for Student."""
    
    program_name = serializers.CharField(source='program.name', read_only=True)
    program_code = serializers.CharField(source='program.code', read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'id', 'student_id', 'full_name', 'father_name',
            'gender', 'gender_display', 'date_of_birth',
            'cnic_or_bform', 'mobile', 'email', 'address',
            'program', 'program_name', 'program_code',
            'admission_date', 'mdcat_roll_number',
            'merit_number', 'merit_percentage',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['student_id', 'created_at', 'updated_at']
