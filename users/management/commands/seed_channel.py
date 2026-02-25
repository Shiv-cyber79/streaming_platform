from django.contrib.auth.models import User
from videos.models import Video
from faker import Faker
from users.models import Channel
import random
from django.core.management.base import BaseCommand


fake = Faker()
class Command(BaseCommand):

    def handle(self,*args,**kwargs):
        self.stdout.write(self.style.WARNING("function calling..."))

        self.create_fake_channels(50)

        self.stdout.write(self.style.WARNING("channel creation complete..."))
    def create_fake_channels(self,count):
        users = User.objects.all()
        # videos = Video.objects.all()
        for _ in range(count):
            owner = random.choice(users)
            try:
                Channel.objects.create(name=owner, user_id=owner.id)
            except Exception as e:
                print(e)
        print("channels created")
    