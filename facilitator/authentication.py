from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from .models import ApiKey
from django.utils.timezone import now

class ApiKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # Check if the API key is provided in the request headers
        api_key = request.headers.get('X-API-KEY')

        if not api_key:
            raise AuthenticationFailed("API key is required for access.")  # Raise error if API key is missing

        try:
            # Check if the API key exists and is active
            api_key_obj = ApiKey.objects.get(key=api_key, is_active=True)
        except ApiKey.DoesNotExist:
            raise AuthenticationFailed("Invalid API key or API key is not active.")

        # Optionally, check if the API key has expired (if expiration logic is implemented)
        if api_key_obj.expires_at and api_key_obj.expires_at < now():
            raise AuthenticationFailed("API key has expired.")

        # Return the API key object for further use if required (e.g., attaching to user)
        return (None, api_key_obj)  # You can return None if the API key isn't linked to any user (since this is for access control)
