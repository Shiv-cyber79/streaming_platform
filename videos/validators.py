import os
from django.core.exceptions import ValidationError

def validate_video_size(value):
    max_size = 50 * 1024 * 1024  
    if value.size > max_size:
        raise ValidationError("Video file size should not exceed 50 MB")
    
def validate_video_file(file):
    ext = os.path.splitext(file.name)[1]  # get extension

    valid_extensions = ['.mp4', '.webm', '.mkv', '.avi']

    if not ext.lower() in valid_extensions:
        raise ValidationError("Only video files are allowed (mp4, webm, mkv, avi)")