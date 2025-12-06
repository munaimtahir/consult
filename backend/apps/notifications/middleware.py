"""
WebSocket authentication middleware for JWT token authentication.
"""

from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.conf import settings
from django.contrib.auth.models import AnonymousUser

User = get_user_model()


@database_sync_to_async
def get_user_from_token(token_string):
    """Get user from JWT token."""
    try:
        # Validate token and get validated token
        validated_token = UntypedToken(token_string)
        
        # Get user from validated token
        user_id = validated_token.get('user_id')
        if user_id:
            try:
                return User.objects.get(id=user_id)
            except User.DoesNotExist:
                return AnonymousUser()
        return AnonymousUser()
    except (TokenError, InvalidToken, Exception):
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """
    Custom middleware to authenticate WebSocket connections using JWT tokens.
    
    The token should be passed as a query parameter: ?token=<jwt_token>
    """

    async def __call__(self, scope, receive, send):
        # Extract token from query string
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]
        
        # If no token, set anonymous user
        if not token:
            scope['user'] = AnonymousUser()
        else:
            # Get user from token
            scope['user'] = await get_user_from_token(token)
        
        return await super().__call__(scope, receive, send)
