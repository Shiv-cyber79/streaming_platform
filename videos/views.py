from datetime import timedelta
from django.http import HttpResponseForbidden, HttpResponse,FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import VideoForm, PlaylistForm, CreatePlaylistWithVideoForm
from .models import Video, Comment, Playlist,VideoLike,User,Notification,LiveStream 
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import F
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from users.utils import has_active_subscription
# import stripe
from django.conf import settings
from django.db.models import Q

from users.models import Subscription
from.models import Post,PostLike,PostComment
from .forms import PostForm

from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt


# stripe.api_key = settings.STRIPE_SECRET_KEY

def home(request):
    category = request.GET.get("category")
    query = request.GET.get("q")   

    if request.user.is_authenticated:
        videos = Video.objects.filter(
            Q(is_private=False) | Q(user=request.user)
        )
    else:
        videos = Video.objects.filter(
            is_private=False
        )
        
    if query:
        videos = videos.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(user__username__icontains=query)
        )

    videos = videos.order_by("-created_at")
    Live_streams = LiveStream.objects.filter(is_live=True)

    return render(request, "videos/home.html", {
        "videos": videos,
        "posts": PostForm,
        "query": query,
        "LiveStream": LiveStream  
    })

def live_page(request, username):
    is_broadcaster = request.user.username == username

    if is_broadcaster:
        LiveStream.objects.update_or_create(
            user=request.user,
            defaults={
                "room_name": username,
                "is_live": True
            }
        )

        subscribers = Subscription.objects.filter(
            channel=request.user
        ).select_related("subscriber")

        for sub in subscribers:
            Notification.objects.create(
                recipient=sub.subscriber,
                sender=request.user,
                message=f"{request.user.username} is LIVE 🔴"
            )

        send_email_to_subscribers(
            subscribers,
            request.user,
            "is LIVE now 🔴"
        )

    return render(request, "videos/live.html", {
        "room_name": username,
        "is_broadcaster": is_broadcaster
    })
def live_view(request, room_name):
    return render(request, "live.html", {
        "room_name": room_name
    })

def live_stream(request, username):
    is_broadcaster = request.user.username == username
    return render(request, "live.html", {
        "is_broadcaster": is_broadcaster
    })

@csrf_exempt
def upload_live_video(request):
    if request.method == "POST":
        file = request.FILES.get("video")

        video = Video.objects.create(
            user=request.user,
            title="Live Stream",
            video_file=file,
            
        )

        return JsonResponse({
            "status": "success",
            "video_id": video.id
        })
        return JsonResponse({"error": "Invalid request"}, status=400)
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

    return FileResponse(video.video_file.open(), content_type="video/mp4")


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
# def create_stripe_checkout(request, plan_id):
#     plan = get_object_or_404(SubscriptionPlan, id=plan_id)

#     session = stripe.checkout.Session.create(
#         payment_method_types=["card"],
#         line_items=[{
#             "price_data": {
#                 "currency": "inr",
#                 "product_data": {
#                     "name": plan.name,
#                 },
#                 "unit_amount": plan.price * 100,  # paise
#             },
#             "quantity": 1,
#         }],
#         mode="payment",
#         success_url=request.build_absolute_uri(
#             reverse("stripe_success")
#         ) + "?plan_id=" + str(plan.id),
#         cancel_url=request.build_absolute_uri(
#             reverse("subscription_plans")
#         ),
#     )

#     return redirect(session.url, code=303)

# @login_required
# def stripe_success(request):
#     plan_id = request.GET.get("plan_id")
#     plan = get_object_or_404(SubscriptionPlan, id=plan_id)

#     UserSubscription.objects.create(
#         user=request.user,
#         plan=plan,
#         end_date=timezone.now() + timedelta(days=plan.duration_days),
#         active=True
#     )

#     return render(request, "videos/stripe_success.html", {
#         "plan": plan
#     })

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
            print(video.user,request.user)
            video.save()
         
            subscribers = Subscription.objects.filter(
                channel=request.user
            ).select_related("subscriber")

            for sub in subscribers:
                Notification.objects.create(recipient=sub.subscriber,sender=request.user,video=video,message=f"{request.user.username} uploaded a new video" )

            send_email_to_subscribers( subscribers, request.user, "uploaded a new video 🎥")

            return redirect("/")  

    else:
        form = VideoForm()

    return render(request, "videos/upload_video.html", {"form": form})

@login_required
def upload_video_detail(request, video_id=None):
    videos = Video.objects.filter(is_private=False).order_by('-created_at')

    if video_id:
        video = get_object_or_404(Video, id=video_id)
    else:
        video = videos.first()

    subscribed_channels = Subscription.objects.filter(
        subscriber=request.user
    ).select_related("channel")

    playlists = Playlist.objects.filter(user=request.user)

    if video_id:    
        suggested_videos = videos.exclude(id=video.id)[:10]
        return render(request, 'videos/upload_video_detail.html', {
            'video': video,
            'suggested_videos': suggested_videos,
            'subscribed_channels': subscribed_channels,
            'playlists': playlists,
        })
    else:
        return render(request,'videos/upload_video_detail.html')
    
