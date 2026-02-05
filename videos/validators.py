from django.core.exceptions import ValidationError

def validate_video_size(value):
    max_size = 50 * 1024 * 1024  
    if value.size > max_size:
        raise ValidationError("Video file size should not exceed 50 MB")
