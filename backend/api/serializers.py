from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.validators import UniqueTogetherValidator

from constants import ZERO
from recipes.models import (Cart, Favorite, Ingredient, IngredientsOfRecipe,
                            Recipes, Subscriptions, Tags, User)


class DjoserUserSerializer(UserSerializer):
    """Переделаный из joser сериализатор пользователя."""

    is_subscribed = SerializerMethodField(read_only=True)

    def get_is_subscribed(self, obj):
        """Получение значения подписки пользователя на автора."""
        subscriber = self.context.get('request').user
        return (subscriber.is_authenticated
                and obj.following.filter(subscriber=subscriber).exists())

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'is_subscribed', 'id')


class DjoserUserCreateSerializer(UserCreateSerializer):
    """Переделаный из joser сериализатор создания пользователя."""

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'password', 'id')

        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'password': {'write_only': True},
            'email': {'required': True},
            'username': {'required': True},
        }


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор тэгов."""

    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug')


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientsOfRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientsOfRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        validators = [
            UniqueTogetherValidator(
                queryset=IngredientsOfRecipe.objects.all(),
                fields=['ingredient', 'recipe']
            )
        ]


class RecipesSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""

    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)
    author = DjoserUserSerializer(read_only=True)
    tags = TagsSerializer(read_only=True, many=True)
    ingredients = IngredientsOfRecipeSerializer(
        read_only=True,
        many=True,
        source='ingredients_in_recipe',
    )

    def get_is_favorited(self, obj):
        """Получаем значение, добавлен ли рецепт избранное."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Получаем значение, добавлен ли рецепт в корзину."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.cart.filter(recipe=obj).exists()

    class Meta:
        model = Recipes
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time')


class PostIngredientsOfRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для передачи количества игредиентов в рецепты.

    При POST запросах.
    """

    id = IntegerField(write_only=True)

    class Meta:
        model = IngredientsOfRecipe
        fields = ('id', 'amount')


class PostRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор рецптов запроса POST."""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(), many=True)
    image = Base64ImageField()
    author = DjoserUserSerializer(read_only=True)
    ingredients = PostIngredientsOfRecipeSerializer(many=True)

    class Meta:
        model = Recipes
        fields = ('id', 'author', 'ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')

    def validate(self, attrs):
        """Валидация создания и изменения."""
        ingredients = self.initial_data.get('ingredients')
        ingredients_list = []
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Нужен хоть один ингридиент для рецепта'})
        for ingredient in ingredients:
            value = get_object_or_404(Ingredient, id=ingredient['id'])
            if value in ingredients_list:
                raise ValidationError({'ошибка': 'Ингредиенты не должны '
                                                 'дублироваться'})
            ingredients_list.append(value)
            if ingredient['amount'] <= ZERO:
                raise ValidationError({'ошибка': 'не верно '
                                                 'указано количество'})

        tags = self.initial_data.get('tags')
        tags_list = []
        if not tags:
            raise ValidationError({'ошибка': 'Поле ингредиенты не заполнено'})
        for tag in tags:
            if tag in tags_list:
                raise ValidationError({'ошибка': 'Тэг не должен повторяться'})
            tags_list.append(tag)

        image = self.initial_data.get('image')
        if not image:
            raise ValidationError({'ошибка': 'Поле картинка не заполнено'})

        cooking_time = self.initial_data.get('cooking_time')
        if not cooking_time or cooking_time <= ZERO:
            raise ValidationError({'ошибка': 'Поле время '
                                   'заполнено не корректно'})

        return attrs

    def ingredients_amounts(self, ingredients, recipe):
        recipe_ingredients = []
        for ingredient_data in ingredients:
            amount = ingredient_data['amount']
            recipe_ingredient = IngredientsOfRecipe(
                ingredient_id=ingredient_data.get('id'),
                recipe=recipe,
                amount=amount
            )
            recipe_ingredients.append(recipe_ingredient)
        IngredientsOfRecipe.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data):
        """Создание многострадального рецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipes.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.ingredients_amounts(ingredients, recipe)

        return recipe

    def update(self, instance, validated_data):
        """Обновление пецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        instance.ingredients.clear()
        instance.tags.clear()
        instance.tags.set(tags)
        self.ingredients_amounts(ingredients, instance)
        instance.save()
        return instance

    def to_representation(self, instance):
        """Возвращение созданного рецепта пользователю."""
        request = self.context.get('request')
        context = {'request': request}
        return RecipesSerializer(instance,
                                 context=context).data


class UniversalRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор добавления рецепта в корзину."""

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeUserSerializer(DjoserUserSerializer):
    """Сериализатор подписок."""

    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        fields = ('username', 'email', 'first_name',
                  'last_name', 'is_subscribed', 'id',
                  'recipes', 'recipes_count')
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def get_recipes(self, obj):
        """Получение рецептов автора."""
        recipes = obj.recipes.all()
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        if recipes_limit:
            try:
                recipes = recipes[:int(recipes_limit)]
            except Exception:
                pass
        serializer = UniversalRecipeSerializer(recipes, many=True,
                                               read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        """Количество рецептов автора."""
        return obj.recipes.count()


class PostSubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор создания подписки."""

    class Meta:
        model = Subscriptions
        fields = ('author', 'subscriber')

    def validate(self, data):
        author = data['author']
        subscriber = data['subscriber']
        if Subscriptions.objects.filter(author=author,
                                        subscriber=subscriber).exists():
            raise ValidationError(
                detail='Нельзя подписаться второй раз',
                code=status.HTTP_400_BAD_REQUEST,
            )
        if subscriber == author:
            raise ValidationError(
                detail='Нельзя подписаться на себя',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data

    def to_representation(self, instance):
        return SubscribeUserSerializer(
            instance.author, context=self.context).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранных рецептов."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe',)

    def validate(self, data):
        print(2)
        if self.Meta.model.objects.filter(user=data['user'],
                                          recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Нельзядважды добавить рецепт.')
        return data

    def to_representation(self, instance):
        print(3)
        return UniversalRecipeSerializer(
            instance.recipe,
            context=self.context).data


class CartSerializer(FavoriteSerializer):
    """Сериализатор для карзины."""

    class Meta:
        model = Cart
        fields = ('user', 'recipe',)
