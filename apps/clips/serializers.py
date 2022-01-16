from django.db.models import fields
from rest_framework import serializers
from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework.fields import SerializerMethodField
from rest_framework.relations import RelatedField

from .models import Clip, Comment, Like, Tag
from apps.users.serializers import BasicUserSerializer
from apps.files.serializers import FileSerializer

class LikeSerializer(serializers.ModelSerializer):

    liked_user = serializers.SerializerMethodField(required=False)

    def get_liked_user(self, obj):
        return obj.liked_user_id

    class Meta:
        model = Like
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class ClipSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField(required=False)
    likes = serializers.SerializerMethodField(read_only=True)
    likes_count = serializers.SerializerMethodField(read_only=True)
    tags = TagSerializer(many=True,read_only=True)
    file = serializers.SerializerMethodField(read_only=True)

    def get_file(self,obj):
        return FileSerializer(obj.file,read_only=True).data

    def get_likes(self, obj):
        flat_list = [item for sublist in obj.likes.values_list(
            'liked_user_id') for item in sublist]
        return flat_list

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_user(self, obj):
        return obj.user.id

    class Meta:
        model = Clip
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):

    replies = SerializerMethodField()
    user = serializers.SerializerMethodField(read_only=True)

    def get_user(self,obj):
        return BasicUserSerializer(obj.user).data

    def get_replies(self, obj):
        replies = CommentSerializer(obj.replies.all(), many=True)
        return replies.data

    class Meta:
        model = Comment
        fields = '__all__'
        extra_kwargs = {"user": {"required": False, "read_only": True}}


class TrendingClipSerializer(serializers.ModelSerializer):

    likes_count = serializers.SerializerMethodField(read_only=True)
    comments_count = serializers.SerializerMethodField(read_only=True)
    file = FileSerializer(read_only=True)

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self,obj):
        return obj.comments.count()

    class Meta:
        model = Clip
        fields = '__all__'
        

class SimpleClipSerializer(serializers.ModelSerializer):
    
    file = FileSerializer(read_only=True)

    class Meta:
        model = Clip
        exclude = ['description','user','tags']