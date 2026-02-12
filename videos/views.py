from datetime import timedelta
from django.http import HttpResponseForbidden, HttpResponse,FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import VideoForm, PlaylistForm, CreatePlaylistWithVideoForm
from .models import Video, Comment, Playlist,VideoLike,User,Notification
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import F
from .utils import has_active_subscription
import stripe
from django.conf import settings
from django.urls import reverse
from django.db.models import Q
from users.models import Subscription

stripe.api_key = settings.STRIPE_SECRET_KEY

def home(request):
    
    playlists = Playlist.objects.all()
    return render(request, "videos/home.html", {
        "playlists": playlists
    })

def playlist_list(request):
    playlists = Playlist.objects.filter(user=request.user)
    return render(request, "videos/playlist_list.html", {
        "playlists": playlists
    })

@login_required(login_url="login")
def stream_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)

    if video.is_private and video.user != request.user:
        return HttpResponseForbidden("Private video")

    return FileResponse(video.video_file.open(), content_type="video/mp4")@login_required


@login_required
def playlist_detail(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id)

    if not playlist.is_public and playlist.user != request.user:
     return render(request, "videos/private_playlist.html", {
        "playlist": playlist
    }, status=403)

    if request.user == playlist.user:
       videos = playlist.videos.order_by("created_at")
    else:
       videos = playlist.videos.filter(is_private=False).order_by("created_at")

    video_id = request.GET.get("video")

    if video_id:
        current_video = videos.filter(id=video_id).first()
    else:
        current_video = videos.first()

    if current_video and current_video.is_premium:
        if not has_active_subscription(request.user):
            return render(request, "videos/premium_locked.html", {
            "video": current_video
        })
    if current_video:
        Video.objects.filter(id=current_video.id).update(
            views=F("views") + 1
        )
    next_video = None
    if current_video:
        video_list = list(videos)
        index = video_list.index(current_video)
        if index + 1 < len(video_list):
            next_video = video_list[index + 1]

    print("playlist details: ",current_video.user, current_video.user.id)
    
    return render(
        request,
        "videos/playlist_player.html",  
        {
            "playlist": playlist,
            "videos": videos,
            "current_video": current_video,
            "next_video": next_video,
        }
    )

# @login_required
# def create_payment(request, plan_id):
#     plan = get_object_or_404(SubscriptionPlan, id=plan_id)

#     client = razorpay.Client(
#         auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
#     )

#     order = client.order.create({
#         "amount": plan.price * 100,
#         "currency": "INR",
#         "payment_capture": 1
#     })

#     request.session["plan_id"] = plan.id

#     return JsonResponse({
#         "order_id": order["id"],
#         "amount": plan.price,
#         "key": settings.RAZORPAY_KEY_ID
#     })

# @require_POST
# @login_required
# def payment_success(request):
#     plan_id = request.session.get("plan_id")
#     plan = get_object_or_404(SubscriptionPlan, id=plan_id)

#     UserSubscription.objects.create(
#         user=request.user,
#         plan=plan,
#         end_date=timezone.now() + timedelta(days=plan.duration_days),
#         active=True
#     )

#     return redirect("home")


@login_required(login_url="login")
def upload_video(request):
    if request.method == "POST":
        form = VideoForm(request.POST, request.FILES)

        if form.is_valid():
            video = form.save(commit=False)
            video.user = request.user
            video.save()
         
            subscribers = Subscription.objects.filter(
                channel=request.user
            ).select_related("subscriber")

            for sub in subscribers:
                Notification.objects.create(
                    recipient=sub.subscriber,
                    sender=request.user,
                    video=video,
                    message=f"{request.user.username} uploaded a new video"
                )

            return redirect("playlist_list")  

    else:
        form = VideoForm()

    return render(request, "videos/upload_video.html", {"form": form})

@login_required
def notifications(request):
    notifications = (
        Notification.objects
        .filter(recipient=request.user)
        .order_by("-created_at")
    )

    notifications.filter(is_read=False).update(is_read=True)

    return render(request, "videos/notifications.html", {
        "notifications": notifications
    })

@login_required
def video_list(request):
    playlists = Playlist.objects.filter(user=request.user)
    return render(request, "videos/video_list.html", {
        "playlists": playlists
    })

