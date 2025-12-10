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


from .permissions import IsConsultParticipant, CanAssignConsult

class ConsultRequestViewSet(viewsets.ModelViewSet):
    """Provides API endpoints for managing consult requests.

    This ViewSet handles the entire lifecycle of a consult request, from
    creation to completion. It includes standard CRUD operations as well as
    custom actions for workflow management, such as acknowledging,
    assigning, and adding notes to a consult.

    Access is restricted to authenticated users, and the queryset is
    dynamically filtered based on the user's role and permissions.
    """
    
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsConsultParticipant()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Constructs the queryset for the view, with dynamic filtering.

        This method applies filters based on the user's role and query
        parameters. It allows filtering by status, urgency, overdue status,
        and provides different views ('my_department', 'assigned_to_me', etc.).

        Returns:
            A Django QuerySet of `ConsultRequest` objects.
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
        """Selects the appropriate serializer for the current action.

        Uses `ConsultRequestListSerializer` for 'list',
        `ConsultRequestCreateSerializer` for 'create', and
        `ConsultRequestDetailSerializer` for all other actions.

        Returns:
            The serializer class to be used for the request.
        """
        if self.action == 'list':
            return ConsultRequestListSerializer
        elif self.action == 'create':
            return ConsultRequestCreateSerializer
        return ConsultRequestDetailSerializer
    
    def perform_create(self, serializer):
        """Sets the requester and triggers notifications on creation.

        This method is called after the serializer has been validated and is
        ready to be saved. It sets the `requester` to the current user and
        then calls the `NotificationService` to send out notifications about
        the new consult.

        Args:
            serializer: The serializer instance.
        """
        from .services import ConsultService
        
        # We need to extract data from serializer to pass to service
        # But serializer.save() does a lot of work. 
        # For now, let's let serializer save, but we might want to move creation logic to service fully later.
        # Actually, to strictly follow service pattern:
        # serializer.save(requester=self.request.user)
        # ConsultService.notify_new_consult(serializer.instance)
        
        # Better approach:
        # 1. Validate data
        # 2. Call service
        
        # However, since we are using ModelViewSet, perform_create is called after validation.
        # Let's override create instead? Or just hook into perform_create.
        
        # Let's stick to the current pattern but use service for notifications/side effects
        instance = serializer.save(requester=self.request.user)
        from apps.notifications.services import NotificationService
        NotificationService.notify_new_consult(instance)
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledges a pending consult request.

        This action is for users in the target department to officially
        acknowledge receipt of a new consult.

        Args:
            request: The Django HttpRequest object.
            pk: The primary key of the `ConsultRequest`.

        Returns:
            A DRF Response object with the updated consult data, or an
            error response.
        """
        consult = self.get_object()
        from .services import ConsultService
        
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
        
        ConsultService.acknowledge_consult(consult, request.user)
        
        serializer = self.get_serializer(consult)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assigns a consult to a specific user within the department.

        This action is typically performed by a Head of Department or an
        administrator. The `assigned_to` user ID must be provided in the
        request body.

        Args:
            request: The Django HttpRequest object.
            pk: The primary key of the `ConsultRequest`.

        Returns:
            A DRF Response object with the updated consult data, or an
            error response.
        """
        consult = self.get_object()
        from .services import ConsultService
        
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
        
        ConsultService.assign_consult(consult, assigned_user, assigner=request.user)
        
        serializer = self.get_serializer(consult)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='acknowledge-assign')
    def acknowledge_assign(self, request, pk=None):
        """Acknowledges and assigns a consult in one combined action.

        This is the new workflow where acknowledgement and assignment must happen together.
        Only HOD or delegated receivers can perform this action.

        Args:
            request: The Django HttpRequest object.
            pk: The primary key of the `ConsultRequest`.

        Returns:
            A DRF Response object with the updated consult data, or an
            error response.
        """
        consult = self.get_object()
        from .services import ConsultService
        
        # Check permissions - only HOD or delegated receivers can acknowledge & assign
        if not request.user.can_manage_consults:
            return Response(
                {'error': 'You do not have permission to acknowledge and assign consults. Only HOD or delegated receivers can perform this action.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if request.user.department != consult.target_department:
            return Response(
                {'error': 'You can only acknowledge and assign consults in your department'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate consult status - should be SUBMITTED
        if consult.status not in ['SUBMITTED', 'ACKNOWLEDGED']:
            return Response(
                {'error': f'Only SUBMITTED consults can be acknowledged and assigned. Current status: {consult.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the assigned user
        assigned_to_id = request.data.get('assigned_to_user_id')
        if not assigned_to_id:
            return Response(
                {'error': 'Please provide assigned_to_user_id'},
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
                {'error': 'Assigned user must be in the target department'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Perform acknowledge and assign in one atomic action
        ConsultService.acknowledge_and_assign_consult(consult, request.user, assigned_user)
        
        serializer = self.get_serializer(consult)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_note(self, request, pk=None):
        """Adds a new note to a consult.

        This action allows authorized users to add a `ConsultNote` to the
        specified `ConsultRequest`. The note data should be provided in the
        request body.

        Args:
            request: The Django HttpRequest object.
            pk: The primary key of the `ConsultRequest`.

        Returns:
            A DRF Response object with the newly created note's data, or
            an error response.
        """
        consult = self.get_object()
        from .services import ConsultService
        
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
            # Use service to add note
            note = ConsultService.add_note(
                consult=consult,
                author=request.user,
                content=serializer.validated_data['content'],
                note_type=serializer.validated_data.get('note_type', 'PROGRESS'),
                recommendations=serializer.validated_data.get('recommendations', ''),
                follow_up_required=serializer.validated_data.get('follow_up_required', False),
                follow_up_instructions=serializer.validated_data.get('follow_up_instructions', ''),
                is_final=serializer.validated_data.get('is_final', False)
            )
            
            return Response(ConsultNoteSerializer(note).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Marks a consult as completed.

        This action is for the assigned user or a HOD to officially close
        a consult.

        Args:
            request: The Django HttpRequest object.
            pk: The primary key of the `ConsultRequest`.

        Returns:
            A DRF Response object with the updated consult data, or an
            error response.
        """
        consult = self.get_object()
        from .services import ConsultService
        
        # Check permissions
        if (request.user != consult.assigned_to and 
            not request.user.can_assign_consults):
            return Response(
                {'error': 'Only the assigned doctor or HOD can complete a consult'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        ConsultService.complete_consult(consult)
        
        serializer = self.get_serializer(consult)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancels a consult request.

        This action can only be performed by the original requester or an
        administrator. Completed consults cannot be cancelled.

        Args:
            request: The Django HttpRequest object.
            pk: The primary key of the `ConsultRequest`.

        Returns:
            A DRF Response object with the updated consult data, or an
            error response.
        """
        consult = self.get_object()
        from .services import ConsultService
        
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
        
        ConsultService.cancel_consult(consult)
        
        serializer = self.get_serializer(consult)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Retrieves dashboard statistics for the current user.

        This action provides a summary of consults, categorized by
        department, assigned to the user, and requested by the user.

        Args:
            request: The Django HttpRequest object.

        Returns:
            A DRF Response object containing the dashboard statistics.
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
    """Provides API endpoints for managing consult notes.

    This ViewSet allows for the creation, retrieval, updating, and deletion
    of notes associated with a consult. It is typically used in the context
    of a specific consult request.
    """
    
    serializer_class = ConsultNoteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Constructs the queryset for the view.

        Filters notes by the `consult` ID if provided as a query
        parameter.

        Returns:
            A Django QuerySet of `ConsultNote` objects.
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
        Called after validation and before saving the note instance.

        Sets the author of the note to the current user.
        Args:
            serializer: The serializer instance.
        """
        serializer.save(author=self.request.user)
