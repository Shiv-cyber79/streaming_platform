from django.contrib import admin
from .models import Subscription,SubscriptionPlan,UserSubscription,Channel
# Register your models here.

admin.site.register(SubscriptionPlan)
admin.site.register(UserSubscription)
admin.site.register(Subscription)
admin.site.register(Channel)