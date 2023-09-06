from django.contrib import admin

from .models import (Cart, Favorite, Ingredient, IngredientsOfRecipe,
                     Recipes, Subscriptions, Tags, User)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    empty_value_display = '=пусто='


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    empty_value_display = '=пусто='


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('name',)
    empty_value_display = '=пусто='


@admin.register(IngredientsOfRecipe)
class IngredientsOfRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
    search_fields = ('recipe', 'ingredient', 'amount')
    list_filter = ('recipe', 'ingredient', 'amount')
    empty_value_display = '=пусто='


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    list_display = ('author_name', 'name', 'text', 'cooking_time',
                    'recipes_ingredients', 'recipes_tag', )
    list_filter = ('tag', 'author', 'name')
    search_fields = ('name', 'cooking_time', 'tags__name',
                     'author__email', 'ingredients__name')
    empty_value_display = '=пусто='

    @admin.display(description='автор')
    def author_name(self, obj):
        return obj.author.username

    @admin.display(description='теги')
    def recipes_tag(self, obj):
        return obj.recipe.tags.all()

    @admin.display(description='ингридиенты')
    def recipes_ingredients(self, obj):
        return obj.recipe.ingredients.all()

    @admin.display(description='отметок в избраном')
    def favorite_count(self, obj):
        return obj.favorites.count()


@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ('author', 'subscriber')
    search_fields = ('author', 'subscriber')
    list_filter = ('author', 'subscriber')
    empty_value_display = '=пусто='


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'color', 'slug')
    list_filter = ('name', 'color', 'slug')
    empty_value_display = '=пусто='


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'password')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'password')
    list_filter = ('email', 'username', 'first_name', 'last_name', 'password')
    empty_value_display = '=пусто='
