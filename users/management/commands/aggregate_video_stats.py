from django.core.management.base import BaseCommand
from videos.models import VideoWatch, VideoStatiscics
from django.db.models.functions import TruncDate
from django.db.models import Sum

class Command(BaseCommand):
    help = "Aggregate daily video watch statistics"

    def handle(self, *args, **Kwargs):
        aggregated = (
            VideoWatch.objects
            .annotate(date=TruncDate("watched_at"))   # extract date
            .values("video_id", "video__user_id", "date")
            .annotate(total_watch_time=Sum("watch_time_sec"))
        )
        self.stdout.write(self.style.SUCCESS("aggregated data created successfully..."))
        for row in aggregated:
            VideoStatiscics.objects.update_or_create(
                video_id_id=row["video_id"],
                date=row["date"],
                defaults={
                    "channel_id_id": row["video__user_id"],
                    "day_watch_time": row["total_watch_time"]
                }
            )
        self.stdout.write(self.style.SUCCESS("aggregated successfully..."))
