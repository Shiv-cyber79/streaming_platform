from allauth.socialaccount.signals import social_account_added
from django.dispatch import receiver
from django.contrib.auth import get_user_model
User = get_user_model()
@receiver(social_account_added)
def save_google_data(request, sociallogin, **kwargs):
    user = sociallogin.user
    data = sociallogin.account.extra_data

    picture = data.get("picture")
    if picture:
        profile, _ = user.profile.__class__.objects.get_or_create(user=user)
        profile.avatar = picture
        profile.save()

@receiver(social_account_added)
def populate_username(request, sociallogin, **kwargs):
    user = sociallogin.user

    if not user.username:
        base = user.email.split("@")[0]
        username = base
        counter = 1

        while User.objects.filter(username=username).exists():
            username = f"{base}{counter}"
            counter += 1

        user.username = username
        user.save()