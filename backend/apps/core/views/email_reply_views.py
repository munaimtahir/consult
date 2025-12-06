"""
Email Reply Views
API endpoints for processing email replies.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from apps.core.services.email_reply_service import EmailReplyService
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])  # Will be secured with token/secret in production
def process_email_reply(request):
    """
    Process an email reply and execute the requested action.
    
    This endpoint is designed to be called by:
    - Google Apps Script (for Gmail integration)
    - Email webhook services
    - Manual API calls
    
    Expected POST data:
    {
        "reply_token": "uuid-string",
        "sender_email": "user@pmc.edu.pk",
        "reply_body": "acknowledged"
    }
    
    For production, add authentication (API key, secret token, etc.)
    """
    reply_token = request.data.get('reply_token')
    sender_email = request.data.get('sender_email')
    reply_body = request.data.get('reply_body', '')
    
    if not reply_token:
        return Response(
            {'error': 'reply_token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not sender_email:
        return Response(
            {'error': 'sender_email is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Process the reply
    result = EmailReplyService.process_email_reply(
        reply_token=reply_token,
        sender_email=sender_email,
        reply_body=reply_body
    )
    
    if result['success']:
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

