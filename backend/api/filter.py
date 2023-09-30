from django_filters.rest_framework import FilterSet, filters
from recipes.models import Ingredient, Recipes, Tags


class FilterForRecipe(FilterSet):
    """Фильтер-класс для рецептов."""

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
        """Фильтр для избранного."""
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтр для корзины."""
        if value and self.request.user.is_authenticated:
            return queryset.filter(cart__user=self.request.user)
        return queryset


class ChangSearchForName(FilterSet):
    """Фильтр для смены search на name."""

    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ['name']
