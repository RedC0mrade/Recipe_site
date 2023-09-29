from rest_framework import permissions


class AuthenticatedOrReadOnly(permissions.BasePermission):
    """Аутентифицированый пользователь или безопасный метод."""

    def has_permission(self, request, view):
        if request.user.is_anonymous and view.action == 'me':
            return False
        return bool(
            request.method in permissions.SAFE_METHODS
            or request.user
            and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)


class AdminOrReadOnly(permissions.BasePermission):
    """Администратор или безопасный метод."""

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_staff)
