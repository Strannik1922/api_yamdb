from rest_framework import permissions


class AdminOrSuperUserOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.user.is_authenticated and (
            request.user.is_admin or request.user.is_superuser)
        )


class AdminOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.role == 'admin'


class StaffOrAuthorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)


class PermissionTrue(permissions.BasePermission):

    def has_permission(self, request, value):
        return True
