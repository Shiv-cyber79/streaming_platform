from .models import Notification
from users.models import Subscription

def notification_count(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        return {"unread_notifications_count": count}
    return {}

def subscriptions_processor(request):
    if request.user.is_authenticated:
        return {
            'subscribed_channels': Subscription.objects.filter(
                subscriber=request.user   # ✅ FIXED
            ).select_related("channel")
        }
    return {
        'subscribed_channels': []
    }