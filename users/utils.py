from django.utils import timezone
from .models import UserSubscription

def has_active_subscription(user):
    return UserSubscription.objects.filter(
        user=user,
        active=True,
        end_date__gt=timezone.now()
    ).exists()
