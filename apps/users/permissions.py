from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import User


class ClipOwnerOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj.user:
            return request.user.is_authenticated 
        else:
            return request.method in SAFE_METHODS

# TODO have to redo
class OwnerOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj.user:
            return request.user.is_authenticated 
        else:
            return request.method in SAFE_METHODS

class AuthorizedUserOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return super().has_permission(request, view)
        else:
            return request.user.is_authenticated 
        
class CampaignOwnerOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj.owner:
            return request.user.is_authenticated 
        else:
            return request.method in SAFE_METHODS