def send_email_to_subscribers(subscribers, creator, text, video=None):
    emails = [sub.subscriber.email for sub in subscribers if sub.subscriber.email]

    if not emails:
        return

    subject = f"{creator.username} {text}"

    html_content = render_to_string("emails/notification_email.html", {
        "creator": creator,
        "text": text,
        "video": video,
        "site_url": "http://127.0.0.1:8000"
    })

    email = EmailMultiAlternatives(
        subject,
        "",
        settings.DEFAULT_FROM_EMAIL,
        emails
    )

    email.attach_alternative(html_content, "text/html")
    email.send()
    
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

def video_detail(request, video_id):

    print("video detail",video_id)
    video = get_object_or_404(Video, id=video_id)

    suggested_videos = Video.objects.exclude(id=video_id)[:10]

    from_page = request.GET.get("from")  # 👈 IMPORTANT

    subscribed_channels = []
    if request.user.is_authenticated:
        
        subscribed_channels = Subscription.objects.filter(
            subscriber=request.user
        ).select_related("channel")

    return render(request, "videos/video_detail.html", {
        "video": video,
        "suggested_videos": suggested_videos,
        "subscribed_channels": subscribed_channels,
        "from_page": from_page
    })

@require_POST
@login_required
def toggle_like(request, video_id):
    video = get_object_or_404(Video, id=video_id)

@login_required
def add_post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        text = request.POST.get("text")

        if text:
            PostComment.objects.create(
                user=request.user,
                post=post,
                text=text
            )

    return redirect(request.META.get("HTTP_REFERER"))

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.user != request.user:
        return HttpResponseForbidden()

    post.delete()
    return redirect(request.META.get("HTTP_REFERER"))

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.user != request.user:
        return HttpResponseForbidden()

    if request.method == "POST":
        post.content = request.POST.get("content")
        post.save()
        return redirect("user_profile_posts", username=request.user.username)

    return render(request, "videos/edit_post.html", {"post": post})

@login_required
def view_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    return render(request, "videos/view_post.html", {
        "post": post
    })
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
# def unsubscribe(request, channel_id):
#     if request.method == "POST":
#         Subscription.objects.filter(
#             subscriber=request.user,
#             channel_id=channel_id
#         ).delete()

#     return redirect(request.META.get("HTTP_REFERER", "home"))

# @login_required
# def subscription_feed(request):
#     videos = (
#         Video.objects
#         .filter(user__subscribers__subscriber=request.user)
#         .order_by("-created_at")
#     )

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
                is_public=form.cleaned_data.get("is_public", False)
            )

            video = Video.objects.create(
               title=form.cleaned_data["video_title"],
               video_file=form.cleaned_data["video_file"],
               thumbnail=form.cleaned_data.get("thumbnail"),
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

@login_required
def create_post(request):
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()

            subscribers = Subscription.objects.filter(
                channel=request.user
            ).select_related("subscriber")

            for sub in subscribers:
                Notification.objects.create(
                    recipient=sub.subscriber,
                    sender=request.user,
                    post=post,  
                    message=f"{request.user.username} added a new post 📝"
            )
            send_email_to_subscribers(
                subscribers,
                request.user,
                "added a new post 📝"
            )

            return redirect('home')

    else:
        form = PostForm()

    return render(request, 'videos/create_post.html', {'form': form})
@login_required
def toggle_post_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    like, created = PostLike.objects.get_or_create(
        user=request.user,
        post=post
    )

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({
        "liked": liked,
        "count": post.likes.count()
    })

# @login_required
# def user_settings(request):
#     profile, _ = Profile.objects.get_or_create(user=request.user)

#     photo_form = ProfilePhotoForm(instance=profile)
#     name_form = NameChangeForm(instance=request.user)

#     if request.method == "POST":
     
#         if "photo_submit" in request.POST:
#             photo_form = ProfilePhotoForm(
#                 request.POST,
#                 request.FILES,
#                 instance=profile
#             )

#             if photo_form.is_valid():
#                 new_avatar = photo_form.cleaned_data["avatar"]

#                 if profile.avatar_requested_at:
#                  time_diff = timezone.now() - profile.avatar_requested_at
#                  if time_diff < timedelta(hours=3):
#                     remaining_time = timedelta(hours=3) - time_diff
#                     minutes_left = int(remaining_time.total_seconds() // 60)

#                     messages.error(
#                         request,
#                         f"You can change your profile picture after {minutes_left} minutes."
#                     )
#                     return redirect("user_settings")
               
#                 profile.avatar = new_avatar
#                 profile.avatar_requested_at = timezone.now()
#                 profile.save()

#                 messages.success(
#                     request,
#                     "Profile picture update request submitted successfully."
#                 )
#                 return redirect("user_settings")

       
#         elif "name_submit" in request.POST:
#             name_form = NameChangeForm(
#                 request.POST,
#                 instance=request.user
#             )
#             print("Name Submit Pressed")
#             if name_form.is_valid():
#                 if profile.username_requested_at:
#                     time_diff = timezone.now() - profile.username_requested_at
#                     if time_diff < timedelta(hours=3):
#                         remaining_time = timedelta(hours=3) - time_diff
#                         minutes_left = int(remaining_time.total_seconds() // 60)

#                         messages.error(
#                             request,
#                             f"You can change your name after {minutes_left} minutes."
#                         )
#                         return redirect("user_settings")
#                 name_form.save()
#                 profile.username_requested_at = timezone.now()
#                 profile.save()
#                 messages.success(request, "Profile name updated successfully.")
#                 return redirect("user_settings")
            
#     return render(request, "videos/settings.html", {
#         "photo_form": photo_form,
#         "name_form": name_form,
#         "profile": profile
#     })
