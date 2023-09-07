from abc import ABC

from djoser.serializers import UserSerializer, UserCreateSerializer, \
    TokenCreateSerializer
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from recipes.models import User


class DjoserUserSerializer(UserSerializer):
    """Переделаный из joser сериализатор пользователя."""

    # is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name')


class DjoserUserCreateSerializer(UserCreateSerializer):
    """Переделаный из joser сериализатор создания пользователя."""

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'password', 'id')


