from rest_framework import permissions


class AuthenticatedOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
                request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated and request.user)
            )

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS


class ReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS
