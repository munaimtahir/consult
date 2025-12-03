"""
Admin views for email notification and SMTP configuration management.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from apps.accounts.permissions import CanManagePermissions
from .models import EmailNotificationSettings, SMTPConfiguration
from .serializers import (
    EmailNotificationSettingsSerializer,
    SMTPConfigurationSerializer,
    SMTPConfigurationListSerializer
)
from apps.departments.models import Department
import logging

logger = logging.getLogger(__name__)


class EmailNotificationSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing email notification settings per department.
    Only super admins and sys admins can access this.
    """
    queryset = EmailNotificationSettings.objects.select_related('department').all()
    serializer_class = EmailNotificationSettingsSerializer
    permission_classes = [IsAuthenticated, CanManagePermissions]
    
    def get_queryset(self):
        """Filter by department if provided."""
        queryset = super().get_queryset()
        department_id = self.request.query_params.get('department_id')
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Create email notification settings for a department."""
        department_id = request.data.get('department_id')
        if not department_id:
            return Response(
                {'error': 'department_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            department = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            return Response(
                {'error': 'Department not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if settings already exist
        if EmailNotificationSettings.objects.filter(department=department).exists():
            return Response(
                {'error': 'Email notification settings already exist for this department'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(department=department)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def by_department(self, request):
        """Get email notification settings for a specific department."""
        department_id = request.query_params.get('department_id')
        if not department_id:
            return Response(
                {'error': 'department_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            settings = EmailNotificationSettings.objects.get(department_id=department_id)
            serializer = self.get_serializer(settings)
            return Response(serializer.data)
        except EmailNotificationSettings.DoesNotExist:
            # Return default settings
            try:
                department = Department.objects.get(id=department_id)
                default_settings = EmailNotificationSettings(department=department)
                serializer = self.get_serializer(default_settings)
                return Response(serializer.data)
            except Department.DoesNotExist:
                return Response(
                    {'error': 'Department not found'},
                    status=status.HTTP_404_NOT_FOUND
                )


class SMTPConfigurationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing SMTP configurations.
    Only super admins and sys admins can access this.
    """
    queryset = SMTPConfiguration.objects.all()
    permission_classes = [IsAuthenticated, CanManagePermissions]
    
    def get_serializer_class(self):
        """Use different serializer for list vs detail."""
        if self.action == 'list':
            return SMTPConfigurationListSerializer
        return SMTPConfigurationSerializer
    
    def get_queryset(self):
        """Order by active status."""
        return super().get_queryset().select_related('created_by')
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a specific SMTP configuration."""
        config = self.get_object()
        config.is_active = True
        config.save()
        serializer = self.get_serializer(config)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a specific SMTP configuration."""
        config = self.get_object()
        config.is_active = False
        config.save()
        serializer = self.get_serializer(config)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test SMTP connection."""
        config = self.get_object()
        
        try:
            import smtplib
            from email.mime.text import MIMEText
            
            # Test connection
            if config.use_tls:
                server = smtplib.SMTP(config.host, config.port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(config.host, config.port)
            
            server.login(config.username, config.password)
            server.quit()
            
            return Response({
                'success': True,
                'message': 'SMTP connection test successful'
            })
        except Exception as e:
            logger.error(f"SMTP connection test failed: {e}")
            return Response(
                {
                    'success': False,
                    'message': f'SMTP connection test failed: {str(e)}'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get the currently active SMTP configuration."""
        try:
            config = SMTPConfiguration.objects.get(is_active=True)
            serializer = self.get_serializer(config)
            return Response(serializer.data)
        except SMTPConfiguration.DoesNotExist:
            return Response(
                {'error': 'No active SMTP configuration found'},
                status=status.HTTP_404_NOT_FOUND
            )

