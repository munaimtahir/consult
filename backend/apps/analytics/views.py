from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Count, F, Q, DurationField
from django.db.models.functions import Extract
from apps.accounts.models import User
from apps.consults.models import ConsultRequest

class DoctorAnalyticsViewSet(viewsets.ViewSet):
    """
    Provides analytics data for doctors.
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        Returns a list of analytics for each doctor.
        """
        analytics_data = User.objects.filter(role='DOCTOR').annotate(
            total_consults=Count('assigned_consults'),
            avg_acknowledgment_time=Avg(
                Extract(F('assigned_consults__acknowledged_at') - F('assigned_consults__created_at'), 'epoch'),
                output_field=DurationField()
            ),
            avg_completion_time=Avg(
                Extract(F('assigned_consults__completed_at') - F('assigned_consults__created_at'), 'epoch'),
                output_field=DurationField()
            ),
            pending_workload=Count('assigned_consults', filter=Q(assigned_consults__status__in=['SUBMITTED', 'ACKNOWLEDGED', 'IN_PROGRESS'])),
            escalations_handled=Count('assigned_consults', filter=Q(assigned_consults__escalation_level__gt > 0)),
            delayed_consults=Count('assigned_consults', filter=Q(assigned_consults__is_overdue=True))
        ).values(
            'id',
            'first_name',
            'last_name',
            'total_consults',
            'avg_acknowledgment_time',
            'avg_completion_time',
            'pending_workload',
            'escalations_handled',
            'delayed_consults'
        )

        return Response(list(analytics_data))
