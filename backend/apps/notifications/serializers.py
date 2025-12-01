from rest_framework import serializers
from .models import Device


class DeviceRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for device registration."""
    
    class Meta:
        model = Device
        fields = ['id', 'device_id', 'fcm_token', 'platform', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'is_active', 'created_at', 'updated_at']

    def create(self, validated_data):
        """Create or update a device registration."""
        user = self.context['request'].user
        device_id = validated_data['device_id']
        
        # Try to update existing device registration
        device, created = Device.objects.update_or_create(
            user=user,
            device_id=device_id,
            defaults={
                'fcm_token': validated_data['fcm_token'],
                'platform': validated_data.get('platform', 'android'),
                'is_active': True,
            }
        )
        return device


class DeviceTokenUpdateSerializer(serializers.Serializer):
    """Serializer for updating FCM token."""
    device_id = serializers.CharField(max_length=255)
    fcm_token = serializers.CharField()

    def update(self, instance, validated_data):
        """Update the FCM token for a device."""
        instance.fcm_token = validated_data['fcm_token']
        instance.is_active = True
        instance.save()
        return instance
