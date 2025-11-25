"""
Views for Patients app.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .models import Patient
from .serializers import PatientSerializer, PatientListSerializer


class PatientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Patient model.
    Provides CRUD operations for patient records.
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter queryset based on search parameters.
        """
        queryset = Patient.objects.select_related('primary_department')
        
        # Search by MRN or name
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(mrn__icontains=search) | Q(name__icontains=search)
            )
        
        # Filter by department
        department_id = self.request.query_params.get('department', None)
        if department_id:
            queryset = queryset.filter(primary_department_id=department_id)
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        """
        if self.action == 'list':
            return PatientListSerializer
        return PatientSerializer
    
    @action(detail=True, methods=['get'])
    def consults(self, request, pk=None):
        """
        Get all consults for a specific patient.
        """
        patient = self.get_object()
        from apps.consults.serializers import ConsultRequestListSerializer
        consults = patient.consults.all()
        serializer = ConsultRequestListSerializer(consults, many=True)
        return Response(serializer.data)
