from django.shortcuts import render, redirect
from django.http import HttpResponse,JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate,logout
from django.contrib import messages

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return redirect(request.path)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)

        next_url = request.POST.get("next") or request.GET.get("next")
        return redirect(next_url or "/")

    return render(request, "signup.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid username or password")
            return render(request, "login.html")

        login(request, user)
        return redirect("home")  

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("home") 

def refresh_access_token(request):
    refresh_token = request.session.get("refresh_token")

    if not refresh_token:
        return JsonResponse({"error": "No refresh token"}, status=401)

    try:
        refresh = RefreshToken(refresh_token)
        new_access = str(refresh.access_token)

        request.session["access_token"] = new_access

        return JsonResponse({"access": new_access})

    except Exception:
        return JsonResponse({"error": "Invalid refresh token"}, status=401)