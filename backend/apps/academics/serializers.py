"""
Serializers for Academics app.
"""

from rest_framework import serializers
from .models import Program, Term


class ProgramSerializer(serializers.ModelSerializer):
    """Serializer for Program."""
    
    class Meta:
        model = Program
        fields = [
            'id', 'code', 'name', 'description',
            'duration_years', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class TermSerializer(serializers.ModelSerializer):
    """Serializer for Term."""
    
    class Meta:
        model = Term
        fields = [
            'id', 'code', 'name', 'academic_year',
            'start_date', 'end_date', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
