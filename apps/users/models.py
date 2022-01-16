from django.db.models.base import Model
from django.db.models.enums import Choices
from django.utils.translation import gettext_lazy as _
import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework.exceptions import ValidationError

class AccountStatus(models.TextChoices):
    PENDING_EMAIL = 'PENDING_EMAIL', _('PENDING_EMAIL')
    VERIFIED = 'VERIFIED', _('VERIFIED')

class GenderTypes(models.TextChoices):
    MALE = 'MALE',_('MALE')
    FEMALE = 'FEMALE',_('FEMALE')
    TRANSGENDER = 'TRANSGENDER',_('TRANSGENDER')
    PREFER_NOT_TO_SAY = 'PREFER_NOT_TO_SAY',_('PREFER_NOT_TO_SAY')

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    last_name = models.CharField(max_length=200, null=True, blank=True, default=None)
    phone = models.CharField(max_length=15, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    account_status = models.CharField(
        max_length=20,
        choices=AccountStatus.choices,
        default=AccountStatus.PENDING_EMAIL
    )
    pseudonym = models.CharField(max_length=100,unique=True,null=True,blank=True)
    is_verified_artist = models.BooleanField(default=False)

class EmailVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='verification')
    token = models.CharField(max_length=100)
    is_valid = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)

class PersonalVerification(models.Model):
    user = models.ForeignKey("users.User", related_name="personal_verification", on_delete=models.CASCADE)
    fullname = models.CharField(max_length=300)
    address = models.TextField()
    phone_number = models.CharField(max_length=200)

class DocumentVerification(models.Model):
    user = models.ForeignKey("users.User", related_name="document_verification", on_delete=models.CASCADE)
    document = models.OneToOneField("files.File", related_name = "verification_document", on_delete=models.CASCADE)

class ArtistVerification(models.Model):
    user = models.ForeignKey("users.User", related_name="artist_verification", on_delete=models.CASCADE)
    personal_verification = models.OneToOneField(PersonalVerification, related_name ="verify_artist", on_delete=models.CASCADE)
    document_verification =models.OneToOneField(DocumentVerification, related_name="verify_artist", on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)

class Profile(models.Model):
    user = models.OneToOneField(User,primary_key=True,related_name="profile", on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True,blank=True)
    gender = models.CharField(max_length=25,null=True,blank=True,choices=GenderTypes.choices)
    bio = models.TextField(null=True,blank=True)
    location = models.CharField(max_length=50,null=True,blank=True)
    country = models.CharField(max_length=50,null=True,blank=True)
    karma = models.IntegerField(null=True,blank=True)
    profile_picture = models.ForeignKey("files.File", related_name = "profile_picture",null=True,blank=True, on_delete=models.CASCADE)
    facebook = models.URLField(null=True,blank=True, max_length=300)
    instagram = models.URLField(null=True,blank=True, max_length=300)
    linkedin = models.URLField(null=True,blank=True, max_length=300)
    twitter = models.URLField(null=True,blank=True, max_length=300)
    created_date = models.DateTimeField(auto_now_add=True)

class Follow(models.Model):
    user_from = models.ForeignKey("users.User", related_name="followings",on_delete=models.CASCADE)
    user_to = models.ForeignKey("users.User", related_name="followers", on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.user_from == self.user_to:
            raise ValidationError("Can't follow self")
        super(Follow, self).save(*args, **kwargs)

    class Meta:
        unique_together = [['user_from','user_to']]

class UserCollection(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey("users.User", related_name="collections", on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)

class ClipCollection(models.Model):
    collection = models.ForeignKey(UserCollection, related_name="clips",on_delete=models.CASCADE)
    clip = models.ForeignKey("clips.Clip", related_name="collected_clips",on_delete=models.CASCADE)
