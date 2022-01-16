import re
from typing import Collection
from django.db.models.aggregates import Count
from django.shortcuts import render
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import request, serializers, status, permissions
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import filters
from django.utils.translation import gettext_lazy as _


from django.core.exceptions import PermissionDenied
from rest_framework.permissions import SAFE_METHODS
from django.db.models import Q, query
from django.shortcuts import get_object_or_404
from django.db import IntegrityError

from .serializers import ClipInCollectionSerializer, AuthRegisterSerializer, BasicCollectionSerializer, BasicUserSerializer,UserSerializer,UserRequestResetPasswordSerializer,ProfileSerializer,CollectionSerializer,\
CustomTokenObtainPairSerializer,FollowSerializer
from .services import register_user,confirm_email_verification,send_verification_email,request_password_reset,password_reset,\
change_password,delete_user
from .models import ClipCollection, EmailVerification,AccountStatus, Profile,User,UserCollection,Follow
from .permissions import OwnerOnly

from apps.common.models import Notification, NotificationType
from apps.clips.serializers import SimpleClipSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class AuthViewset(ViewSet):
    @action(methods=['post'], detail=False, permission_classes=[], url_path='register', url_name='register')
    def register(self, request):
        serializer = AuthRegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = register_user(request.data)
            return Response(serializer.data, status=status.HTTP_200_OK) # TODO auto login

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated], url_path='verify-email', url_name='verify_email')
    def verify_email(self,request):
        token = self.request.query_params.get('token')
        confirm_email_verification(request.user,token)
        return Response({token:"Account Verified"}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated], url_path='resend-verify-email', url_name='resend_verify_email')
    def resend_verification_email(self,request):
        send_verification_email(request.user)
        return Response({"Verification Mail Sent"},status=status.HTTP_200_OK)


class UserViewset(ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated,OwnerOnly]
    queryset = User.objects.filter(is_active=True)

    def get_queryset(self):
        return super().get_queryset()

    def destroy(self, request, pk=None):
        delete_user(pk)
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated], url_path='me', url_name='me')
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # TODO - have to redo for activate account
    @action(methods=['post'], detail=False, permission_classes=[OwnerOnly], url_path='activate', url_name='activate')
    def account_activate(self, request):
        user = get_object_or_404(User,pk=request.user.id)
        user.is_active = True
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class RequestResetPassword(APIView):
    serializer_class = UserSerializer
    permission_classes = []

    def post(self, request, format=None):
        serializer = UserRequestResetPasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = get_object_or_404(User, email=request.data['email'])
            request_password_reset(user)
            return Response({"Password Reset Mail Sent"}, status=status.HTTP_200_OK)

class ResetPassword(APIView):
    serializer_class = UserSerializer
    permission_classes = []

    def post(self, request, format=None):
        user = get_object_or_404(User, email=request.data['email'])
        password_reset(user, request.data)
        return Response({"Password Reset Successfull"}, status=status.HTTP_200_OK)

class ChangePassword(APIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, format=None):
        user = request.user
        change_password(user, request.data)
        return Response({}, status=status.HTTP_200_OK)

class ProfileViewSet(ModelViewSet):

    serializer_class = ProfileSerializer
    permission_classes = [OwnerOnly]
    queryset = Profile.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__first_name','user__last_name']

    def get_queryset(self):
        location = self.request.query_params.get('location')
        country = self.request.query_params.get('country')

        if location:
            return Profile.objects.filter(location=location)
        elif country:
            return Profile.objects.filter(country=country)

        return super().get_queryset()
    
    def perform_create(self, serializer):
        raise ValidationError('Profile Creation Not Allowded')
        
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @action(methods=['get'], detail=False, permission_classes=[],
            url_path="basic-profiles", url_name='basic_profiles_list')
    def list_basic_profiles(self,request):
        serializer = BasicUserSerializer(User.objects.all(),many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, permission_classes=[],
            url_path="(?P<id>[^/.]+)/basic-profile", url_name='basic_profile_get')
    def get_basic_profile(self,request,id):
        user = get_object_or_404(User,pk=id)
        serializer = BasicUserSerializer(user)
        return Response(serializer.data,status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, permission_classes=[],
            url_path="top-users", url_name='get_top_users')
    def get_top_users(self,request):
        top_users = User.objects.all() # TODO filter users
        top_users_data = []
        for user in top_users:
            data = {
                'user':BasicUserSerializer(user).data,
                'latest_arts': SimpleClipSerializer(user.arts.all()[:10],many=True).data
            }
            top_users_data.append(data)
        return Response(top_users_data,status=status.HTTP_200_OK)



class FollowViewSet(ModelViewSet):
    
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        try:
            follow = get_object_or_404(Follow,user_from=self.request.user,user_to_id=self.request.data['user_to'])
            follow.delete()
        except:
            serializer.save(user_from=self.request.user)
            try:
                Notification.objects.create(user_by=self.request.user,user_to_id=self.request.data['user_to'],type=NotificationType.FOLLOW,message="Followed you")
            except IntegrityError:
                pass

    @action(methods=['get'], detail=False, permission_classes=[],
            url_path="(?P<user_id>[^/.]+)/followings", url_name='followings')
    def get_followings(self,request,user_id):
        followings = []
        user = get_object_or_404(User,pk=user_id)
        serializer = FollowSerializer(user.followings.all(),many=True)
        for data in serializer.data:
            followings.append(data['user_to'])

        followings_dict = {
            'followings_count':len(followings),
            'followings' : followings            
        } 
        return Response(followings_dict,status=status.HTTP_200_OK)
    
    @action(methods=['get'], detail=False, permission_classes=[],
            url_path="(?P<user_id>[^/.]+)/followers", url_name='followings')
    def get_followers(self,request,user_id):
        followers = []
        user = get_object_or_404(User,pk=user_id)
        serializer = FollowSerializer(user.followers.all(),many=True)
        for data in serializer.data:
            followers.append(data['user_from'])

        followers_dict = {
            'followers_count':len(followers),
            'followers' : followers
        } 
        return Response(followers_dict,status=status.HTTP_200_OK)
      
class CollectionViewet(ModelViewSet):
    serializer_class = CollectionSerializer
    permission_classes = [OwnerOnly]
    queryset = UserCollection.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return super().get_serializer_class()
        else:
            return BasicCollectionSerializer
    
    def get_queryset(self):
       return super().get_queryset()
   
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        return super().perform_update(serializer)
    
    def perform_destroy(self, instance):
        return super().perform_destroy(instance)

    @action(methods=['get'], detail=False, permission_classes=[],
            url_path="(?P<user_id>[^/.]+)/user-collections", url_name='get_user_collections')
    def get_user_collections(self,request,user_id):
        collections = UserCollection.objects.filter(user_id=user_id)
        serializer = CollectionSerializer(collections,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)


class ClipColllectionViewSet(ModelViewSet):
    serializer_class = ClipInCollectionSerializer
    permission_classes = []
    queryset = ClipCollection.objects.all()


    def perform_create(self, serializer):
        collection = get_object_or_404(UserCollection,pk=self.request.data['collection'])
        if self.request.user == collection.user:
            return super().perform_create(serializer)
        else:
            raise PermissionDenied()    

    def perform_destroy(self, instance):
        if self.request.user.id != instance.collection.user_id:
            raise PermissionDenied()
        else:
            return super().perform_destroy(instance)
