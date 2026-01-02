from django.contrib import admin
from .models import Program, Term


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'duration_years', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['code', 'name']
    ordering = ['code']


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'academic_year', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active', 'academic_year', 'start_date']
    search_fields = ['code', 'name', 'academic_year']
    ordering = ['-start_date', 'code']
