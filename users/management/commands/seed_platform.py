import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User

from faker import Faker

from videos.models import Video, VideoWatch


fake = Faker()


class Command(BaseCommand):
    help = "Seed full streaming platform with fake users, videos, and watch data"

    # -----------------------------
    # CLI ARGUMENTS
    # -----------------------------
    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=1000)
        parser.add_argument("--videos", type=int, default=500)
        parser.add_argument("--watch", type=int, default=10000)

    # -----------------------------
    # MAIN EXECUTION
    # -----------------------------
    def handle(self, *args, **kwargs):
        user_count = kwargs["users"]
        video_count = kwargs["videos"]
        watch_count = kwargs["watch"]

        self.stdout.write(self.style.WARNING("Seeding platform data..."))

        self.create_fake_users(user_count)
        self.create_fake_videos(video_count)
        self.create_fake_watch_data(watch_count)

        self.stdout.write(self.style.SUCCESS("Platform seeding completed!"))

    # -----------------------------
    # CREATE USERS
    # -----------------------------
    def create_fake_users(self, count):
        self.stdout.write(f"Creating {count} users...")

        users = []

        for _ in range(count):
            username = fake.user_name() + str(random.randint(1, 9999))
            email = fake.email()

            users.append(
                User(
                    username=username,
                    email=email
                )
            )

        User.objects.bulk_create(users, batch_size=500)
        self.stdout.write(self.style.SUCCESS("Users created"))

    # -----------------------------
    # CREATE VIDEOS
    # -----------------------------
    def create_fake_videos(self, count):
        self.stdout.write(f"Creating {count} videos...")

        users = list(User.objects.all())

        if not users:
            self.stdout.write(self.style.ERROR("No users available"))
            return

        videos = []

        for _ in range(count):
            owner = random.choice(users)

            videos.append(
                Video(
                    title=fake.sentence(nb_words=5),
                    description=fake.text(),
                    duration=random.randint(60, 3600),
                    user=owner,
                    is_private=False,
                )
            )

        Video.objects.bulk_create(videos, batch_size=500)
        self.stdout.write(self.style.SUCCESS("Videos created"))

    # -----------------------------
    # CREATE WATCH DATA
    # -----------------------------
    def create_fake_watch_data(self, count):
        self.stdout.write(f"Creating {count} watch records...")

        users = list(User.objects.all())
        videos = list(Video.objects.all())

        if not users or not videos:
            self.stdout.write(self.style.ERROR("Users or Videos missing"))
            return

        watches = []

        for _ in range(count):

            user = random.choice(users)
            video = random.choice(videos)
            video_duration = getattr(video, "duration", 600)

            # ensure valid duration
            if not video_duration or video_duration < 10:
                video_duration = 60

            watch_type = random.choices(
                ["full", "partial", "drop"],
                weights=[0.2, 0.5, 0.3]
            )[0]

            if watch_type == "full":
                watch_time = video_duration
                completed = True

            elif watch_type == "partial":
                min_watch = int(video_duration * 0.3)
                max_watch = int(video_duration * 0.9)
                watch_time = random.randint(min_watch, max_watch)
                completed = False

            else:  # drop
                max_watch = max(5, int(video_duration * 0.2))
                watch_time = random.randint(5, max_watch)
                completed = False

            watched_at = timezone.now() - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )

            watches.append(
                VideoWatch(
                    user=user,
                    video=video,
                    watch_time_sec=watch_time,
                    watched_at=watched_at,
                    completed=completed,
                )
            )

        VideoWatch.objects.bulk_create(watches, batch_size=1000)
        self.stdout.write(self.style.SUCCESS("Watch data created"))