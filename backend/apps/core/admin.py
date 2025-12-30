from django.contrib import admin
from .models import EmailNotificationSettings, SMTPConfiguration


@admin.register(EmailNotificationSettings)
class EmailNotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ['department', 'notify_on_consult_generated', 'notify_on_sla_breach', 'updated_at']
    list_filter = ['notify_on_consult_generated', 'notify_on_sla_breach']
    search_fields = ['department__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SMTPConfiguration)
class SMTPConfigurationAdmin(admin.ModelAdmin):
    list_display = ['name', 'host', 'username', 'from_email', 'is_active', 'is_test_mode', 'created_at']
    list_filter = ['is_active', 'is_test_mode', 'created_at']
    search_fields = ['name', 'host', 'username', 'from_email']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
