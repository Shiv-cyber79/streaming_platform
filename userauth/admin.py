from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "is_frozen", "is_suspended")
    list_filter = ("is_frozen", "is_suspended")