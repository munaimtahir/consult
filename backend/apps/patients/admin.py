"""
Django admin configuration for Patient model.
"""

from django.contrib import admin
from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    """
    Patient admin with search and filtering.
    """
    
    list_display = ['mrn', 'name', 'age', 'gender', 'location', 'primary_department', 'consults_count']
    list_filter = ['gender', 'primary_department']
    search_fields = ['mrn', 'name']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('mrn', 'name', 'age', 'gender')
        }),
        ('Location', {
            'fields': ('ward', 'bed_number', 'primary_department')
        }),
        ('Medical Information', {
            'fields': ('primary_diagnosis',)
        }),
    )
    
    def consults_count(self, obj):
        return obj.consults_count
    consults_count.short_description = 'Consults'
