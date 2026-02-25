import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User

from faker import Faker
from users.models import Channel, Subscription

class Command(BaseCommand):
    help="Generate subscribers data"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("seeding subscribers data..."))

        users = list(User.objects.all())
        channels = list(Channel.objects.all())

        subsribers = []
        unique_pairs = set()
        
        for _ in range(5000):
            us = random.choice(users)
            ch = random.choice(channels)
            ch_user = ch.user
            pair = (ch_user.id,us.id)

            if pair in unique_pairs:
                continue
            
            if ch_user==us:
                continue
            
            if Subscription.objects.filter(
                channel=ch_user,
                subscriber_id=us.id
            ).exists():
                continue
            
            unique_pairs.add(pair)

            created_at = timezone.now() - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            subsribers.append(
                Subscription(channel=ch_user,
                            subscriber=us,
                            created_at=created_at)
            )
        
        Subscription.objects.bulk_create(subsribers,batch_size=500)
        self.stdout.write(self.style.WARNING("seeding completead and update Subscription table..."))

         