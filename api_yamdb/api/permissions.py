from rest_framework import permissions


class AdminOrSuperUserOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.user.is_authenticated and (
            request.user.role == 'admin' or request.user.role == 'user')
        )


class AdminOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        elif request.user.is_authenticated and request.user.is_admin:
            return True


class StaffOrAuthorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)


class IsAdminOrReadOnlyPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.user.is_superuser:
            return True
        elif (
            request.user.is_authenticated
            and request.user.role == 'admin'
        ):
            return True
        else:
            return False


class CommentsAndViewsPermission(permissions.BasePermission):

    def has_permissions(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.method == 'POST':
            return request.user.role == 'admin'
        elif request.method in ['DEL', 'PATCH']:
            return (request.user.role in ['moderator', 'admin'] or
                    request.user.id == request.data.get('author'))
        else:
            return False
