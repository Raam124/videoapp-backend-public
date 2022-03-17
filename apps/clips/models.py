from django.db import models
import uuid

from apps.users.models import User
from apps.files.models import File

class Tag(models.Model):
    name = models.CharField(max_length=50,unique=True)

class Clip(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name="clips", on_delete=models.CASCADE)
    file = models.ForeignKey(File, related_name="clips", on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, related_name = "clips" )

class Like(models.Model):
    liked_user = models.ForeignKey("users.User", related_name="liked_clips", on_delete=models.CASCADE)
    liked_clip = models.ForeignKey(Clip, related_name="likes", on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['liked_user','liked_clip']]

class Comment(models.Model):
    clip = models.ForeignKey(Clip, related_name="comments",on_delete=models.CASCADE)
    user = models.ForeignKey("users.User", related_name="commenter",on_delete=models.CASCADE)
    comment_text = models.CharField(max_length=100)  
    parent_comment = models.ForeignKey("self", related_name="replies", null=True,blank=True, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
