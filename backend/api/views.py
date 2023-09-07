from django.contrib.auth import get_user_model
from django.shortcuts import render
from djoser.views import UserViewSet
from rest_framework import viewsets

from .pagination import UserPagination
from .permission import AuthenticatedOrReadOnly
from .serializers import DjoserUserSerializer

User = get_user_model()


class DjoserUserViewSet(UserViewSet):
    """Представление пользователей."""
    
    queryset = User.objects.all()
    serializer_class = DjoserUserSerializer
    pagination_class = UserPagination
    permission_classes = (AuthenticatedOrReadOnly,)
