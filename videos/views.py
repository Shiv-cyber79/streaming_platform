from django.http import HttpResponseForbidden, HttpResponse,FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import VideoForm, PlaylistForm, CreatePlaylistWithVideoForm
from .models import Video, Comment, Playlist



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

    videos = playlist.videos.order_by("created_at")

    video_id = request.GET.get("video")

    
    if video_id:
        current_video = videos.filter(id=video_id).first()
    else:
        current_video = videos.first()  

    
    next_video = None
    if current_video:
        video_list = list(videos)
        index = video_list.index(current_video)

        if index + 1 < len(video_list):
            next_video = video_list[index + 1]

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

@login_required
def playlist_player(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id)
    videos = playlist.videos.all()

    current_video = videos.first() if videos.exists() else None

    return render(request, "videos/playlist_detail.html", {
        "playlist": playlist,
        "videos": videos,
        "current_video": current_video
    })


@login_required(login_url="login")
def upload_video(request):
    if request.method == "POST":
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.user = request.user
            video.save()
            return redirect("home")  
    else:
        form = VideoForm()

    return render(request, "videos/upload_video.html", {"form": form})

@login_required
def video_list(request):
    playlists = Playlist.objects.filter(user=request.user)
    return render(request, "videos/video_list.html", {
        "playlists": playlists
    })

@login_required(login_url="login")
def video_detail(request, video_id):
    video = get_object_or_404(Video, id=video_id)

    if video.is_private and not request.user.is_authenticated:
        return redirect("login")

    return render(request, "videos/video_detail.html", {"video": video})


# @login_required
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
        return redirect("playlist_player", playlist_id=playlist.id)

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
                user=request.user
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
    videos = Video.objects.all().order_by("-created_at")
    return render(request, "videos/all_videos.html", {
        "videos": videos
    })