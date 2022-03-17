from django.conf import settings
from datetime import datetime
from django.contrib.auth import get_user_model
from urllib import parse
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction

from rest_framework.exceptions import APIException,NotFound,ValidationError

from .models import Profile, User,EmailVerification,AccountStatus
from.serializers import UserResetPasswordSerializer,UserChangePasswordSerializer

from apps.common.services import send_mail,generate_hash_token

@transaction.atomic
def register_user(data):
    user = User(
        username=data["email"],
        email=data["email"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        pseudonym = data['pseudonym'] # TODO case check
    )
    user.set_password(data["password"])
    user.save()
    # send_mail(user.email,"Welcome to Our Site","site is in developing mode please wait")
    # send_verification_email(user)

    profile = Profile(
        user=user
    )
    profile.save()
    return user

def send_verification_email(user):
    token = generate_hash_token()
    verification = EmailVerification(
        user = user,
        token=token,
        is_valid=True,
    )
    verification.save()

    FRONTEND_URL = "http://localhost:8080/"
    verify_link = FRONTEND_URL + 'email-verify/' + token
    send_mail(user.email,"Verification Email",verify_link)

@transaction.atomic
def confirm_email_verification(user,token):
    email_verification = get_object_or_404(EmailVerification,token=token)
    if email_verification.is_valid:
        email_verification.is_valid = False
        email_verification.save()
        user.account_status = AccountStatus.VERIFIED
        user.save()
    else:
        raise ValidationError("Token Expired")

def request_password_reset(user):
    token = default_token_generator.make_token(user)
    reset_url = '%s/reset-password?email=%s&token=%s' % ("http://localhost:8080", user.email, token)
    send_mail(user.email, "Password Reset",reset_url)
    print(reset_url)


def password_reset(user, reset_data):
    serializer = UserResetPasswordSerializer(data=reset_data)
    if serializer.is_valid(raise_exception=True):
        if default_token_generator.check_token(user, reset_data['token']):
            user.set_password(reset_data['new_password'])
            user.save()
        else:
            raise APIException("Reset token is invalid")

def change_password(user, password_data):
    if user.check_password(password_data['old_password']):
        serializer = UserChangePasswordSerializer(data=password_data)
        if serializer.is_valid(raise_exception=True):
            user.set_password(password_data['new_password'])
            user.save()
    else:
        raise APIException("Old password is invalid")


def delete_user(user_id):
    user: User = User.objects.get(pk=user_id)
    user.is_active = False
    user.save()

    return user
