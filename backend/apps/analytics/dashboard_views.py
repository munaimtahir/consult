"""
Dashboard API views for Admin Panel.
"""

from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from apps.consults.models import ConsultRequest
from apps.departments.models import Department
from apps.accounts.permissions import CanViewDepartmentDashboard, CanViewGlobalDashboard


class DepartmentDashboardView(views.APIView):
    """Department Dashboard API.
    
    Returns statistics and consult lists for a specific department.
    Shows both sent and received consults.
    """
    
    permission_classes = [IsAuthenticated, CanViewDepartmentDashboard]
    
    def get(self, request):
        """Get department dashboard data."""
        user = request.user
        
        # Get department from query params or use user's department
        department_id = request.query_params.get('department_id')
        
        if department_id:
            try:
                department = Department.objects.get(id=department_id)
            except Department.DoesNotExist:
                return Response(
                    {'error': 'Department not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check permission for the specific department
            if not user.can_view_department_dashboard_for(department):
                return Response(
                    {'error': 'You do not have permission to view this department\'s dashboard'},
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            # Use user's department
            if not user.department:
                return Response(
                    {'error': 'No department specified and you are not assigned to a department'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            department = user.department
        
        # Get query params for filtering
        consult_type = request.query_params.get('type', 'all')  # received, sent, all
        status_filter = request.query_params.get('status')
        urgency_filter = request.query_params.get('urgency')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        overdue_filter = request.query_params.get('overdue')
        assigned_to = request.query_params.get('assigned_to')
        
        # Build base querysets
        received_qs = ConsultRequest.objects.filter(target_department=department)
        sent_qs = ConsultRequest.objects.filter(requesting_department=department)
        
        # Apply common filters
        def apply_filters(qs):
            nonlocal status_filter, urgency_filter, date_from, date_to, overdue_filter, assigned_to
            
            if status_filter:
                qs = qs.filter(status=status_filter)
            if urgency_filter:
                qs = qs.filter(urgency=urgency_filter)
            if date_from:
                qs = qs.filter(created_at__gte=date_from)
            if date_to:
                qs = qs.filter(created_at__lte=date_to)
            if overdue_filter is not None:
                qs = qs.filter(is_overdue=overdue_filter.lower() == 'true')
            if assigned_to:
                qs = qs.filter(assigned_to_id=assigned_to)
            
            return qs
        
        received_qs = apply_filters(received_qs)
        sent_qs = apply_filters(sent_qs)
        
        # Calculate summary stats
        today = timezone.now().date()
        
        summary = {
            'total_active': received_qs.exclude(status__in=['COMPLETED', 'CANCELLED']).count(),
            'pending': received_qs.filter(status='PENDING').count(),
            'acknowledged': received_qs.filter(status='ACKNOWLEDGED').count(),
            'in_progress': received_qs.filter(status='IN_PROGRESS').count(),
            'completed_today': received_qs.filter(
                status='COMPLETED',
                completed_at__date=today
            ).count(),
            'overdue': received_qs.filter(
                is_overdue=True
            ).exclude(status__in=['COMPLETED', 'CANCELLED']).count(),
            'sent_active': sent_qs.exclude(status__in=['COMPLETED', 'CANCELLED']).count(),
        }
        
        # Build consult list data
        def serialize_consult(consult):
            return {
                'id': consult.id,
                'patient': {
                    'id': consult.patient.id,
                    'name': consult.patient.name,
                    'mrn': consult.patient.mrn,
                    'location': f"{consult.patient.ward or ''} {consult.patient.bed_number or ''}".strip(),
                },
                'requesting_department': {
                    'id': consult.requesting_department.id,
                    'name': consult.requesting_department.name,
                },
                'target_department': {
                    'id': consult.target_department.id,
                    'name': consult.target_department.name,
                },
                'assigned_to': {
                    'id': consult.assigned_to.id,
                    'name': consult.assigned_to.get_full_name(),
                } if consult.assigned_to else None,
                'created_at': consult.created_at.isoformat(),
                'urgency': consult.urgency,
                'status': consult.status,
                'completed_at': consult.completed_at.isoformat() if consult.completed_at else None,
                'is_overdue': consult.is_overdue,
                'reason_for_consult': consult.reason_for_consult[:100] + '...' if len(consult.reason_for_consult) > 100 else consult.reason_for_consult,
            }
        
        # Get consults based on type filter
        received_list = []
        sent_list = []
        
        if consult_type in ['received', 'all']:
            received_consults = received_qs.select_related(
                'patient', 'requesting_department', 'target_department', 'assigned_to'
            ).order_by('-created_at')[:50]
            received_list = [serialize_consult(c) for c in received_consults]
        
        if consult_type in ['sent', 'all']:
            sent_consults = sent_qs.select_related(
                'patient', 'requesting_department', 'target_department', 'assigned_to'
            ).order_by('-created_at')[:50]
            sent_list = [serialize_consult(c) for c in sent_consults]
        
        return Response({
            'department': {
                'id': department.id,
                'name': department.name,
                'code': department.code,
            },
            'summary': summary,
            'received_consults': received_list,
            'sent_consults': sent_list,
        })


class GlobalDashboardView(views.APIView):
    """Global Dashboard API.
    
    Returns system-wide statistics and consult lists across all departments.
    Only accessible to users with global dashboard permission.
    """
    
    permission_classes = [IsAuthenticated, CanViewGlobalDashboard]
    
    def get(self, request):
        """Get global dashboard data."""
        
        # Get query params for filtering
        requesting_department = request.query_params.get('requesting_department')
        target_department = request.query_params.get('target_department')
        status_filter = request.query_params.get('status')
        urgency_filter = request.query_params.get('urgency')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        overdue_filter = request.query_params.get('overdue')
        assigned_to = request.query_params.get('assigned_to')
        
        # Build base queryset
        qs = ConsultRequest.objects.all()
        
        # Apply filters
        if requesting_department:
            qs = qs.filter(requesting_department_id=requesting_department)
        if target_department:
            qs = qs.filter(target_department_id=target_department)
        if status_filter:
            qs = qs.filter(status=status_filter)
        if urgency_filter:
            qs = qs.filter(urgency=urgency_filter)
        if date_from:
            qs = qs.filter(created_at__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__lte=date_to)
        if overdue_filter is not None:
            qs = qs.filter(is_overdue=overdue_filter.lower() == 'true')
        if assigned_to:
            qs = qs.filter(assigned_to_id=assigned_to)
        
        # Global KPIs
        today = timezone.now().date()
        
        global_kpis = {
            'total_open': qs.exclude(status__in=['COMPLETED', 'CANCELLED']).count(),
            'total_today': qs.filter(created_at__date=today).count(),
            'overdue_count': qs.filter(
                is_overdue=True
            ).exclude(status__in=['COMPLETED', 'CANCELLED']).count(),
            'pending_count': qs.filter(status='PENDING').count(),
            'in_progress_count': qs.filter(status='IN_PROGRESS').count(),
            'completed_today': qs.filter(
                status='COMPLETED',
                completed_at__date=today
            ).count(),
        }
        
        # Serialize consults
        def serialize_consult(consult):
            return {
                'id': consult.id,
                'patient': {
                    'id': consult.patient.id,
                    'name': consult.patient.name,
                    'mrn': consult.patient.mrn,
                    'location': f"{consult.patient.ward or ''} {consult.patient.bed_number or ''}".strip(),
                },
                'requesting_department': {
                    'id': consult.requesting_department.id,
                    'name': consult.requesting_department.name,
                },
                'target_department': {
                    'id': consult.target_department.id,
                    'name': consult.target_department.name,
                },
                'assigned_to': {
                    'id': consult.assigned_to.id,
                    'name': consult.assigned_to.get_full_name(),
                } if consult.assigned_to else None,
                'requester': {
                    'id': consult.requester.id,
                    'name': consult.requester.get_full_name(),
                },
                'created_at': consult.created_at.isoformat(),
                'updated_at': consult.updated_at.isoformat(),
                'urgency': consult.urgency,
                'status': consult.status,
                'completed_at': consult.completed_at.isoformat() if consult.completed_at else None,
                'is_overdue': consult.is_overdue,
                'reason_for_consult': consult.reason_for_consult[:100] + '...' if len(consult.reason_for_consult) > 100 else consult.reason_for_consult,
            }
        
        # Get consults list
        consults = qs.select_related(
            'patient', 'requesting_department', 'target_department', 
            'assigned_to', 'requester'
        ).order_by('-created_at')[:100]
        consults_list = [serialize_consult(c) for c in consults]
        
        # Department summary stats
        departments = Department.objects.filter(is_active=True)
        department_stats = []
        
        for dept in departments:
            dept_received = ConsultRequest.objects.filter(target_department=dept)
            dept_sent = ConsultRequest.objects.filter(requesting_department=dept)
            
            # Calculate average times (only for completed consults)
            completed = dept_received.filter(
                status='COMPLETED',
                acknowledged_at__isnull=False,
                completed_at__isnull=False
            )
            
            avg_ack_time = None
            avg_completion_time = None
            
            if completed.exists():
                # Calculate average acknowledgement time in minutes
                ack_times = []
                completion_times = []
                for c in completed:
                    if c.acknowledged_at:
                        ack_delta = (c.acknowledged_at - c.created_at).total_seconds() / 60
                        ack_times.append(ack_delta)
                    if c.completed_at:
                        comp_delta = (c.completed_at - c.created_at).total_seconds() / 60
                        completion_times.append(comp_delta)
                
                if ack_times:
                    avg_ack_time = round(sum(ack_times) / len(ack_times), 1)
                if completion_times:
                    avg_completion_time = round(sum(completion_times) / len(completion_times), 1)
            
            department_stats.append({
                'department_id': dept.id,
                'department_name': dept.name,
                'open_received_count': dept_received.exclude(
                    status__in=['COMPLETED', 'CANCELLED']
                ).count(),
                'open_sent_count': dept_sent.exclude(
                    status__in=['COMPLETED', 'CANCELLED']
                ).count(),
                'overdue_count': dept_received.filter(
                    is_overdue=True
                ).exclude(status__in=['COMPLETED', 'CANCELLED']).count(),
                'average_ack_time_minutes': avg_ack_time,
                'average_completion_time_minutes': avg_completion_time,
            })
        
        return Response({
            'global_kpis': global_kpis,
            'consults': consults_list,
            'department_stats': department_stats,
        })


class ConsultReassignView(views.APIView):
    """API for reassigning consults globally.
    
    Allows users with can_manage_consults_globally permission to
    reassign consults to different doctors or departments.
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, consult_id):
        """Reassign a consult."""
        from apps.accounts.permissions import CanManageConsultsGlobally
        from apps.accounts.models import User
        
        # Check permission
        if not request.user.is_superuser and not request.user.can_manage_consults_globally:
            return Response(
                {'error': 'You do not have permission to reassign consults globally'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            consult = ConsultRequest.objects.get(id=consult_id)
        except ConsultRequest.DoesNotExist:
            return Response(
                {'error': 'Consult not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get reassignment data
        assigned_to_id = request.data.get('assigned_to')
        target_department_id = request.data.get('target_department')
        previous_assignee = consult.assigned_to
        
        if assigned_to_id:
            try:
                new_assignee = User.objects.get(id=assigned_to_id)
                consult.assigned_to = new_assignee
            except User.DoesNotExist:
                return Response(
                    {'error': 'User not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        if target_department_id:
            try:
                new_dept = Department.objects.get(id=target_department_id)
                consult.target_department = new_dept
                # Clear assignment when changing department
                consult.assigned_to = None
            except Department.DoesNotExist:
                return Response(
                    {'error': 'Department not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        consult.save()
        
        # Send reassignment notification
        from apps.notifications.services import NotificationService
        NotificationService.notify_reassignment(consult, previous_assignee)
        
        # Return updated consult info
        return Response({
            'id': consult.id,
            'status': consult.status,
            'assigned_to': {
                'id': consult.assigned_to.id,
                'name': consult.assigned_to.get_full_name(),
            } if consult.assigned_to else None,
            'target_department': {
                'id': consult.target_department.id,
                'name': consult.target_department.name,
            },
            'message': 'Consult reassigned successfully'
        })


class ConsultForceCloseView(views.APIView):
    """API for force-closing consults.
    
    Allows users with can_manage_consults_globally permission to
    force close or cancel consults with a reason.
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, consult_id):
        """Force close a consult."""
        from apps.consults.models import ConsultNote
        
        # Check permission
        if not request.user.is_superuser and not request.user.can_manage_consults_globally:
            return Response(
                {'error': 'You do not have permission to force close consults'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            consult = ConsultRequest.objects.get(id=consult_id)
        except ConsultRequest.DoesNotExist:
            return Response(
                {'error': 'Consult not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if consult.status in ['COMPLETED', 'CANCELLED']:
            return Response(
                {'error': 'Consult is already closed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = request.data.get('reason')
        action = request.data.get('action', 'complete')  # complete or cancel
        
        if not reason:
            return Response(
                {'error': 'Reason is required for force closing a consult'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Add a note documenting the force close
        ConsultNote.objects.create(
            consult=consult,
            author=request.user,
            note_type='FINAL',
            content=f"ADMIN ACTION: Consult force {'closed' if action == 'complete' else 'cancelled'} by {request.user.get_full_name()}. Reason: {reason}",
            is_final=True
        )
        
        if action == 'cancel':
            consult.status = 'CANCELLED'
        else:
            consult.status = 'COMPLETED'
            consult.completed_at = timezone.now()
        
        consult.save()
        
        return Response({
            'id': consult.id,
            'status': consult.status,
            'message': f'Consult {action}d successfully'
        })
