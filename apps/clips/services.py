from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from .models import Clip,Like, Tag
from .serializers import LikeSerializer,ClipSerializer
from django.db import transaction

@transaction.atomic
def like_clips(request_data,clip_id,user):
    try:
        serializer = LikeSerializer(data={'liked_clip':request_data.get('clip')})
        if serializer.is_valid(raise_exception=True):
            serializer.save(liked_user=user)
        return serializer.data
    except Exception as e:
        print(e)
        raise ValidationError("Something went wrong")

@transaction.atomic
def unlike_clip(request_data,clip_id,user):
    try:
        like = get_object_or_404(Like,liked_clip_id=clip_id,liked_user = user)
        like.delete()
    except Exception as e:
        print(e)
        raise ValidationError("Something went wrong")

def get_likes(id):
    likes = []
    like = Like.objects.filter(liked_clip_id=id) 
    serializer = LikeSerializer(like,many=True)
    for data in serializer.data:
        likes.append(data['liked_user'])

    data ={
        "total_likes":like.count(),
        "liked_by" : likes
    }

    return data

def add_tags(request_data,clip):
    if len(request_data) > 5:
        raise ValueError("List too long to process")

    existing_tags_data = []
    new_tags_data = []

    for data in request_data:
        name = data.lower()
        if not Tag.objects.filter(name=name).exists():                
            obj = Tag(name=name)
            new_tags_data.append(obj)
        else:
            existing_obj = get_object_or_404(Tag,name=name)
            existing_tags_data.append(existing_obj)

    new_tagies = Tag.objects.bulk_create(new_tags_data)
    tagies = [*new_tagies, *existing_tags_data] 

    clip.tags.add(*tagies)
