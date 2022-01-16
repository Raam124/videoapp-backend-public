"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter


from apps.users import views as UserViews
from apps.files import views as FileViews
from apps.clips import views as ClipViews
from apps.common import views as CommonViews


router = DefaultRouter()
router.register('auth', UserViews.AuthViewset, basename='auth')
router.register('files', FileViews.FileViewSet, basename='files')
router.register('users', UserViews.UserViewset, basename='users')
router.register('profiles', UserViews.ProfileViewSet, basename='profiles')
router.register('clips',ClipViews.ClipViewSet,basename='clips')
router.register('likes',ClipViews.LikeViewSet,basename='likes')
router.register('follows',UserViews.FollowViewSet,basename='follows')
router.register('collections',UserViews.CollectionViewet,basename='collections')
router.register('clip-collections',UserViews.ClipColllectionViewSet,basename='clip-collections')
router.register('comments',ClipViews.CommentViewSet,basename='comments')
router.register('tags',ClipViews.TagViewSet,basename='tags')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),

    path('api/auth/token/', UserViews.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/request-reset-password/', UserViews.RequestResetPassword.as_view(), name='auth-request-reset-password'),
    path('api/auth/password-reset/', UserViews.ResetPassword.as_view(), name='auth-reset-password'),
    path('api/auth/change-password/', UserViews.ChangePassword.as_view(), name='auth-change-password'),

    # path('api/files/', FileViews.FileUploadView.as_view()),
    # path('api/files/<uuid:id>/', FileViews.FileUploadView.as_view()),
    # path('api/file-sucess/<uuid:id>/', FileViews.FileUploadSuccessView.as_view()),

    path('api/notifications/',CommonViews.NotificationView.as_view(),name='notifications'),
    path('api/notifications/<int:id>/',CommonViews.NotificationDetailView.as_view(),name='detail_notification'),
]
