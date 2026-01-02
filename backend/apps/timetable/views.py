"""
Views for Timetable app.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from datetime import datetime, timedelta

from .models import WeekPlan, WeekChangeLog, SessionOccurrence
from .serializers import (
    WeekPlanListSerializer,
    WeekPlanDetailSerializer,
    WeekGridSaveSerializer,
    WeekChangeLogSerializer,
    SessionOccurrenceSerializer
)
from .services import TimetableService, get_monday
from .permissions import (
    CanEditTimetable,
    CanVerifyTimetable,
    CanPublishTimetable,
    CanRevertTimetable
)
from .exceptions import TimetableValidationError


class WeekPlanViewSet(viewsets.ModelViewSet):
    """ViewSet for managing week plans."""
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get queryset with optional filtering."""
        queryset = WeekPlan.objects.select_related(
            'created_by',
            'verified_by',
            'published_by'
        ).prefetch_related('slot_rows', 'cells__department')
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date:
            queryset = queryset.filter(week_start_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(week_start_date__lte=end_date)
        
        return queryset.order_by('-week_start_date')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return WeekPlanListSerializer
        return WeekPlanDetailSerializer
    
    def get_permissions(self):
        """Instantiate and return permissions for this view."""
        if self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), CanEditTimetable()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['post'])
    def create_week(self, request):
        """Create a single week plan."""
        week_start_date = request.data.get('week_start_date')
        if not week_start_date:
            return Response(
                {'error': 'week_start_date is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            date_obj = datetime.strptime(week_start_date, '%Y-%m-%d').date()
            week_plan = TimetableService.create_week(date_obj, request.user)
            serializer = WeekPlanDetailSerializer(week_plan)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except TimetableValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def create_next_4_weeks(self, request):
        """Create the next 4 weeks."""
        from_week_start = request.data.get('from_week_start', None)
        date_obj = None
        
        if from_week_start:
            try:
                date_obj = datetime.strptime(from_week_start, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        try:
            week_plans = TimetableService.create_next_4_weeks(date_obj, request.user)
            serializer = WeekPlanListSerializer(week_plans, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except TimetableValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def save_grid(self, request, pk=None):
        """Bulk save grid data (rows and cells)."""
        week_plan = self.get_object()
        
        # Check permissions
        if not week_plan.can_edit(request.user):
            return Response(
                {'error': 'You do not have permission to edit this week'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = WeekGridSaveSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            updated_week = TimetableService.bulk_save_grid(
                week_plan.id,
                serializer.validated_data['rows'],
                serializer.validated_data['cells'],
                request.user
            )
            result_serializer = WeekPlanDetailSerializer(updated_week)
            return Response(result_serializer.data)
        except TimetableValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify a draft week."""
        week_plan = self.get_object()
        
        if not CanVerifyTimetable().has_object_permission(request, self, week_plan):
            return Response(
                {'error': 'You do not have permission to verify this week'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            updated_week = TimetableService.verify_week(week_plan.id, request.user)
            serializer = WeekPlanDetailSerializer(updated_week)
            return Response(serializer.data)
        except TimetableValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish a verified week."""
        week_plan = self.get_object()
        
        if not CanPublishTimetable().has_object_permission(request, self, week_plan):
            return Response(
                {'error': 'You do not have permission to publish this week'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            updated_week = TimetableService.publish_week(week_plan.id, request.user)
            serializer = WeekPlanDetailSerializer(updated_week)
            return Response(serializer.data)
        except TimetableValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def revert_to_draft(self, request, pk=None):
        """Revert a verified/published week to draft."""
        week_plan = self.get_object()
        
        if not CanRevertTimetable().has_object_permission(request, self, week_plan):
            return Response(
                {'error': 'You do not have permission to revert this week'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        reason = request.data.get('reason', '')
        if not reason:
            return Response(
                {'error': 'Reason is required for reverting'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            updated_week = TimetableService.revert_to_draft(
                week_plan.id,
                request.user,
                reason
            )
            serializer = WeekPlanDetailSerializer(updated_week)
            return Response(serializer.data)
        except TimetableValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def change_logs(self, request, pk=None):
        """Get change logs for a week plan."""
        week_plan = self.get_object()
        logs = WeekChangeLog.objects.filter(week_plan=week_plan).order_by('-created_at')
        serializer = WeekChangeLogSerializer(logs, many=True)
        return Response(serializer.data)


class SessionOccurrenceViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing session occurrences."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = SessionOccurrenceSerializer
    
    def get_queryset(self):
        """Get queryset with optional filtering."""
        queryset = SessionOccurrence.objects.select_related(
            'week_plan',
            'department'
        )
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        # Filter by department
        department_id = self.request.query_params.get('department_id', None)
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        
        # Filter by week_plan
        week_plan_id = self.request.query_params.get('week_plan_id', None)
        if week_plan_id:
            queryset = queryset.filter(week_plan_id=week_plan_id)
        
        return queryset.order_by('date', 'start_time')
