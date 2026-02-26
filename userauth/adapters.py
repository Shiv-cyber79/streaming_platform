print("Adapter triggering")

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from allauth.exceptions import ImmediateHttpResponse

from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from users.models import Channel
from .models import OTP, UserProfile

import random

User = get_user_model()


class MyAccountAdapter(DefaultAccountAdapter):

    def login(self, request, user):
        otp_code = str(random.randint(100000, 999999))
        OTP.objects.create(user=user, otp=otp_code)

        request.session['otp_user'] = user.id

        try:
            profile = UserProfile.objects.get(user=user)

            if profile.mobile:
                print("OTP sent to mobile:", otp_code)
            else:
                raise Exception()

        except:
            user.email_user(
                "Your OTP Code",
                f"Your OTP is {otp_code}"
            )

        return redirect("verify_otp")



class MySocialAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        user = sociallogin.user

        otp_code = str(random.randint(100000, 999999))
        OTP.objects.create(user=user, otp=otp_code)

        request.session['otp_user'] = user.id

        user.email_user(
            "Your OTP",
            f"Your OTP is {otp_code}"
        )

    
        raise ImmediateHttpResponse(redirect("verify_otp"))

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)

        if not user.username:
            base = user.email.split("@")[0]
            counter = 0

            while True:
                try:
                    username = base if counter == 0 else f"{base}{counter}"
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