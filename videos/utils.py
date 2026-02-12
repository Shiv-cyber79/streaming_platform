from .models import UserSubscription
from django.utils import timezone

def has_active_subscription(user):
    if not user.is_authenticated:
        return False

    return UserSubscription.objects.filter(
        user=user,
        active=True,
        end_date__gt=timezone.now()
    ).exists()
