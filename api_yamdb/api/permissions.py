from rest_framework import permissions


class AdminOrSuperUserOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.user.is_authenticated and (
            request.user.role == 'admin' or request.user.role == 'user')
        )


class AdminOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.role == 'admin'


class StaffOrAuthorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        roles = ['user', 'moderator', 'admin']
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.user.is_superuser:
            return True
        elif request.user.is_authenticated:
            return request.user.role in roles
        else:
            return False


class IsAdminOrReadOnlyPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return request.user.role == 'admin'
