from django.db import models
from django import forms
from django.contrib.auth.models import User
from .validators import validate_video_size
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    def __str__(self):
        return self.user.username
def video_upload_path(instance, filename):
    return f"videos/user_{instance.user.id}/{filename}"

class Playlist(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Video(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    video_file = models.FileField(upload_to="videos/")
    thumbnail = models.ImageField(upload_to="thumbnails/", default="thumbnails/default.jpg")
    playlists = models.ManyToManyField(Playlist, related_name="videos", blank=True )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_private = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)

    views = models.PositiveIntegerField(default=0)  

    created_at = models.DateTimeField(auto_now_add=True)
    comments_enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter playlist name"
            })
        }
    def __str__(self):
        return self.name
    
    def __str__(self):
        return f"{self.user.username} liked {self.video.title}"
class Comment(models.Model):
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.text[:20]}"
    
class VideoLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="likes")

    class Meta:
        unique_together = ("user", "video")


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriptions"
    )
    channel = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscribers"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("subscriber", "channel")

    def __str__(self):
        return f"{self.subscriber} → {self.channel}"

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()  
    duration_days = models.IntegerField()

    def __str__(self):
        return self.name
    
class UserSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    active = models.BooleanField(default=True)

    def is_active(self):
        return self.active and self.end_date > timezone.now()
    
class Notification(models.Model):
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_notifications"
    )
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"To {self.recipient.username}: {self.message}"