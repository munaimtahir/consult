"""
Analytics Service
Provides methods for calculating and aggregating analytics data.
"""

from django.utils import timezone
from django.db.models import Count, Avg, Q, F
from datetime import timedelta

from apps.analytics.models import DoctorPerformanceMetric, DepartmentDailyStats, ConsultTimeline
from apps.consults.models import ConsultRequest, ConsultNote
from apps.accounts.models import User
from apps.departments.models import Department


class AnalyticsService:
    """Provides methods for analytics calculations.

    This service handles all analytics computations including
    doctor performance, department stats, and consult metrics.
    """

    @staticmethod
    def get_doctor_performance(doctor, start_date=None, end_date=None):
        """Gets performance metrics for a doctor.

        Args:
            doctor: The User instance.
            start_date: Start date for the period (default: 30 days ago).
            end_date: End date for the period (default: today).

        Returns:
            Dict with performance metrics.
        """
        if not end_date:
            end_date = timezone.now().date()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        # Get completed consults in period
        consults = ConsultRequest.objects.filter(
            assigned_to=doctor,
            completed_at__date__gte=start_date,
            completed_at__date__lte=end_date
        )

        completed_count = consults.count()
        sla_compliant = consults.filter(
            completed_at__lte=F('expected_response_time')
        ).count()

        # Calculate average response time
        completed_consults = consults.filter(acknowledged_at__isnull=False)
        if completed_consults.exists():
            total_minutes = sum(
                (c.acknowledged_at - c.created_at).total_seconds() / 60
                for c in completed_consults
            )
            avg_response = total_minutes / completed_consults.count()
        else:
            avg_response = 0

        # Get notes count
        notes_count = ConsultNote.objects.filter(
            author=doctor,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).count()

        # Get escalations
        escalations = ConsultRequest.objects.filter(
            assigned_to=doctor,
            escalation_level__gt=0,
            updated_at__date__gte=start_date,
            updated_at__date__lte=end_date
        ).count()

        return {
            'doctor_id': doctor.id,
            'doctor_name': doctor.get_full_name(),
            'period_start': start_date.isoformat(),
            'period_end': end_date.isoformat(),
            'consults_completed': completed_count,
            'sla_compliance_rate': (sla_compliant / completed_count * 100) if completed_count > 0 else 100,
            'avg_response_time_minutes': round(avg_response, 2),
            'notes_added': notes_count,
            'escalations_received': escalations,
            'active_consults': ConsultRequest.objects.filter(
                assigned_to=doctor,
                status__in=['PENDING', 'ACKNOWLEDGED', 'IN_PROGRESS']
            ).count()
        }

    @staticmethod
    def get_department_stats(department, start_date=None, end_date=None):
        """Gets statistics for a department.

        Args:
            department: The Department instance.
            start_date: Start date for the period.
            end_date: End date for the period.

        Returns:
            Dict with department statistics.
        """
        if not end_date:
            end_date = timezone.now().date()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        consults = ConsultRequest.objects.filter(
            target_department=department,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )

        total_received = consults.count()
        completed = consults.filter(status='COMPLETED').count()
        pending = consults.filter(status__in=['PENDING', 'ACKNOWLEDGED']).count()
        in_progress = consults.filter(status='IN_PROGRESS').count()
        overdue = consults.filter(is_overdue=True).exclude(status='COMPLETED').count()
        escalated = consults.filter(escalation_level__gt=0).count()

        # SLA compliance
        completed_consults = consults.filter(status='COMPLETED')
        sla_compliant = completed_consults.filter(
            completed_at__lte=F('expected_response_time')
        ).count()

        # Average response time
        acked_consults = consults.filter(acknowledged_at__isnull=False)
        if acked_consults.exists():
            total_minutes = sum(
                (c.acknowledged_at - c.created_at).total_seconds() / 60
                for c in acked_consults
            )
            avg_response = total_minutes / acked_consults.count()
        else:
            avg_response = 0

        # Urgency breakdown
        urgency_breakdown = {
            'emergency': consults.filter(urgency='EMERGENCY').count(),
            'urgent': consults.filter(urgency='URGENT').count(),
            'routine': consults.filter(urgency='ROUTINE').count(),
        }

        return {
            'department_id': department.id,
            'department_name': department.name,
            'period_start': start_date.isoformat(),
            'period_end': end_date.isoformat(),
            'total_received': total_received,
            'completed': completed,
            'pending': pending,
            'in_progress': in_progress,
            'overdue': overdue,
            'escalated': escalated,
            'sla_compliance_rate': (sla_compliant / completed * 100) if completed > 0 else 100,
            'avg_response_time_minutes': round(avg_response, 2),
            'urgency_breakdown': urgency_breakdown,
            'completion_rate': (completed / total_received * 100) if total_received > 0 else 0
        }

    @staticmethod
    def get_global_stats(start_date=None, end_date=None):
        """Gets system-wide statistics.

        Args:
            start_date: Start date for the period.
            end_date: End date for the period.

        Returns:
            Dict with global statistics.
        """
        if not end_date:
            end_date = timezone.now().date()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        consults = ConsultRequest.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )

        total = consults.count()
        completed = consults.filter(status='COMPLETED').count()
        active = consults.exclude(status__in=['COMPLETED', 'CANCELLED']).count()
        overdue = consults.filter(is_overdue=True).exclude(status='COMPLETED').count()

        # SLA compliance
        completed_consults = consults.filter(status='COMPLETED', completed_at__isnull=False)
        sla_compliant = completed_consults.filter(
            completed_at__lte=F('expected_response_time')
        ).count()

        # Department ranking
        department_stats = []
        for dept in Department.objects.filter(is_active=True):
            dept_consults = consults.filter(target_department=dept)
            dept_completed = dept_consults.filter(status='COMPLETED').count()
            dept_total = dept_consults.count()
            
            dept_completed_consults = dept_consults.filter(status='COMPLETED')
            dept_sla_compliant = dept_completed_consults.filter(
                completed_at__lte=F('expected_response_time')
            ).count()

            department_stats.append({
                'department_id': dept.id,
                'department_name': dept.name,
                'total_consults': dept_total,
                'completed': dept_completed,
                'sla_compliance_rate': (dept_sla_compliant / dept_completed * 100) if dept_completed > 0 else 100
            })

        # Sort by SLA compliance
        department_stats.sort(key=lambda x: x['sla_compliance_rate'], reverse=True)

        return {
            'period_start': start_date.isoformat(),
            'period_end': end_date.isoformat(),
            'total_consults': total,
            'completed': completed,
            'active': active,
            'overdue': overdue,
            'sla_compliance_rate': (sla_compliant / completed * 100) if completed > 0 else 100,
            'department_ranking': department_stats[:10]
        }

    @staticmethod
    def add_timeline_event(consult, event_type, actor=None, description=None, metadata=None):
        """Adds a timeline event for a consult.

        Args:
            consult: The ConsultRequest instance.
            event_type: The event type string.
            actor: Optional User who triggered the event.
            description: Optional description (auto-generated if not provided).
            metadata: Optional additional data dict.

        Returns:
            The created ConsultTimeline instance.
        """
        if not description:
            description = AnalyticsService._generate_event_description(
                event_type,
                actor,
                metadata
            )

        return ConsultTimeline.objects.create(
            consult=consult,
            event_type=event_type,
            actor=actor,
            description=description,
            metadata=metadata or {}
        )

    @staticmethod
    def _generate_event_description(event_type, actor, metadata):
        """Generates a description for a timeline event."""
        actor_name = actor.get_full_name() if actor else 'System'
        
        descriptions = {
            'CREATED': f'Consult created by {actor_name}',
            'ACKNOWLEDGED': f'Consult acknowledged by {actor_name}',
            'ASSIGNED': f'Consult assigned to {metadata.get("assigned_to", "unknown")}' if metadata else f'Consult assigned by {actor_name}',
            'REASSIGNED': f'Consult reassigned by {actor_name}',
            'NOTE_ADDED': f'Note added by {actor_name}',
            'STATUS_CHANGED': f'Status changed to {metadata.get("new_status", "unknown")}' if metadata else f'Status changed by {actor_name}',
            'ESCALATED': f'Consult escalated to level {metadata.get("level", "unknown")}' if metadata else 'Consult escalated',
            'COMPLETED': f'Consult completed by {actor_name}',
            'CANCELLED': f'Consult cancelled by {actor_name}',
            'SLA_WARNING': 'SLA deadline approaching',
            'SLA_BREACH': 'SLA deadline exceeded',
        }
        
        return descriptions.get(event_type, f'{event_type} by {actor_name}')

    @staticmethod
    def get_consult_timeline(consult):
        """Gets the timeline for a consult.

        Args:
            consult: The ConsultRequest instance.

        Returns:
            List of timeline events.
        """
        events = ConsultTimeline.objects.filter(
            consult=consult
        ).select_related('actor').order_by('timestamp')

        return [
            {
                'id': event.id,
                'event_type': event.event_type,
                'event_display': event.get_event_type_display(),
                'actor': {
                    'id': event.actor.id,
                    'name': event.actor.get_full_name()
                } if event.actor else None,
                'description': event.description,
                'metadata': event.metadata,
                'timestamp': event.timestamp.isoformat(),
                'timestamp_human': AnalyticsService._humanize_timestamp(event.timestamp)
            }
            for event in events
        ]

    @staticmethod
    def _humanize_timestamp(timestamp):
        """Converts a timestamp to a human-friendly format."""
        now = timezone.now()
        diff = now - timestamp

        if diff.total_seconds() < 60:
            return 'just now'
        elif diff.total_seconds() < 3600:
            minutes = int(diff.total_seconds() / 60)
            return f'{minutes} minute{"s" if minutes != 1 else ""} ago'
        elif diff.total_seconds() < 86400:
            hours = int(diff.total_seconds() / 3600)
            return f'{hours} hour{"s" if hours != 1 else ""} ago'
        elif diff.days == 1:
            return 'yesterday'
        elif diff.days < 7:
            return f'{diff.days} days ago'
        else:
            return timestamp.strftime('%b %d, %Y at %I:%M %p')

    @staticmethod
    def calculate_daily_stats(date=None):
        """Calculates and stores daily statistics.

        Args:
            date: The date to calculate for (default: yesterday).

        Returns:
            Number of records created/updated.
        """
        if not date:
            date = (timezone.now() - timedelta(days=1)).date()

        count = 0

        # Update department stats
        for dept in Department.objects.filter(is_active=True):
            stats = AnalyticsService.get_department_stats(dept, date, date)
            
            DepartmentDailyStats.objects.update_or_create(
                department=dept,
                date=date,
                defaults={
                    'consults_received': stats['total_received'],
                    'consults_completed': stats['completed'],
                    'consults_escalated': stats['escalated'],
                    'consults_pending': stats['pending'],
                    'consults_overdue': stats['overdue'],
                    'avg_response_time_minutes': stats['avg_response_time_minutes'],
                    'sla_compliance_rate': stats['sla_compliance_rate']
                }
            )
            count += 1

        # Update doctor stats
        for doctor in User.objects.filter(
            is_active=True,
            role__in=['DOCTOR', 'HOD', 'DEPARTMENT_USER']
        ):
            perf = AnalyticsService.get_doctor_performance(doctor, date, date)
            
            DoctorPerformanceMetric.objects.update_or_create(
                doctor=doctor,
                date=date,
                defaults={
                    'consults_assigned': perf['active_consults'],
                    'consults_completed': perf['consults_completed'],
                    'avg_response_time_minutes': perf['avg_response_time_minutes'],
                    'sla_compliance_rate': perf['sla_compliance_rate'],
                    'notes_added': perf['notes_added'],
                    'escalations_received': perf['escalations_received']
                }
            )
            count += 1

        return count
