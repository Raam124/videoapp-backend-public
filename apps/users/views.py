from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404


from .serializers import AuthRegisterSerializer,UserSerializer,UserRequestResetPasswordSerializer
from .services import register_user,confirm_email_verification,send_verification_email,request_password_reset,password_reset,change_password
from .models import EmailVerification,AccountStatus,User


class AuthViewset(ViewSet):
    @action(methods=['post'], detail=False, permission_classes=[], url_path='register', url_name='register')
    def register(self, request):
        serializer = AuthRegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = register_user(request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)

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

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated], url_path='me', url_name='me')
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

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