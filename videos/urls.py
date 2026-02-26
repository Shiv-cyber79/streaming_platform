from django.urls import path
from . import views
from .api import PlaylistAPI
from.views import live_view


# app_name = 'videos'

urlpatterns = [
  
    path("",views.home, name="home"),
    path("playlists/", views.playlist_list, name="playlist_list"),
    path("video/<int:video_id>/", views.video_detail, name="video_detail"),
    path("api/playlists/", PlaylistAPI.as_view(), name="playlist_api"),
    path("all-videos/", views.all_videos, name="all_videos"),
    path("stream/<int:video_id>/", views.stream_video, name="stream_video"),
    path("video/<int:video_id>/comment/", views.add_comment, name="add_comment"),
    path("video/<int:video_id>/add-to-playlist/", views.add_video_to_playlist, name="add_to_playlist"),
    path("upload/", views.upload_video, name="upload_video"),
    path("playlists/<int:playlist_id>/edit/",views.edit_playlist, name="edit_playlist"),
    path("playlists/<int:playlist_id>/", views.playlist_detail, name="playlist_detail"),
    path("playlists/new/", views.create_playlist, name="create_playlist"),


    # path("settings/", views.user_settings, name="user_settings"),
    # path("subscription-plans/", views.subscription_plans, name="subscription_plans"),
    # # path("create-payment/<int:plan_id>/", views.create_payment, name="create_payment"),

    # path("stripe-checkout/<int:plan_id>/", views.create_stripe_checkout, name="stripe_checkout"),
    # path("stripe-success/", views.stripe_success, name="stripe_success"),

    # path("unsubscribe/<int:channel_id>/", views.unsubscribe, name="unsubscribe"),
    

    path('watch/', views.upload_video_detail, name='watch_all'),
    path('watch/<int:video_id>/', views.upload_video_detail, name='upload_video_detail'),

    path('live/<str:username>/', views.live_page, name='live_page'),
    # path('live/<str:room_name>/', live_view, name='live'),
    path("upload-live/", views.upload_live_video, name="upload_live"),
    # path('watch/', views.upload_video_detail, name='watch_all'),
    # path('watch/<int:video_id>/', views.upload_video_detail, name='watch_video'),
    path('post/create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/like/', views.toggle_post_like, name='toggle_post_like'),
    path('post/<int:post_id>/comment/', views.add_post_comment, name='add_post_comment'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),

]