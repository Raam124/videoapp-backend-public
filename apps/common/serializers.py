from rest_framework import fields, serializers

from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        exclude = ['user_to']