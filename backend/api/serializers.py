from abc import ABC

from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from recipes.models import Tags, User, Subscriptions, Recipes, Ingredient


class DjoserUserSerializer(UserSerializer):
    """Переделаный из joser сериализатор пользователя."""

    is_subscribed = SerializerMethodField(read_only=True)

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        else:
            return Subscriptions.objects.filter(subscriber=user,
                                                author=obj).exists()

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'is_subscribed',)


class DjoserUserCreateSerializer(UserCreateSerializer):
    """Переделаный из joser сериализатор создания пользователя."""

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'password', 'id')


class TagsSerializer(ModelSerializer):
    """Сериализатор тэгов."""

    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug')


class RecipesSerializer(ModelSerializer):
    """Сериализатор рецептов."""

    class Meta:
        models = Recipes
        fields = ('tags', 'image', 'name', 'text', 'cooking_time')


class IngredientsSerializer(ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        models = Ingredient
        fields = ('name', 'measurement_unit')
