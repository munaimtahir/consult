"""
Admin configuration for Patients app.
"""

from django.contrib import admin
from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = [
        'mrn',
        'name',
        'age',
        'gender',
        'ward',
        'bed_number',
        'primary_department',
        'created_at'
    ]
    list_filter = [
        'gender',
        'primary_department',
        'ward',
        'created_at'
    ]
    search_fields = [
        'mrn',
        'name',
        'primary_diagnosis'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('mrn', 'name', 'age', 'gender')
        }),
        ('Location', {
            'fields': ('ward', 'bed_number', 'primary_department')
        }),
        ('Clinical', {
            'fields': ('primary_diagnosis',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )
