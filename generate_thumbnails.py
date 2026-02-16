import os
import django
import subprocess

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "streaming_platform.settings")
django.setup()

from django.conf import settings
from videos.models import Video

videos = Video.objects.all()

for v in videos:
    if not v.thumbnail:
        try:
            video_path = v.video_file.path
            print("Processing:", video_path)

            thumbnail_name = f"{v.id}.jpg"
            thumbnail_path = os.path.join(settings.MEDIA_ROOT, 'thumbnails', thumbnail_name)

            os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)

            command = [
                "ffmpeg",
                "-i", video_path,
                "-ss", "00:00:02",
                "-vframes", "1",
                thumbnail_path
            ]

            result = subprocess.run(command)

            if result.returncode == 0:
                v.thumbnail = f"thumbnails/{thumbnail_name}"
                v.save()
                print("✅ Done:", v.id)
            else:
                print("❌ FFmpeg failed:", v.id)

        except Exception as e:
            print("❌ Error:", e)
