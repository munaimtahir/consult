from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import Device
from .serializers import DeviceRegistrationSerializer, DeviceTokenUpdateSerializer


class DeviceRegistrationView(APIView):
    """
    API endpoint for registering devices for push notifications.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Register a new device or update existing registration."""
        serializer = DeviceRegistrationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            device = serializer.save()
            return Response(DeviceRegistrationSerializer(device).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeviceTokenUpdateView(APIView):
    """
    API endpoint for updating FCM token for an existing device.
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        """Update the FCM token for a device."""
        device_id = request.data.get('device_id')
        if not device_id:
            return Response(
                {'error': 'device_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            device = Device.objects.get(user=request.user, device_id=device_id)
        except Device.DoesNotExist:
            return Response(
                {'error': 'Device not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = DeviceTokenUpdateSerializer(device, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(DeviceRegistrationSerializer(device).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeviceUnregisterView(APIView):
    """
    API endpoint for unregistering a device from push notifications.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Unregister a device (mark as inactive)."""
        device_id = request.data.get('device_id')
        if not device_id:
            return Response(
                {'error': 'device_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            device = Device.objects.get(user=request.user, device_id=device_id)
            device.is_active = False
            device.save()
            return Response({'status': 'Device unregistered'})
        except Device.DoesNotExist:
            return Response(
                {'error': 'Device not found'},
                status=status.HTTP_404_NOT_FOUND
            )
