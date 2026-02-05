from django import forms
from .models import Playlist, Video

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ["title", "video_file", "comments_enabled"]

class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ["name"]

class CreatePlaylistWithVideoForm(forms.Form):
    playlist_name = forms.CharField(max_length=200)
    video_title = forms.CharField(max_length=255)
    video_file = forms.FileField()