from django.contrib import admin
from .models import Device


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['user', 'device_id', 'platform', 'is_active', 'created_at', 'updated_at']
    list_filter = ['platform', 'is_active', 'created_at']
    search_fields = ['user__email', 'device_id']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']
