from django.contrib import admin
from .models import Video, Comment,Playlist

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    filter_horizontal = ("playlists",)
@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    pass

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "video", "user", "created_at")
    list_filter = ("video", "user")
