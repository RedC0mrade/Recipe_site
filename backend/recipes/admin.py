from django.contrib import admin

from .models import (Cart, Favorite, IngredientsOfRecipe, Ingredient,
                     Recipes, Subscriptions, Tags, User)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Админка корзины."""

    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    empty_value_display = '=пусто='


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админка Избранного."""

    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    empty_value_display = '=пусто='


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка ингредиентов."""

    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)
    empty_value_display = '=пусто='


@admin.register(IngredientsOfRecipe)
class IngredientsOfRecipeAdmin(admin.ModelAdmin):
    """Админка игнредиентов рецепта."""

    list_display = ('recipe', 'ingredient', 'amount')
    search_fields = ('recipe', 'ingredient', 'amount')
    list_filter = ('recipe', 'ingredient', 'amount')
    empty_value_display = '=пусто='


class RecipeIngredientAdmin(admin.StackedInline):
    """Передача ингредиентов в админку рецептов."""

    model = IngredientsOfRecipe
    autocomplete_fields = ('ingredient',)
    min_num = 1


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    """Админка рецептов."""

    list_display = ('id', 'author_name', 'name', 'text', 'cooking_time',
                    'recipes_ingredients', 'recipes_tags', 'favorite_count',
                    'image')
    list_filter = ('tags', 'author', 'name')
    search_fields = ('name', 'cooking_time', 'tags__name',
                     'author__email', 'ingredients__name')
    empty_value_display = '=пусто='
    inlines = (RecipeIngredientAdmin,)

    @admin.display(description='автор')
    def author_name(self, obj):
        """Возвращаем юзернэйм автора рецепта."""
        return obj.author.username

    @admin.display(description='теги')
    def recipes_tags(self, obj):
        """Возвращаем тэги рецепта."""
        result = []
        for tag in obj.tags.all():
            result.append(tag.name)
        return ', '.join(result)

    @admin.display(description='ингридиенты')
    def recipes_ingredients(self, obj):
        """Возвращаем ингредиенты рецепта."""
        result = []
        for ingredient in obj.ingredients.all():
            result.append(ingredient.name[0].upper() + ingredient.name[1:])
        return ', '.join(result)

    @admin.display(description='отметок в избраном')
    def favorite_count(self, obj):
        """Возвращаем количество отметок в избраном у рецепта."""
        return obj.favorites.count()


@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    """Админка подписок."""

    list_display = ('author', 'subscriber')
    search_fields = ('author', 'subscriber')
    list_filter = ('author', 'subscriber')
    empty_value_display = '=пусто='


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    """Админка тэгов."""

    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('id', 'name', 'color', 'slug')
    list_filter = ('id', 'name', 'color', 'slug')
    empty_value_display = '=пусто='


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Админка пользователей."""

    list_display = ('id', 'email', 'username', 'first_name',
                    'last_name', 'password')
    search_fields = ('email', 'username', 'first_name',
                     'last_name', 'password')
    list_filter = ('email', 'username', 'first_name', 'last_name')
    empty_value_display = '=пусто='
