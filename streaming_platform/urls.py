from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView,)

from users import views
import videos

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("videos.urls")),
    # path("login/", auth_views.LoginView.as_view(), name="login"),
    # path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    path("user_auth/", include("userauth.urls")),
   
    path("channel/<str:username>/", views.user_profile, name="user_profile"),
    path("channel/<str:username>/videos/", views.user_profile_videos, name="user_profile_videos"),

    path("subscribe/<int:user_id>/", views.toggle_subscribe, name="toggle_subscribe"),
    path("video/<int:video_id>/like/", views.toggle_like, name="toggle_like"),
    path("subscriptions/", views.subscription_feed, name="subscription_feed"),
    path("subscription-plans/", views.subscription_plans, name="subscription_plans"),
    path("notifications/", videos.views.notifications,name="notifications"),
    # path("create-payment/<int:plan_id>/", views.create_payment, name="create_payment"),

    # path("stripe-checkout/<int:plan_id>/", views.create_stripe_checkout, name="stripe_checkout"),
    # path("stripe-success/", views.stripe_success, name="stripe_success"),
   
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
