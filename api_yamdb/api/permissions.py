from rest_framework import permissions


def check_post(request):
    roles = ['user', 'moderator', 'admin']
    return (request.method == 'POST' and request.user.role in roles)


def check_patch_delete(request, obj):
    roles = ['moderator', 'admin']
    methods = ['PATCH', 'DELETE']
    return (request.method in methods
            and (request.user.role in roles
                 or request.user == obj.author))


class AdminOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.user.is_superuser
                or request.user.is_authenticated and request.user.is_admin)


class StaffOrAuthorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_superuser
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_superuser
                or (request.user.is_authenticated
                    and (check_patch_delete(request, obj)
                         or check_post(request))))


class IsAdminOrReadOnlyPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_superuser or request.user.is_authenticated
                and request.user.role == 'admin')
