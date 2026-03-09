from django.contrib.auth.models import User
from django.db import models
import random


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    profile_picture = models.ImageField( upload_to='profiles/',default='default.jpg', blank=True,null=True)

    is_profile_complete = models.BooleanField(default=False)
    mobile = models.CharField(max_length=10, blank=True, null=True)
    is_frozen = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)
    suspension_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_otp(self):
        return str(random.randint(100000, 999999))
    