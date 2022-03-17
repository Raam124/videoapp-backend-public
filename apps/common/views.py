from re import sub
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework import filters

from .serializers import NotificationSerializer

class NotificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self,request):
        data = {
            'notification_count': request.user.notifications.all().count(),
            'notifications':NotificationSerializer(request.user.notifications.all(),many=True).data
        }
        return Response(data,status=status.HTTP_200_OK)

class NotificationDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self,request,id):
        notification = request.user.notifications.get(pk=id)
        notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)    