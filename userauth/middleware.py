from django.shortcuts import redirect
from django.contrib.auth import logout
from django.urls import reverse
from .models import UserProfile

class AccountStatusMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated:

            # Safely get profile
            profile = UserProfile.objects.filter(user=request.user).first()

            if not profile:
                # If profile doesn't exist, create one automatically
                profile = UserProfile.objects.create(user=request.user)

            if profile.is_suspended:
                logout(request)
                return redirect(reverse("account_suspended"))

        return self.get_response(request)