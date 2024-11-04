from rest_framework import permissions
from .models import UserProfile

class IsAdminOrStaffPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        try:
            profile = request.user.userprofile
            
            # Admin can do anything
            if profile.user_type == 'admin':
                return True
                
            # Staff permissions
            if profile.user_type == 'staff':
                if request.method in ['GET', 'PUT', 'PATCH']:
                    return True
                if request.method == 'POST' and view.__class__.__name__ != 'ProductListCreate':
                    return True
                return False
                
        except UserProfile.DoesNotExist:
            return False
            
        return False

    def has_object_permission(self, request, view, obj):
        try:
            profile = request.user.userprofile
            
            # Admin can do anything
            if profile.user_type == 'admin':
                return True
                
            # Staff can only access their own objects
            if hasattr(obj, 'user'):
                return obj.user == request.user
            return False
            
        except UserProfile.DoesNotExist:
            return False 