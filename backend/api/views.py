from django.contrib.auth import get_user_model
from django.shortcuts import render
from djoser.views import UserViewSet
from rest_framework import viewsets

from .pagination import UserPagination
from .serializers import UserSerializer


User = get_user_model()


class MyUserViewSet(UserViewSet):
    """Представление пользователей."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = UserPagination
