from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipes, Tags, User


class FilterForRecipe(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(queryset=Tags.objects.all(),
                                             field_name='tags__slug',
                                             to_field_name='slug')

    class Meta:
        model = Recipes
        fields = ('author', 'tags')

    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorite_recipes__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset


class ChangSearchForName(FilterSet):
    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ['name']
