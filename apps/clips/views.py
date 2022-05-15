from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404,get_list_or_404
from django.core.exceptions import PermissionDenied

from rest_framework import request, serializers, viewsets, permissions, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import filters
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers

from .models import Clip, Comment,Like, Tag
from .serializers import ClipSerializer, CommentSerializer, LikeSerializer, SimpleClipSerializer, TagSerializer, TrendingClipSerializer
from .services import add_tags, get_likes, like_clips, unlike_clip

from apps.users.permissions import ClipOwnerOnly,AuthorizedUserOnly,OwnerOnly
from apps.users.models import User
from apps.common.models import Notification,NotificationType

from .paginations import ClipResultPagination

class ClipViewSet(viewsets.ModelViewSet):

    serializer_class = ClipSerializer
    permission_classes = [ClipOwnerOnly]
    queryset = Clip.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']
    pagination_class = ClipResultPagination

    def get_serializer_class(self):
        if self.action == 'list':
            return SimpleClipSerializer
        else:
            return super().get_serializer_class()

    def get_queryset(self):
        return super().get_queryset()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        return super().perform_update(serializer)

    def perform_destroy(self, instance):
        return super().perform_destroy(instance)

    @action(methods=['get'], detail=False, permission_classes=[],
            url_path="(?P<user_id>[^/.]+)/user-clips", url_name='get_user_clips')
    def get_user_clips(self,request,user_id):
        user = get_object_or_404(User,pk=user_id)
        serializer = ClipSerializer(self.paginate_queryset(queryset=user.clips.all().order_by('created_date')),many=True)
        return Response(self.get_paginated_response(serializer.data).data,status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, permission_classes=[],
            url_path="trending", url_name='get_trending_clips')
    def get_trending_clips(self,request):

        most_liked_clips = Clip.objects.annotate(likes_count=Count('likes')).order_by('-likes_count')

        return Response(TrendingClipSerializer(most_liked_clips,many=True).data,status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, permission_classes=[],
            url_path="follows", url_name='get_followers_clips')
    def get_followers_clips(self,request):
        following_users = []
        clips = []
        for following in request.user.followings.all(): following_users.append(following.user_to)
        for following_user in following_users:clips.append(following_user.clips.all())
        flat_list = [item for sublist in clips for item in sublist]
        return Response(SimpleClipSerializer(flat_list,many=True).data,status=status.HTTP_200_OK)

    @action(methods=['post','delete'], detail=False, permission_classes=[permissions.IsAuthenticated],
            url_path="(?P<clip_id>[^/.]+)/tags", url_name='add_clip_tags')
    def add_clip_tags(self,request,clip_id):
        clip = get_object_or_404(Clip,pk=clip_id)

        if request.method == 'POST':
            add_tags(request.data,clip)
            return Response(status = status.HTTP_200_OK)

        if request.method == 'DELETE':
            tag = get_object_or_404(Tag,name=request.data['tag'])
            clip.tags.remove(tag)
            return Response(status=status.HTTP_204_NO_CONTENT)
            

    @action(methods=['get'], detail=False, permission_classes=[permissions.IsAuthenticated],
            url_path="(?P<clip_id>[^/.]+)/similar-clips", url_name='get_similar_clips')
    def get_similar_clips(self,request,clip_id):

        clip = get_object_or_404(Clip,pk=clip_id)
        similar_clips = []

        for tag in clip.tags.all():
            for clip in tag.clips.exclude(id=clip_id)[:25]:
                similar_clips.append(clip)
            
        serializer = SimpleClipSerializer(set(similar_clips),many=True)
        return Response(serializer.data, status = status.HTTP_200_OK)


    @action(methods=['get'], detail=False, permission_classes=[permissions.IsAuthenticated],
            url_path="tags", url_name='get_tag_related_clips')
    def get_tag_related_clips(self,request):
        tag = request.query_params.get('tag')
        if tag is not None:
            tag = get_object_or_404(Tag,name=tag)
            serializer  = SimpleClipSerializer(self.paginate_queryset(tag.clips.all().order_by('created_date')),many=True)
            return Response(self.get_paginated_response(serializer.data).data, status = status.HTTP_200_OK)
        else:
            return Response(SimpleClipSerializer(Clip.objects.all(),many=True).data, status = status.HTTP_200_OK)


class LikeViewSet(viewsets.ViewSet):

    permission_classes = [AuthorizedUserOnly]

    def retrieve(self,request,pk=None):
        data = get_likes(pk)
        return Response(data,status=status.HTTP_200_OK)

    def create(self,request):
        perform = self.request.query_params.get('perform')
        liked_clip = request.data['clip']

        if perform == 'like':
            like = like_clips(request.data,liked_clip,request.user)
            clip = get_object_or_404(Clip,pk=liked_clip)
            Notification.objects.create(message = "Liked your Clip",clip_id = liked_clip,type=NotificationType.LIKE,user_by=request.user,user_to=clip.user)
            return Response(like,status=status.HTTP_200_OK)

        elif perform == 'unlike':
            unlike_clip(request.data,liked_clip,request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [OwnerOnly]
    queryset = Comment.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        try:
            clip = get_object_or_404(Clip,pk=self.request.data['clip'])
            if 'parent_comment' in self.request.data:
                parent_comment = get_object_or_404(Comment,pk=self.request.data['parent_comment'])
                Notification.objects.create(message = "Replied to your comment",clip_id = self.request.data['clip'],type=NotificationType.REPLY,
                    user_by=self.request.user,user_to_id=parent_comment.user_id,comment_id=serializer.data.get('id'))
            else:
                Notification.objects.create(message = "Commented on your clip",clip_id = self.request.data['clip'],type=NotificationType.COMMENT,
                    user_by=self.request.user,user_to=clip.user,comment_id=serializer.data.get('id'))
        except Exception as e :
            print(e)
            pass
    
    def perform_destroy(self, instance):
        return super().perform_destroy(instance)

    def perform_update(self, serializer):
        return super().perform_update(serializer)

    @action(methods=['get'], detail=False, permission_classes=[],
            url_path="clip/(?P<clip_id>[^/.]+)", url_name='get_comments')
    def get_art_comments(self,request,clip_id):
        clip =get_object_or_404(Clip,pk=clip_id)
        serializer = CommentSerializer(clip.comments.filter(parent_comment=None),many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)


class TagViewSet(viewsets.ViewSet):

    permission_classes = [permissions.IsAuthenticated]

    def create(self,request):
        raise PermissionDenied("Tags creation not allowded")

    def get(self,request):
        name = request.query_params.get('name')
        if name:
            serializer = TagSerializer(Tag.objects.filter(name__contains=name),many=True)
        else:
            serializer = TagSerializer(Tag.objects.all(),many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
