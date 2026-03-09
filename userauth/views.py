import sys

from django.shortcuts import render, redirect
from django.http import HttpResponse,JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate,logout
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.contrib.auth.views import PasswordResetView
from django.conf import settings
import random
from .models import OTP
from videos.forms import CustomPasswordResetForm
from django.core.mail import send_mail

def test_email(request):
    send_mail(
        "Test Email",
        "This is a test email from Django.",
        "rshiv9900@gmail.com",
        ["bhumilc88@gmail.com"],
        fail_silently=False,
    )
    return HttpResponse("Email sent")
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
        
        user_obj = User.objects
        user = user_obj.create_user(username=username, email=email, password=password)

        otp_code = str(random.randint(100000, 999999))
        OTP.objects.create(user=user, otp=otp_code)

        if user.email and otp_code:
            request.session['otp_user'] = user.id
            try:
                send_mail(
                    'Welcome to Streamify! Verify Your Account',
                    f'Hi {username},\n\nThank you for signing up for Stream!\n\nYour OTP is {otp_code}',
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False)
            except Exception as e:
                print("Error sending email:", e)
                user_obj.filter(id=user.id).delete()
                messages.error(request, "Failed to send OTP. Please try signing up again.")
            print("user mail",user.email)
            print("otp code",otp_code)
            print("host mail"  ,settings.EMAIL_HOST_USER)
            # send_mail(
            #         subject='Welcome to Stream Verify Your Account',
            #         message=f'Hi {username},\n\nThank you for signing up for Stream!\n\nYour OTP is {otp_code}',
            #         from_email=settings.EMAIL_HOST_USER,
            #         recipient_list=[user.email],
            #         fail_silently=False)
            return redirect("verify_otp")


        print("inside views/signup after user object created:",user)
        # user.backend = "django.contrib.auth.backends.ModelBackend"
        # login(request, user)

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
        c=0
        while True:
            otp_code = str(random.randint(100000, 999999))
            OTP.objects.create(user=user, otp=otp_code)

            request.session['otp_user'] = user.id

            try:
                send_mail(
                    'Your login OTP for Stream',
                    f'Hi {user.username},\n\nYour OTP is {otp_code}',
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False,
                )
                print("Login OTP sent to:", user.email, otp_code)
                c+=1
                print("OTP send attempt:", c)
            except Exception as e:
                print("Error sending login OTP:", e)
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

        if timezone.now() - otp_obj.created_at < timedelta(minutes=2):
            if otp_obj and otp_obj.otp == entered_otp:

                user = otp_obj.user

                
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')

                try:    
                    del request.session['otp_user']
                except KeyError:
                    print("Session key 'otp_user' not found during deletion.")
                return redirect("home")
            else:
                return render(request, "videos/verify_otp.html",
                              {"error": "Invalid OTP",
                               "invalid":True})
        return render(request, "videos/verify_otp.html", {
            "error": "Invalid or expired OTP",
            "otp_expired": True
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
    
class CustomPasswordResetView(PasswordResetView):
    template_name = "registration/password_reset_form.html"

    def form_valid(self, form):
        email = form.cleaned_data.get('email')

        if not User.objects.filter(email=email).exists():
            messages.error(self.request, "❌ Email does not exist!")
            return self.form_invalid(form)

        return super().form_valid(form)
    
class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = "registration/password_reset_form.html"

    def form_invalid(self, form):
        for error in form.errors.values():
            messages.error(self.request, error[0])
        return super().form_invalid(form)