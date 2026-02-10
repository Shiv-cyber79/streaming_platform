from django.http import HttpResponse,FileResponse,JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

from .models import Subscription,SubscriptionPlan,UserSubscription
from videos.models import Video,VideoLike
import razorpay
from datetime import timedelta


@login_required
def user_profile(request, username):
    channel_user = get_object_or_404(User,username=username)
    # print(channel_user,request.user)
    videos = Video.objects.filter(user=channel_user)
    # print(videos)
    context = {
        "channel_user":channel_user,
        "request_user":request.user,
        "videos":videos
    }
    return render(request, "videos/user_page.html", context)

@login_required
def create_payment(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    order = client.order.create({
        "amount": plan.price * 100,
        "currency": "INR",
        "payment_capture": 1
    })

    request.session["plan_id"] = plan.id

    return JsonResponse({
        "order_id": order["id"],
        "amount": plan.price,
        "key": settings.RAZORPAY_KEY_ID
    })

@require_POST
@login_required
def payment_success(request):
    plan_id = request.session.get("plan_id")
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)

    UserSubscription.objects.create(
        user=request.user,
        plan=plan,
        end_date=timezone.now() + timedelta(days=plan.duration_days),
        active=True
    )

    return redirect("home")
@require_POST
@login_required
def toggle_subscribe(request, user_id):
    channel = get_object_or_404(User, id=user_id)

    if channel == request.user:
        return JsonResponse(
            {"error": "You cannot subscribe to yourself"},
            status=400
        )

    sub, created = Subscription.objects.get_or_create(
        subscriber=request.user,
        channel=channel
    )

    if not created:
        sub.delete()
        subscribed = False
    else:
        subscribed = True

    return JsonResponse({
        "subscribed": subscribed,
        "count": channel.subscribers.count()
    })

@require_POST
@login_required
def toggle_like(request, video_id):
    video = get_object_or_404(Video, id=video_id)

    like, created = VideoLike.objects.get_or_create(
        user=request.user,
        video=video
    )

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({
        "liked": liked,
        "count": video.likes.count()
    })

@login_required
def subscription_feed(request):
    videos = (
        Video.objects
        .filter(user__subscribers__subscriber=request.user)
        .order_by("-created_at")
    )

    return render(request, "videos/subscription_feed.html", {
        "videos": videos
    })