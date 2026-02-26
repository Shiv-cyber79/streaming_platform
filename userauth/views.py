from django.shortcuts import render, redirect
from django.http import HttpResponse,JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate,logout
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
import random
from .models import OTP


def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request,"Username already exists. Try another.")
            return redirect(request.path)
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered. Please login.")
            return redirect(request.path)
        
        user = User.objects.create_user( username=username, email=email,password=password)

        print("inside views/signup after user object created:",user)
        user.backend = "django.contrib.auth.backends.ModelBackend"
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

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

        # 🔥 OTP logic
        otp_code = str(random.randint(100000, 999999))
        OTP.objects.create(user=user, otp=otp_code)

        request.session['otp_user'] = user.id

        send_mail(
            'Your OTP Code',
            f'Your OTP is {otp_code}',
            'your_email@gmail.com',
            [user.email],
            fail_silently=False,
        )

        return redirect("verify_otp")

    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect("home") 

def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        user_id = request.session.get('otp_user')

        otp_obj = OTP.objects.filter(user_id=user_id).last()

        if otp_obj and otp_obj.otp == entered_otp:
            from django.utils import timezone
            from datetime import timedelta

            if timezone.now() - otp_obj.created_at < timedelta(seconds=30):
                user = otp_obj.user

                
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')

                del request.session['otp_user']

                return redirect("home")

        return render(request, "videos/verify_otp.html", {
            "error": "Invalid or expired OTP"
        })

    return render(request, "videos/verify_otp.html")

def resend_otp(request):
    user_id = request.session.get('otp_user')

    if not user_id:
        return JsonResponse({"error": "Session expired"}, status=400)

    user = User.objects.get(id=user_id)

    otp_code = str(random.randint(100000, 999999))
    OTP.objects.create(user=user, otp=otp_code)

    # send OTP (email for now)
    user.email_user(
        "Your New OTP",
        f"Your OTP is {otp_code}"
    )

    return JsonResponse({"message": "OTP resent successfully"})


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