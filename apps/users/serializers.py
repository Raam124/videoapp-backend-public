from django.contrib.auth.password_validation import validate_password
from django.db.models import fields
from django.shortcuts import get_object_or_404

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import ClipCollection, UserCollection, User,Profile,Follow
from apps.clips.models import Clip

from apps.files.serializers import FileSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super(CustomTokenObtainPairSerializer, self).validate(attrs)
        data.update({'id': self.user.id})
        return data

class AuthRegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        exclude = [
            'username', 'is_superuser', 'last_login', 'is_staff', 'groups', 'user_permissions'
        ]

class BasicUserSerializer(serializers.ModelSerializer):

    karma = serializers.SerializerMethodField(read_only=True)
    profile_picture = serializers.SerializerMethodField(read_only=True)
    

    def get_profile_picture(self,obj):
        return FileSerializer(obj.profile.profile_picture).data

    def get_karma(self,obj):
        return obj.profile.karma

    class Meta:
        model = User
        fields = ['id','first_name','last_name','karma','profile_picture','pseudonym']

class UserRequestResetPasswordSerializer(serializers.Serializer):
    email = serializers.CharField()


class UserResetPasswordSerializer(serializers.ModelSerializer):
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, data):
        if data.get('new_password') != data.get('new_password_confirm'):
            raise serializers.ValidationError("Passwords don't match.")

        return data

    class Meta:
        model = User
        fields = ['new_password', 'new_password_confirm', 'token']


class UserChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    class Meta:
        model = User
        fields = ['old_password', 'new_password']

class ProfileSerializer(serializers.ModelSerializer):
    user = BasicUserSerializer(read_only=True)
 
    class Meta:
        model = Profile
        fields = '__all__'
        extra_kwargs = {"user": {"required": False,"read_only":True},"karma":{"read_only":True}}


class ClipInCollectionSerializer(serializers.ModelSerializer):


    # art = serializers.SerializerMethodField(read_only=True)

    # def get_art(self,obj):
    #     return FileSerializer(obj.art.file,read_only=True).data

    class Meta:
        model = ClipCollection
        fields = '__all__'


class CollectionSerializer(serializers.ModelSerializer):
    
    arts = ClipInCollectionSerializer(read_only=True,many=True)
    user_id = serializers.SerializerMethodField()

    def get_user_id(self,obj):
        return obj.user_id

    class Meta:
        model = UserCollection
        exclude = ['user']

class BasicCollectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserCollection
        exclude = ['user']

class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields ='__all__'
        extra_kwargs = {"user_from": {"required": False,"read_only":True}}

