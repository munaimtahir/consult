"""
Admin configuration for Consults app.
"""

from django.contrib import admin
from .models import ConsultRequest, ConsultNote


@admin.register(ConsultRequest)
class ConsultRequestAdmin(admin.ModelAdmin):
    """Customizes the Django admin interface for the `ConsultRequest` model.

    Provides a more organized and user-friendly interface for managing
    consult requests in the admin panel, including detailed list displays,
    filters, and search capabilities.
    """
    list_display = [
        'id',
        'patient',
        'urgency',
        'status',
        'target_department',
        'assigned_to',
        'is_overdue',
        'created_at'
    ]
    list_filter = [
        'status',
        'urgency',
        'target_department',
        'is_overdue',
        'created_at'
    ]
    search_fields = [
        'patient__name',
        'patient__mrn',
        'reason_for_consult',
        'clinical_question'
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'acknowledged_at',
        'completed_at',
        'expected_response_time',
        'is_overdue'
    ]
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient',)
        }),
        ('Request Details', {
            'fields': (
                'requester',
                'requesting_department',
                'target_department',
                'assigned_to',
                'status',
                'urgency'
            )
        }),
        ('Clinical Information', {
            'fields': (
                'reason_for_consult',
                'clinical_question',
                'relevant_history',
                'current_medications',
                'vital_signs',
                'lab_results'
            )
        }),
        ('SLA & Tracking', {
            'fields': (
                'expected_response_time',
                'is_overdue',
                'escalation_level'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
                'acknowledged_at',
                'completed_at'
            )
        }),
    )
    
    def get_queryset(self, request):
        """Optimizes the queryset by pre-fetching related objects.

        Args:
            request: The Django HttpRequest object.

        Returns:
            The optimized queryset.
        """
        return super().get_queryset(request).select_related(
            'patient',
            'requester',
            'requesting_department',
            'target_department',
            'assigned_to'
        )


@admin.register(ConsultNote)
class ConsultNoteAdmin(admin.ModelAdmin):
    """Customizes the Django admin interface for the `ConsultNote` model.

    Provides a clear and manageable interface for consult notes in the
    admin panel.
    """
    list_display = [
        'id',
        'consult',
        'author',
        'note_type',
        'is_final',
        'created_at'
    ]
    list_filter = [
        'note_type',
        'is_final',
        'follow_up_required',
        'created_at'
    ]
    search_fields = [
        'consult__patient__name',
        'consult__patient__mrn',
        'content',
        'recommendations'
    ]
    readonly_fields = [
        'created_at',
        'updated_at'
    ]
    fieldsets = (
        ('Note Details', {
            'fields': (
                'consult',
                'author',
                'note_type',
                'content'
            )
        }),
        ('Recommendations', {
            'fields': (
                'recommendations',
                'follow_up_required',
                'follow_up_instructions'
            )
        }),
        ('Metadata', {
            'fields': (
                'is_final',
                'created_at',
                'updated_at'
            )
        }),
    )
    
    def get_queryset(self, request):
        """Optimizes the queryset by pre-fetching related objects.

        Args:
            request: The Django HttpRequest object.

        Returns:
            The optimized queryset.
        """
        return super().get_queryset(request).select_related(
            'consult__patient',
            'author'
        )
