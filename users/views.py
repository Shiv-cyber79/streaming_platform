from django.http import HttpResponse,FileResponse,JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

from .models import Subscription,SubscriptionPlan,UserSubscription,Channel
from videos.models import Video,VideoLike
from videos.forms import ProfilePhotoForm,NameChangeForm
import razorpay
from datetime import timedelta


@login_required
def user_profile(request, username):
    channel_user = get_object_or_404(User,username=username)
    print("Channel username",channel_user,"request username",request.user)
    videos = Video.objects.filter(user=channel_user).order_by("created_at")
    latest_video = videos.first()
    other_videos = videos[1:]
    print(type(videos))
    subscriber_count = Subscription.objects.filter(
        channel=channel_user
    ).count()
    print(subscriber_count)
    is_subscribed = False
    if request.user.is_authenticated:
        is_subscribed = Subscription.objects.filter(
            subscriber=request.user,
            channel=channel_user
        ).exists() 
    print(is_subscribed)

    context = {
        "channel_user":channel_user,
        "request_user":request.user,
        "latest_video":latest_video,
        "other_videos":other_videos,
        "subscriber_count":subscriber_count,
        "is_subscribed":is_subscribed
    }
    return render(request, "videos/user_page.html", context)

@login_required
def user_profile_videos(request, username):
    channel_user = get_object_or_404(User, username=username)
    videos = Video.objects.filter(user=channel_user)
    subscriber_count = Subscription.objects.filter(
        channel=channel_user
    ).count()
    return render(request, "videos/channel_user_videos.html", {
        "channel_user": channel_user,
        "subscriber_count":subscriber_count,
        "videos": videos
    })


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
    channel_user = get_object_or_404(User, id=user_id)
    print("Inside toggle subs",channel_user)
    if channel_user == request.user:
        return JsonResponse(
            {"error": "You cannot subscribe to yourself"},
            status=400
        )

    sub, created = Subscription.objects.get_or_create(
        subscriber=request.user,
        channel=channel_user
    )
    print(sub,created)
    print(not created)

    if not created:
        sub.delete()
        subscribed = False
    else:
        subscribed = True
    context = {
        "subscribed": subscribed,
        "count": channel_user.subscribers.count()
    }
    return JsonResponse(context)

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
@login_required
def subscription_plans(request):
    plans = SubscriptionPlan.objects.all()

    return render(request, "videos/subscription_plans.html", {
        "plans": plans
    })

@login_required
def user_settings(request):
    profile, _ = Channel.objects.get_or_create(user=request.user)

    photo_form = ProfilePhotoForm(instance=profile)
    name_form = NameChangeForm(instance=request.user)

    if request.method == "POST":
        if "photo_submit" in request.POST:
            photo_form = ProfilePhotoForm(
                request.POST,
                request.FILES,
                instance=profile
            )
            if photo_form.is_valid():
                photo_form.save()

        elif "name_submit" in request.POST:
            name_form = NameChangeForm(
                request.POST,
                instance=request.user
            )
            if name_form.is_valid():
                name_form.save()

        return redirect("user_settings")

    return render(request, "videos/settings.html", {
        "photo_form": photo_form,
        "name_form": name_form,
        "profile": profile
    })