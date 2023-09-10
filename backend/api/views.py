from django.contrib.auth import get_user_model
from django.shortcuts import render
from djoser.views import UserViewSet
from rest_framework import viewsets
from rest_framework.viewsets import ModelViewSet

from .pagination import UserPagination
from .permission import AuthenticatedOrReadOnly, ReadOnly
from .serializers import DjoserUserSerializer, TagsSerializer, \
    RecipesSerializer, IngredientsSerializer
from recipes.models import Tags, User, Recipes, Ingredient


class DjoserUserViewSet(UserViewSet):
    """Представление пользователей."""
    
    queryset = User.objects.all()
    serializer_class = DjoserUserSerializer
    pagination_class = UserPagination
    permission_classes = (AuthenticatedOrReadOnly,)


class TagsViewSet(ModelViewSet):
    """Представление тэгов."""

    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (ReadOnly,)


class RecipesViewsSet(ModelViewSet):
    """Представление рецептов."""

    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer


class IngredientsViewsSet(ModelViewSet):
    """Представление игридиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
