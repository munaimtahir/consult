"""
Admin configuration for Departments app.
"""

from django.contrib import admin
from .models import Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = [
        'code',
        'name',
        'head',
        'contact_number',
        'is_active',
        'created_at'
    ]
    list_filter = [
        'is_active',
        'created_at'
    ]
    search_fields = [
        'name',
        'code'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'head', 'contact_number', 'is_active')
        }),
        ('SLA Configuration', {
            'fields': ('emergency_sla', 'urgent_sla', 'routine_sla'),
            'description': 'Service Level Agreement times in minutes'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )
