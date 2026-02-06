from django.urls import path
from . import views
from .api import PlaylistAPI

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
    path("subscribe/<int:user_id>/", views.toggle_subscribe, name="toggle_subscribe"),
    path("video/<int:video_id>/like/", views.toggle_like, name="toggle_like"),
    path("subscriptions/", views.subscription_feed, name="subscription_feed"),
]