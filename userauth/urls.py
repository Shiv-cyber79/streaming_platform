from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from.views import login_view,logout_view,CustomPasswordResetView
from rest_framework_simplejwt.views import TokenRefreshView
from .views import CustomPasswordResetView
from django.shortcuts import redirect


urlpatterns = [
   
    path("signup/", views.signup, name="signup"),

    # path('login/', auth_views.LoginView.as_view(), name='login'),
    path("login/", login_view, name="login"),

    path("logout/",logout_view, name="logout"),
    path("test-email/", views.test_email),
    
    path("password-reset/", auth_views.PasswordResetView.as_view(
        template_name="registration/password_reset_form.html"
    ), name="password_reset"),

    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(
        template_name="registration/password_reset_done.html"
    ), name="password_reset_done"),

    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="registration/password_reset_confirm.html"
    ), name="password_reset_confirm"),

    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(
        template_name="registration/password_reset_complete.html"
    ), name="password_reset_complete"),

    path("refresh-token/", TokenRefreshView.as_view(), name="token_refresh"),

    path("verify_otp/", views.verify_otp, name="verify_otp"),

    path("resend-otp/", views.resend_otp, name="resend_otp"),

    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(
        template_name="registration/password_reset_complete.html"
    ), name="password_reset_complete"),
    
]


