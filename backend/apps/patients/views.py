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
    """Provides API endpoints for managing patients.

    This ViewSet allows for the listing, retrieving, creating, updating, and
    deleting of patient records. It also includes a custom action for
    retrieving all consults associated with a specific patient.
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Constructs the queryset for the view, with optional filtering.

        This method allows for searching by MRN or name, and filtering by
        the patient's primary department.

        Returns:
            A Django QuerySet of `Patient` objects.
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
        """Selects the appropriate serializer for the current action.

        Uses `PatientListSerializer` for the 'list' action to provide a
        more concise representation. For all other actions, it defaults to
        the full `PatientSerializer`.

        Returns:
            The serializer class to be used for the request.
        """
        if self.action == 'list':
            return PatientListSerializer
        return PatientSerializer
    
    @action(detail=True, methods=['get'])
    def consults(self, request, pk=None):
        """Retrieves all consults associated with a specific patient.

        Args:
            request: The Django HttpRequest object.
            pk: The primary key of the `Patient`.

        Returns:
            A DRF Response object containing the serialized consult data.
        """
        patient = self.get_object()
        from apps.consults.serializers import ConsultRequestListSerializer
        consults = patient.consults.all()
        serializer = ConsultRequestListSerializer(consults, many=True)
        return Response(serializer.data)
