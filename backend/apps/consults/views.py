"""
Views for Consults app.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q, Count, Prefetch

from .models import ConsultRequest, ConsultNote
from .serializers import (
    ConsultRequestListSerializer,
    ConsultRequestDetailSerializer,
    ConsultRequestCreateSerializer,
    ConsultNoteSerializer
)


class ConsultRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ConsultRequest model.
    Provides CRUD operations and custom actions for consult workflow.
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter queryset based on user role and permissions.
        """
        user = self.request.user
        queryset = ConsultRequest.objects.select_related(
            'patient',
            'requester',
            'requesting_department',
            'target_department',
            'assigned_to'
        ).prefetch_related('notes')
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by urgency if provided
        urgency_filter = self.request.query_params.get('urgency', None)
        if urgency_filter:
            queryset = queryset.filter(urgency=urgency_filter)
        
        # Filter by overdue if provided
        is_overdue = self.request.query_params.get('is_overdue', None)
        if is_overdue is not None:
            queryset = queryset.filter(is_overdue=is_overdue.lower() == 'true')
        
        # Role-based filtering
        view_type = self.request.query_params.get('view', 'all')
        
        if view_type == 'my_department':
            # Consults for my department
            queryset = queryset.filter(target_department=user.department)
        elif view_type == 'assigned_to_me':
            # Consults assigned to me
            queryset = queryset.filter(assigned_to=user)
        elif view_type == 'my_requests':
            # Consults I requested
            queryset = queryset.filter(requester=user)
        elif view_type == 'pending_assignment':
            # Pending consults in my department
            queryset = queryset.filter(
                target_department=user.department,
                status__in=['PENDING', 'ACKNOWLEDGED'],
                assigned_to__isnull=True
            )
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        """
        if self.action == 'list':
            return ConsultRequestListSerializer
        elif self.action == 'create':
            return ConsultRequestCreateSerializer
        return ConsultRequestDetailSerializer
    
    def perform_create(self, serializer):
        """
        Set requester to current user on creation.
        """
        serializer.save(requester=self.request.user)
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """
        Acknowledge a consult request.
        """
        consult = self.get_object()
        
        # Check permissions
        if request.user.department != consult.target_department:
            return Response(
                {'error': 'You can only acknowledge consults for your department'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if consult.status != 'PENDING':
            return Response(
                {'error': 'Only pending consults can be acknowledged'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        consult.status = 'ACKNOWLEDGED'
        consult.acknowledged_at = timezone.now()
        consult.save()
        
        serializer = self.get_serializer(consult)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """
        Assign a consult to a specific user.
        """
        consult = self.get_object()
        
        # Check permissions - only HOD or admins can assign
        if not request.user.can_assign_consults:
            return Response(
                {'error': 'You do not have permission to assign consults'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if request.user.department != consult.target_department:
            return Response(
                {'error': 'You can only assign consults in your department'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get the assigned user
        assigned_to_id = request.data.get('assigned_to')
        if not assigned_to_id:
            return Response(
                {'error': 'Please provide assigned_to user ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from apps.accounts.models import User
        try:
            assigned_user = User.objects.get(id=assigned_to_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check that assigned user is in the target department
        if assigned_user.department != consult.target_department:
            return Response(
                {'error': 'User must be in the target department'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        consult.assigned_to = assigned_user
        if consult.status == 'PENDING':
            consult.status = 'ACKNOWLEDGED'
            consult.acknowledged_at = timezone.now()
        elif consult.status == 'ACKNOWLEDGED':
            consult.status = 'IN_PROGRESS'
        consult.save()
        
        serializer = self.get_serializer(consult)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_note(self, request, pk=None):
        """
        Add a note to the consult.
        """
        consult = self.get_object()
        
        # Check permissions - must be assigned or in target department
        if (request.user != consult.assigned_to and 
            request.user.department != consult.target_department and
            not request.user.can_assign_consults):
            return Response(
                {'error': 'You do not have permission to add notes to this consult'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ConsultNoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(consult=consult, author=request.user)
            
            # Update consult status
            if consult.status == 'ACKNOWLEDGED':
                consult.status = 'IN_PROGRESS'
                consult.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Mark consult as completed.
        """
        consult = self.get_object()
        
        # Check permissions
        if (request.user != consult.assigned_to and 
            not request.user.can_assign_consults):
            return Response(
                {'error': 'Only the assigned doctor or HOD can complete a consult'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        consult.status = 'COMPLETED'
        consult.completed_at = timezone.now()
        consult.save()
        
        serializer = self.get_serializer(consult)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel a consult request.
        """
        consult = self.get_object()
        
        # Check permissions - only requester or admins can cancel
        if request.user != consult.requester and not request.user.is_admin_user:
            return Response(
                {'error': 'Only the requester or admin can cancel a consult'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if consult.status == 'COMPLETED':
            return Response(
                {'error': 'Cannot cancel a completed consult'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        consult.status = 'CANCELLED'
        consult.save()
        
        serializer = self.get_serializer(consult)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """
        Get dashboard statistics for the current user.
        """
        user = request.user
        
        # Stats for my department
        my_dept_consults = ConsultRequest.objects.filter(
            target_department=user.department
        )
        
        # Stats for consults assigned to me
        my_consults = ConsultRequest.objects.filter(assigned_to=user)
        
        stats = {
            'my_department': {
                'pending': my_dept_consults.filter(status='PENDING').count(),
                'in_progress': my_dept_consults.filter(status='IN_PROGRESS').count(),
                'overdue': my_dept_consults.filter(is_overdue=True).exclude(status='COMPLETED').count(),
                'total_active': my_dept_consults.exclude(status__in=['COMPLETED', 'CANCELLED']).count(),
            },
            'assigned_to_me': {
                'pending': my_consults.filter(status__in=['PENDING', 'ACKNOWLEDGED']).count(),
                'in_progress': my_consults.filter(status='IN_PROGRESS').count(),
                'overdue': my_consults.filter(is_overdue=True).exclude(status='COMPLETED').count(),
            },
            'my_requests': {
                'pending': ConsultRequest.objects.filter(
                    requester=user,
                    status__in=['PENDING', 'ACKNOWLEDGED']
                ).count(),
                'in_progress': ConsultRequest.objects.filter(
                    requester=user,
                    status='IN_PROGRESS'
                ).count(),
                'completed': ConsultRequest.objects.filter(
                    requester=user,
                    status='COMPLETED'
                ).count(),
            }
        }
        
        return Response(stats)


class ConsultNoteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ConsultNote model.
    Provides CRUD operations for consult notes.
    """
    
    serializer_class = ConsultNoteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter notes based on consult access.
        """
        user = self.request.user
        queryset = ConsultNote.objects.select_related(
            'consult',
            'author'
        )
        
        # Filter by consult if provided
        consult_id = self.request.query_params.get('consult', None)
        if consult_id:
            queryset = queryset.filter(consult_id=consult_id)
        
        return queryset.order_by('created_at')
    
    def perform_create(self, serializer):
        """
        Set author to current user on creation.
        """
        serializer.save(author=self.request.user)
