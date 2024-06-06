from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings

API_URLS = ['/api/', '/vet/api/', '/route/']

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if any(request.path.startswith(api_url) for api_url in API_URLS):
            return self.get_response(request)
        response = self.get_response(request)
        
        return response