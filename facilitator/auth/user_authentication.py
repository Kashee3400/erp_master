from rest_framework.authentication import get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from ..models import ApiKey
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.timezone import now

class EnforceBothAuthentication:
    def enforce_authentication(self, request):
        """
        Enforces that both JWT and API Key authentication are required.
        """
        # Check JWT Token (User Authentication)
        jwt_authenticator = JWTAuthentication()
        jwt_header = get_authorization_header(request).decode('utf-8')
        
        if not jwt_header or not jwt_header.startswith("Bearer "):
            raise AuthenticationFailed("JWT Token is required.")

        user, jwt_token = jwt_authenticator.authenticate(request)
        if not user:
            raise AuthenticationFailed("Invalid JWT Token.")

        # Check API Key (External Party Validation)
        api_key = request.headers.get("X-API-KEY")
        if not api_key:
            raise AuthenticationFailed("API Key is required.")

        try:
            api_key_obj = ApiKey.objects.get(key=api_key, is_active=True)
        except ApiKey.DoesNotExist:
            raise AuthenticationFailed("Invalid API Key.")

        if api_key_obj.expires_at and api_key_obj.expires_at < now():
            raise AuthenticationFailed("API Key has expired.")

        # Attach the authenticated user and API key object to the request
        request.user = user
        request.api_key = api_key_obj
