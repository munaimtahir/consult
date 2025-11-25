"""
Custom adapter for django-allauth to restrict to PMC email domain.
"""

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.core.exceptions import ValidationError


class PMCEmailAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter to ensure only @pmc.edu.pk emails can sign up via Google OAuth.
    """
    
    def pre_social_login(self, request, sociallogin):
        """
        Validate email domain before allowing social login.
        """
        email = sociallogin.account.extra_data.get('email', '')
        
        if not email.endswith('@pmc.edu.pk'):
            raise ValidationError(
                'Only Pakistan Medical Commission (@pmc.edu.pk) email addresses are allowed to sign in.'
            )
    
    def populate_user(self, request, sociallogin, data):
        """
        Populate user fields from Google OAuth data.
        """
        user = super().populate_user(request, sociallogin, data)
        
        # Get additional data from Google
        extra_data = sociallogin.account.extra_data
        
        # Set profile photo from Google
        if 'picture' in extra_data:
            user.profile_photo = extra_data['picture']
        
        # Set first and last name from Google
        if 'given_name' in extra_data:
            user.first_name = extra_data['given_name']
        if 'family_name' in extra_data:
            user.last_name = extra_data['family_name']
        
        return user
