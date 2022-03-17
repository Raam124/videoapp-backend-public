from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

class NotificationType(models.TextChoices):
    FOLLOW = 'FOLLOW', _('FOLLOW')
    LIKE = 'LIKE', _('LIKE')
    COMMENT = 'COMMENT', _('COMMENT')
    REPLY = 'REPLY',_('REPLY')

class Notification(models.Model):
    user_to = models.ForeignKey("users.User", related_name ="notifications", on_delete=models.CASCADE)
    user_by = models.ForeignKey("users.User", related_name ="created_notifications", on_delete=models.CASCADE)
    clip = models.ForeignKey("clips.Clip", related_name ="notifications", null=True,blank=True,on_delete=models.CASCADE)
    comment = models.ForeignKey("clips.Comment", related_name ="notifications",null=True,blank=True, on_delete=models.CASCADE)
    type = models.CharField(max_length=100,choices=NotificationType.choices)
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.user_by == self.user_to:
            pass
        else:
            super(Notification, self).save(*args, **kwargs) 