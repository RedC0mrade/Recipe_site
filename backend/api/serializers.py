from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from django.db.models import F
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Ingredient, IngredientsOfRecipe, Recipes,
                            Subscriptions, Tags, User)


class DjoserUserSerializer(UserSerializer):
    """Переделаный из joser сериализатор пользователя."""

    is_subscribed = SerializerMethodField(read_only=True)

    def get_is_subscribed(self, obj):
        subscriber = self.context.get('request').user
        author = obj
        if subscriber.is_anonymous:
            return False
        else:
            return Subscriptions.objects.filter(subscriber=subscriber,
                                                author=author).exists()

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


class TagsSerializer(ModelSerializer):
    """Сериализатор тэгов."""

    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug')


class RecipesSerializer(ModelSerializer):
    """Сериализатор рецептов."""

    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)
    author = DjoserUserSerializer(read_only=True)
    tags = TagsSerializer(read_only=True, many=True)
    ingredients = SerializerMethodField()

    class Meta:
        model = Recipes
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time')

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

    def get_ingredients(self, obj):
        """Получаем добавленные ингредиенты в рецепт."""
        return obj.ingredients.values('id', 'name', 'measurement_unit',
                                      amount=F('ingredients_in_recipe__amount'))


class IngredientsSerializer(ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientsOfRecipeSerializer(ModelSerializer):
    """Сериализатор для ингредиентов в рецепте."""

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['ingredient'] = IngredientsSerializer(instance.ingredient).data
        return data

    class Meta:
        model = IngredientsOfRecipe
        fields = ('ingredient', 'amount')


class PostIngredientsOfRecipeSerializer(ModelSerializer):
    """Сериализатор для передачи количества игредиентов в рецепты
        при POST запросах."""
    id = IntegerField(write_only=True)

    class Meta:
        model = IngredientsOfRecipe
        fields = ('id', 'amount')


class PostRecipesSerializer(ModelSerializer):
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

    def validate_ingredients(self, ingredients):
        """Проверка ингредиентов."""

        ingredients_list = []
        if not ingredients:
            raise ValidationError({'ошибка': 'Поле ингредиенты не заполнено'})
        # ingredients_list = Ingredient.objects.values_list('id', flat=True)
        # for i in value:
        #     if i['id'] in ingredients_list:
        #         raise ValidationError({'ошибка': 'Несуществующий ингредиент'})
        for ingredient in ingredients:
            try:
                value = Ingredient.objects.get(id=ingredient['id'])
            except Exception:
                raise ValidationError({'ошибка': 'Несуществующий ингредиент'})
            if value in ingredients_list:
                raise ValidationError({'ошибка': 'Ингредиенты не должны '
                                                 f'дублироваться'})
            ingredients_list.append(value)
            if ingredient['amount'] <= 0:
                raise ValidationError({'ошибка': 'не указано количество'})
        return ingredients

    def validate_tags(self, tags):
        """Проверка тэгов."""

        tags_list = []
        if not tags:
            raise ValidationError({'ошибка': 'Поле тэг не заполнено'})
        for tag in tags:
            if tag in tags_list:
                raise ValidationError({'ошибка': 'Тэг не должен повторяться'})
            tags_list.append(tag)
        return tags

    def validate_image(self, image):
        """Проверка картинки."""
        if not image:
            raise ValidationError({'ошибка': 'Поле картинка не заполнено'})
        return image

    def validate_cooking_time(self, cooking_time):
        """Проверка времени приготовления."""
        if not cooking_time:
            raise ValidationError({'ошибка': 'Поле время ' 
                                   f'приготовления не заполнено'})
        return cooking_time

    def create(self, validated_data):
        """Создание многострадального рецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipes.objects.create(**validated_data)
        recipe.tags.set(tags)
        recipe_ingredients = []
        for ingredient_data in ingredients:
            ingredient = Ingredient.objects.get(id=ingredient_data['id'])
            amount = ingredient_data['amount']
            recipe_ingredient = IngredientsOfRecipe(
                ingredient=ingredient,
                recipe=recipe,
                amount=amount
            )
            recipe_ingredients.append(recipe_ingredient)
        IngredientsOfRecipe.objects.bulk_create(recipe_ingredients)
        return recipe

    def update(self, instance, validated_data):
        """Обновление пецепта"""
        print(instance)
        print(validated_data)
        try:
            ingredients = validated_data.pop('ingredients')
        except KeyError:
            raise ValidationError({'ошибка': 'Поде Ингредиенты '
                                   f'не заполнено'})
        try:
            tags = validated_data.pop('tags')
        except KeyError:
            raise ValidationError({'ошибка': 'Поле Тэг '
                                   f'не заполнено'})
        try:
            validated_data.pop('image')
        except KeyError:
            raise ValidationError({'ошибка': 'Поле Картинка '
                                   f'не заполнено'})
        instance = super().update(instance, validated_data)
        instance.ingredients.clear()
        instance.tags.clear()
        instance.tags.set(tags)
        recipe_ingredients = []
        for ingredient_data in ingredients:
            ingredient = Ingredient.objects.get(id=ingredient_data['id'])
            amount = ingredient_data['amount']
            recipe_ingredient = IngredientsOfRecipe(
                ingredient=ingredient,
                recipe=instance,
                amount=amount
            )
            recipe_ingredients.append(recipe_ingredient)
        IngredientsOfRecipe.objects.bulk_create(recipe_ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        """Возвращение созданного рецепта пользователю"""
        request = self.context.get('request')
        context = {'request': request}
        return RecipesSerializer(instance,
                                 context=context).data


class RecipeCartFavoriteSerializer(ModelSerializer):
    """Сериализатор добавления рецепта в корзину."""

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор подписок."""

    id = serializers.StringRelatedField(source='author.id', read_only=True)
    username = serializers.StringRelatedField(source='author.username')
    email = serializers.StringRelatedField(source='author.email')
    first_name = serializers.StringRelatedField(source='author.first_name')
    last_name = serializers.StringRelatedField(source='author.last_name')
    is_subscribed = SerializerMethodField(read_only=True)
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = Subscriptions
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
        validators = [UniqueTogetherValidator(
            queryset=Subscriptions.objects.all(),
            fields=['author', 'subscriber'])]
        read_only_fields = ('author',)

    def get_is_subscribed(self, obj):
        """Проверка, подписан ли пользователь на автора."""
        subscriber = self.context['request'].user
        author = obj.author
        if subscriber.is_anonymous:
            return False
        return Subscriptions.objects.filter(author=author,
                                            subscriber=subscriber).exists()

    def get_recipes(self, obj):
        """Получение рецептов автора."""
        recipes = obj.author.recipes.all()
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
            serializer = RecipeCartFavoriteSerializer(recipes, many=True,
                                                      read_only=True)
            return serializer.data
        serializer = RecipeCartFavoriteSerializer(recipes, many=True,
                                                  read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        """Количество рецептов автора."""
        return obj.author.recipes.count()
