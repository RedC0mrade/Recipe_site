from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404
from djoser.views import UserViewSet
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated

from .pagination import UserPagination
from .permission import AuthenticatedOrReadOnly, ReadOnly
from .serializers import (DjoserUserSerializer, TagsSerializer,
                          RecipesSerializer, IngredientsSerializer,
                          PostRecipesSerializer, RecipeCartSerializer, )
from recipes.models import Tags, User, Recipes, Ingredient, Cart, \
    IngredientsOfRecipe


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
    pagination_class = UserPagination
    permission_classes = (AuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        """Выбор серилизатора"""
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return PostRecipesSerializer
        return RecipesSerializer

    def perform_create(self, serializer):
        """Создание рецепта"""
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        """Изменение созданного рецепта"""
        serializer.save(author=self.request.user)

    @action(methods=['post', 'delete'],
            permission_classes=[IsAuthenticated],
            detail=True)
    def shopping_cart(self, request, pk):
        """Добавление/удаление рецепта в корзину"""
        if request.method == 'POST':
            if not Cart.objects.filter(user=request.user,
                                       recipe__id=pk).exists():
                recipe = get_object_or_404(Recipes, id=pk)
                Cart.objects.create(user=request.user, recioe=recipe)
                serializer = RecipeCartSerializer(recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response({'ошибка': 'Рецепт уже в корзине'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            if Cart.objects.filter(user=request.user, recipe__id=pk).exists():
                Cart.objects.filter(user=request.user, recipe__id=pk).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'ощибка': 'Такого рецепта нет'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(permission_classes=[IsAuthenticated],
            detail=True)
    def download_shopping_cart(self, request):
        """Скачивание рецепта"""
        if request.user.shopping_cart.exists():
            ingredients_recipe = IngredientsOfRecipe.objects.filter(
                recipe__shopping_cart__user=request.user)
            values = ingredients_recipe.values('ingredient__name',
                                               'ingredient__measuarement_unit')
            ingredients = values.annotate(amount=Sum('amount'))



class IngredientsViewsSet(ModelViewSet):
    """Представление ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
