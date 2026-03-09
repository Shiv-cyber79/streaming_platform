from django import forms
from .models import Playlist, Video, User,Post
from users.models import Channel
from userauth.models import UserProfile
class ProfilePhotoForm(forms.ModelForm):
    class Meta:
        model = Channel
        fields = ["profile_picture"]

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
            "description",
            "comments_enabled",
            "thumbnail",
            "is_premium", 
        ]
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "placeholder": "Write something about your video..."
                }
            )
        }
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
    thumbnail = forms.ImageField(required=False)  

    is_public = forms.BooleanField(required=False, initial=True)

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image']

class CustomPasswordResetForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("❌ Email is not registered")

        return email

class ProfileCompletionForm(forms.ModelForm):
    username = forms.CharField(max_length=150)

    class Meta:
        model = UserProfile
        fields = ['profile_picture']   

    def save(self, user, commit=True):
        profile = super().save(commit=False)

       
        user.username = self.cleaned_data['username']
        user.save()

        profile.user = user
        profile.is_profile_complete = True

        if commit:
            profile.save()

        return profile