from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework import viewsets

# from recipes.models import User

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """Представление пользователей."""

    queryset = User.objects.all()
