from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'full_name', 'program', 'mobile', 'email', 'is_active', 'created_at']
    list_filter = ['is_active', 'gender', 'program', 'created_at']
    search_fields = ['student_id', 'full_name', 'cnic_or_bform', 'mobile', 'email', 'mdcat_roll_number']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
