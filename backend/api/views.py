from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .pagination import UserPagination
from .permission import AuthenticatedOrReadOnly, ReadOnly
from .serializers import (DjoserUserSerializer, IngredientsSerializer,
                          PostRecipesSerializer, RecipesSerializer,
                          RecipeCartFavoriteSerializer, SubscribeSerializer,
                          TagsSerializer)
from recipes.models import (Cart, Favorite, Ingredient, IngredientsOfRecipe,
                            Recipes, Subscriptions, Tags, User)


class DjoserUserViewSet(UserViewSet):
    """Представление пользователей."""

    queryset = User.objects.all()
    serializer_class = DjoserUserSerializer
    pagination_class = UserPagination
    permission_classes = (AuthenticatedOrReadOnly,)

    @action(methods=['get'],
            permission_classes=(IsAuthenticated,),
            detail=False, )
    def subscriptions(self, request):
        """Все подписки пользователя."""
        page = self.paginate_queryset(Subscriptions.objects.filter(
            subscriber=request.user))
        serializer = SubscribeSerializer(page, many=True,
                                         context={'requests': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,),
            serializer_class=SubscribeSerializer,
            detail=True)
    def subscribe(self, request, **kwargs):
        """Подписка."""
        subscriber = request.user
        author = get_object_or_404(User, id=self.kwargs.get('id'))
        print(author)
        if subscriber == author:
            return Response({'Ошибка': 'Нельзя подписаться на себя'},
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            subscription, _ = Subscriptions.objects.get_or_create(
                subscriber=subscriber, author=author)
            serializer = self.get_serializer(author,
                                             context={'request': request})
            return Response(serializer.data, status.HTTP_201_CREATED)


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
                Cart.objects.create(user=request.user, recipe=recipe)
                serializer = RecipeCartFavoriteSerializer(recipe)
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

    @action(methods=['get'],
            permission_classes=[IsAuthenticated],
            detail=False)
    def download_shopping_cart(self, request):
        """Скачивание рецепта"""
        if request.user.cart.exists():
            ingredients_recipe = IngredientsOfRecipe.objects.filter(
                recipe__cart__user=request.user)
            values = ingredients_recipe.values('ingredient__name',
                                               'ingredient__measurement_unit')
            ingredients = values.annotate(amount=Sum('amount'))

            shop_cart = 'Список покупок.\n'
            list_order = 0
            for ingredient in ingredients:
                list_order += 1
                shop_cart += (f'{list_order}) '
                              f'{ingredient["ingredient__name"][0].upper()}'
                              f'{ingredient["ingredient__name"][1:]} - '
                              f'{ingredient["ingredient__measurement_unit"]} '
                              f'({ingredient["amount"]})\n')

            filename = f'Список покупок.txt'
            response = HttpResponse(shop_cart,
                                    content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename={filename}'
            return response
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post', 'delete'],
            permission_classes=[IsAuthenticated],
            detail=True)
    def favorite(self, request, pk):
        """Добавление/удаление избранных рецептов."""
        if request.method == 'POST':
            if not Favorite.objects.filter(user=request.user,
                                           recipe__id=pk).exists():
                recipe = get_object_or_404(Recipes, id=pk)
                Favorite.objects.create(user=request.user, recipe=recipe)
                serializer = RecipeCartFavoriteSerializer(recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response({'ошибка': 'Рецепт уже в корзине'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            if Favorite.objects.filter(user=request.user,
                                       recipe__id=pk).exists():
                Favorite.objects.filter(user=request.user,
                                        recipe__id=pk).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'ошибка': 'Такого рецепта нет'},
                            status=status.HTTP_400_BAD_REQUEST)


class IngredientsViewsSet(ModelViewSet):
    """Представление ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
