from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password


from .models import User

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