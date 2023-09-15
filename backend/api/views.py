from django.contrib.auth import get_user_model
from django.shortcuts import render
from djoser.views import UserViewSet
from rest_framework import viewsets
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated

from .pagination import UserPagination
from .permission import AuthenticatedOrReadOnly, ReadOnly
from .serializers import (DjoserUserSerializer, TagsSerializer,
                          RecipesSerializer, IngredientsSerializer,
                          PostRecipesSerializer, )
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
    pagination_class = None


class RecipesViewsSet(ModelViewSet):
    """Представление рецептов."""

    queryset = Recipes.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostRecipesSerializer
        return RecipesSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class IngredientsViewsSet(ModelViewSet):
    """Представление игридиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
