from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum,Count
from django.db import connection
from django.db.models.functions import TruncDate
from .models import UserSubscription, Subscription
from datetime import datetime

from videos.models import VideoStatiscics, VideoWatch

def has_active_subscription(user):
    return UserSubscription.objects.filter(
        user=user,
        active=True,
        end_date__gt=timezone.now()
    ).exists()

class Deshboard:
    def __init__(self,request):
        self.request=request
    

    def handle(self,*args,**kwargs):
        self.watch_data(*args,**kwargs)

    def watch_data(self,start_date,end_date):

        stats = None
        print("id:",self.request.user.id)
        if start_date and end_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

            stats = (
                VideoStatiscics.objects
                .filter(
                    channel_id_id=self.request.user,
                    date__range=[start_date, end_date]
                )
                .values("video_id_id","date")
                .annotate(total_watch_time=Sum("day_watch_time"))
                .order_by("video_id_id")
            )
            # print(stats)
        return stats
    
    def subscriber_data(self,start_date,end_date):

        subscriber_stats = None
        if start_date and end_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

            subscriber_stats = (
                Subscription.objects
                .filter(channel_id=self.request.user,
                        created_at__date__range=[start_date,end_date]
                    )
                .values(date=TruncDate("created_at"))
                .annotate(total_subscribers=Count('subscriber_id'))
                .order_by("date")
            )
        # print(subscriber_stats)
        return subscriber_stats
        
    def views_data(self,start_date,end_date):

        view_stats=None
        if start_date and end_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        view_stats = (
            VideoWatch.objects
            .filter()
        )

    def revenue(self,start_date,end_date):
        id=int(self.request.user.id)
        print(id)
        data_list=None
        if start_date and end_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

            query = """
            SELECT video_id_id,SUM(day_watch_time) AS watch_time
            FROM videos_videostatiscics
            WHERE channel_id_id = %s
                AND date BETWEEN %s AND %s
            GROUP BY video_id_id
            ORDER BY watch_time DESC"""
            with connection.cursor() as cursor:
                cursor.execute(query,[id,start_date,end_date])
                data_list = cursor.fetchall()
        print(data_list)
        return data_list
        # for i in range(len(data_list)):
        #     print(data_list[i]['video_id'])