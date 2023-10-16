from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from recipes.models import (Cart, Favorite, Ingredient, IngredientsOfRecipe,
                            Recipe, Subscription, Tag, User)
from .filters import ChangSearchForName, FilterForRecipe
from .pagination import UserPagination
from .permission import AuthorOrReadOnly
from .serializers import (CartSerializer, DjoserUserSerializer,
                          FavoriteSerializer, IngredientsSerializer,
                          PostRecipesSerializer, PostSubscribeSerializer,
                          RecipesSerializer, SubscribeUserSerializer,
                          TagsSerializer)


class DjoserUserViewSet(UserViewSet):
    """Представление пользователей."""

    queryset = User.objects.all()
    serializer_class = DjoserUserSerializer
    pagination_class = UserPagination
    permission_classes = (AuthorOrReadOnly,)

    def get_permissions(self):
        if self.action == 'me':
            return [IsAuthenticated(), ]
        if self.action == 'create':
            return [AllowAny(), ]
        return [AuthorOrReadOnly(), ]

    @action(methods=['get'],
            permission_classes=(IsAuthenticated,),
            detail=False,)
    def subscriptions(self, request):
        """Все подписки пользователя."""
        page = self.paginate_queryset(User.objects.filter(
            following__subscriber=request.user))
        serializer = SubscribeUserSerializer(page, many=True,
                                             context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,),
            detail=True)
    def subscribe(self, request, id):
        """Подписка."""
        get_object_or_404(User, id=id)
        if request.method == 'POST':
            subscriber = request.user
            data = {'subscriber': subscriber.id, 'author': id}
            serializer = PostSubscribeSerializer(data=data,
                                                 context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        data = Subscription.objects.filter(subscriber_id=request.user.id,
                                           author_id=id)
        if data.exists():
            data.delete()
            return Response({'Успех': 'Вы отписаны от автора'},
                            status=status.HTTP_204_NO_CONTENT)
        return Response({'Ошибка': 'Неверные данные'},
                        status=status.HTTP_400_BAD_REQUEST)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление тэгов."""

    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None


class RecipesViewsSet(ModelViewSet):
    """Представление рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FilterForRecipe
    pagination_class = UserPagination

    def get_serializer_class(self):
        """Выбор серилизатора."""
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return PostRecipesSerializer
        return RecipesSerializer

    def perform_create(self, serializer):
        """Создание рецепта."""
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        """Изменение созданного рецепта."""
        serializer.save(author=self.request.user)

    @staticmethod
    def shopping_cart_and_favorite_serialization(serializer, request, pk):
        context = {'request': request}
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['post', 'delete'],
            permission_classes=[IsAuthenticated],
            detail=True,
            )
    def shopping_cart(self, request, pk):
        """Добавление/удаление рецепта в корзину."""
        if request.method == 'POST':
            return self.shopping_cart_and_favorite_serialization(
                CartSerializer, request, pk)
        data = Cart.objects.filter(
            user_id=request.user.id, recipe_id=pk)
        if data.exists():
            data.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        get_object_or_404(Recipe, id=pk)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post', 'delete'],
            permission_classes=[IsAuthenticated],
            detail=True)
    def favorite(self, request, pk):
        """Добавление/удаление избранных рецептов."""
        if request.method == 'POST':
            return self.shopping_cart_and_favorite_serialization(
                FavoriteSerializer, request, pk)

        data = Favorite.objects.filter(user=request.user, recipe__id=pk)
        if data.exists():
            data.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        get_object_or_404(Recipe, id=pk)
        return Response({'ошибка': 'Такого рецепта нет'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'],
            permission_classes=[IsAuthenticated],
            detail=False)
    def download_shopping_cart(self, request):
        """Скачивание рецепта."""
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

            filename = 'Список покупок.txt'
            response = HttpResponse(shop_cart,
                                    content_type='text/plain')
            response['Content-Disposition'] = (f'attachment; '
                                               f'filename={filename}')
            return response
        return Response(status=status.HTTP_400_BAD_REQUEST)


class IngredientsViewsSet(viewsets.ReadOnlyModelViewSet):
    """Представление ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('^name',)
    filterset_class = ChangSearchForName
