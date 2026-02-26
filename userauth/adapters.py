print("Adapter triggering")
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
User = get_user_model()
from users.models import Channel
from django.db import IntegrityError
class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    print
    def is_auto_signup_allowed(self, request, sociallogin):
        print("is_auto_signup_allowed called")
        return True

    # def populate_user(self, request, sociallogin, data):
    #     user = super().populate_user(request, sociallogin, data)
    #     print("populate_user executing")
    #     if not user.username and user.email:
    #         base_username = user.email.split("@")[0]
    #         username = base_username
    #         counter = 1
    #         while User.objects.filter(username=username).exists():
    #             username = f"{base_username}{counter}"
    #             counter += 1

    #         user.username = username
    #     return user


    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)

        if not user.username:
            base = user.email.split("@")[0]
            counter = 0

            while True:
                try:
                    if counter == 0:
                        username = base
                    else:
                        username = f"{base}{counter}"

                    user.username = username
                    user.save()
                    break

                except IntegrityError:
                    counter += 1

        data = sociallogin.account.extra_data
        picture = data.get("picture")

        channel, _ = Channel.objects.get_or_create(user=user)

        if picture:
            channel.profile_picture = picture
            channel.save()

        return user