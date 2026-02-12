from django import forms
from .models import Playlist, Video, Profile, User

class ProfilePhotoForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["avatar"]

class NameChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]
        widgets = {
            "first_name": forms.TextInput(attrs={
                "placeholder": "Profile first name",
                "class": "form-control"
            }),
            "last_name": forms.TextInput(attrs={
                "placeholder": "Profile last name",
                "class": "form-control"
            }),
        }
        labels = {
            "first_name": "First name",
            "last_name": "Last name",
        }

class VideoForm(forms.ModelForm):
    is_private = forms.BooleanField(required=False)
    comments_enabled = forms.BooleanField(required=False)

   
    is_premium = forms.BooleanField(required=False)

    class Meta:
        model = Video
        fields = [
            "title",
            "video_file",
            "is_private",
            "comments_enabled",
            "is_premium",   
        ]
class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ["name", "is_public"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Playlist name"
            }),
        }

class CreatePlaylistWithVideoForm(forms.Form):
    playlist_name = forms.CharField(max_length=200)
    video_title = forms.CharField(max_length=255)
    video_file = forms.FileField()

    is_public = forms.BooleanField(required=False, initial=True)