@login_required(login_url="login")
def video_detail(request, video_id):

    print("video detail",video_id)
    video = get_object_or_404(Video, id=video_id)

  
    if video.is_private:
        if not request.user.is_authenticated or video.user != request.user:
            return HttpResponseForbidden("This video is private.")

    return render(request, "videos/video_detail.html", {"video": video})

@require_POST
@login_required
def toggle_like(request, video_id):
    video = get_object_or_404(Video, id=video_id)

# @require_POST
# @login_required
# def toggle_like(request, video_id):
#     video = get_object_or_404(Video, id=video_id)

#     like, created = VideoLike.objects.get_or_create(
#         user=request.user,
#         video=video
#     )

#     if not created:
#         like.delete()
#         liked = False
#     else:
#         liked = True

#     return JsonResponse({
#         "liked": liked,
#         "count": video.likes.count()
#     })

# @require_POST
# @login_required
# def toggle_subscribe(request, user_id):
#     channel = get_object_or_404(User, id=user_id)

#     if channel == request.user:
#         return JsonResponse(
#             {"error": "You cannot subscribe to yourself"},
#             status=400
#         )

#     sub, created = Subscription.objects.get_or_create(
#         subscriber=request.user,
#         channel=channel
#     )

#     if not created:
#         sub.delete()
#         subscribed = False
#     else:
#         subscribed = True

#     return JsonResponse({
#         "subscribed": subscribed,
#         "count": channel.subscribers.count()
#     })

# @login_required
# def subscription_feed(request):
#     videos = (
#         Video.objects
#         .filter(user__subscribers__subscriber=request.user)
#         .order_by("-created_at")
#     )

#     return render(request, "videos/subscription_feed.html", {
#         "videos": videos
#     })

@login_required
def add_comment(request, video_id):
    video = get_object_or_404(Video, id=video_id)

    if not video.comments_enabled:
        return HttpResponseForbidden("Comments are disabled for this video")

    if request.method == "POST":
        text = request.POST.get("comment")

        if text:
            Comment.objects.create(
                video=video,
                user=request.user,
                text=text
            )

    playlist = video.playlists.first()

    if playlist:
        return redirect(
            f"/playlists/{playlist.id}/?video={video.id}"
        )

    return redirect("video_detail", video_id=video.id)

@login_required
def add_video_to_playlist(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    playlists = Playlist.objects.filter(user=request.user)

    if request.method == "POST":
        playlist_id = request.POST.get("playlist_id")
        playlist = get_object_or_404(
            Playlist, id=playlist_id, user=request.user
        )
        playlist.videos.add(video)
        return redirect("video_detail", video_id=video.id)

    return render(request, "videos/add_to_playlist.html", {
        "video": video,
        "playlists": playlists
    })

@login_required
def edit_playlist(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)

    if request.method == "POST":
        form = PlaylistForm(request.POST, instance=playlist)
        if form.is_valid():
            form.save()
            return redirect("playlist_list")
    else:
        form = PlaylistForm(instance=playlist)

    return render(request, "videos/edit_playlist.html", {
        "form": form,
        "playlist": playlist
    })


@login_required
def create_playlist(request):
    if request.method == "POST":
        form = CreatePlaylistWithVideoForm(request.POST, request.FILES)

        if form.is_valid():
            playlist = Playlist.objects.create(
                name=form.cleaned_data["playlist_name"],
                user=request.user,
                is_public=form.cleaned_data("is_public",False)
            )

            video = Video.objects.create(
                title=form.cleaned_data["video_title"],
                video_file=form.cleaned_data["video_file"],
                user=request.user
            )

            playlist.videos.add(video)

            return redirect("playlist_detail", playlist.id)

    else:
        form = CreatePlaylistWithVideoForm()

    return render(request, "videos/create_playlist.html", {
        "form": form
    })

@login_required
def all_videos(request):
    if request.user.is_authenticated:
        videos = Video.objects.filter(
            Q(is_private=False) | Q(user=request.user)
        ).order_by("-created_at")
    else:
        videos = Video.objects.filter(
            is_private=False
        ).order_by("-created_at")

    return render(request, "videos/all_videos.html", {
        "videos": videos
    })
