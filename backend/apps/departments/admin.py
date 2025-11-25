"""
Django admin configuration for Department model.
"""

from django.contrib import admin
from .models import Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """
    Department admin with user count display.
    """
    
    list_display = ['name', 'code', 'head', 'user_count', 'active_consults_count', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'head', 'contact_number', 'is_active')
        }),
        ('SLA Configuration', {
            'fields': ('emergency_sla', 'urgent_sla', 'routine_sla'),
            'description': 'Service Level Agreements in minutes'
        }),
    )
    
    def user_count(self, obj):
        return obj.user_count
    user_count.short_description = 'Users'
    
    def active_consults_count(self, obj):
        return obj.active_consults_count
    active_consults_count.short_description = 'Active Consults'
