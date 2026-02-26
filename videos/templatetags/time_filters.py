from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def youtube_time(value):
    if not value:
        return ""

    now = timezone.now()
    diff = now - value

    seconds = diff.total_seconds()

    minute = 60
    hour = 3600
    day = 86400
    week = day * 7
    month = day * 30
    year = day * 365

    if seconds < minute:
        return "just now"

    elif seconds < hour:
        m = int(seconds / minute)
        return f"{m} minute{'s' if m > 1 else ''} ago"

    elif seconds < day:
        h = int(seconds / hour)
        return f"{h} hour{'s' if h > 1 else ''} ago"

    elif seconds < week:
        d = int(seconds / day)
        return f"{d} day{'s' if d > 1 else ''} ago"

    elif seconds < month:
        w = int(seconds / week)
        return f"{w} week{'s' if w > 1 else ''} ago"

    elif seconds < year:
        mo = int(seconds / month)
        return f"{mo} month{'s' if mo > 1 else ''} ago"

    else:
        y = int(seconds / year)
        return f"{y} year{'s' if y > 1 else ''} ago"