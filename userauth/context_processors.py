from users.models import Channel

def user_profile_picture(request):
    if request.user.is_authenticated:
        try:
            profile_pic = request.user.channel.profile_picture
        except Channel.DoesNotExist:
            profile_pic=None
    else:
        profile_pic=None
    
    return {
        "profile_pic":profile_pic
    }