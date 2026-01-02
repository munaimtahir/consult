"""
Admin configuration for Timetable app.
"""

from django.contrib import admin
from .models import WeekPlan, WeekSlotRow, WeekCell, WeekChangeLog, SessionOccurrence


@admin.register(WeekPlan)
class WeekPlanAdmin(admin.ModelAdmin):
    """Admin interface for WeekPlan."""
    list_display = [
        'week_start_date',
        'status',
        'created_by',
        'verified_by',
        'published_by',
        'created_at'
    ]
    list_filter = ['status', 'week_start_date', 'created_at']
    search_fields = ['week_start_date']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'week_start_date'


@admin.register(WeekSlotRow)
class WeekSlotRowAdmin(admin.ModelAdmin):
    """Admin interface for WeekSlotRow."""
    list_display = ['week_plan', 'row_index', 'start_time', 'end_time']
    list_filter = ['week_plan']
    ordering = ['week_plan', 'row_index']


@admin.register(WeekCell)
class WeekCellAdmin(admin.ModelAdmin):
    """Admin interface for WeekCell."""
    list_display = [
        'week_plan',
        'day_of_week',
        'slot_row',
        'department',
        'faculty_name',
        'status'
    ]
    list_filter = ['week_plan', 'day_of_week', 'department', 'status']
    search_fields = ['topic', 'faculty_name', 'department__name']
    ordering = ['week_plan', 'day_of_week', 'slot_row__row_index']


@admin.register(WeekChangeLog)
class WeekChangeLogAdmin(admin.ModelAdmin):
    """Admin interface for WeekChangeLog."""
    list_display = [
        'week_plan',
        'changed_by',
        'change_reason',
        'created_at'
    ]
    list_filter = ['week_plan', 'created_at']
    search_fields = ['change_reason', 'changed_by__email']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(SessionOccurrence)
class SessionOccurrenceAdmin(admin.ModelAdmin):
    """Admin interface for SessionOccurrence."""
    list_display = [
        'date',
        'start_time',
        'end_time',
        'department',
        'faculty_name',
        'status'
    ]
    list_filter = ['date', 'department', 'status']
    search_fields = ['topic', 'faculty_name', 'department__name']
    date_hierarchy = 'date'
    ordering = ['date', 'start_time']
