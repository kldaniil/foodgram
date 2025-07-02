from django.contrib.auth import get_user_model
from django.db.models import Case, IntegerField, Q, Value, When
from django_filters.rest_framework import (AllValuesMultipleFilter,
                                           BooleanFilter, CharFilter,
                                           FilterSet)
from recipes.models import Ingredients, Recipes

User = get_user_model()


class RecipesFilter(FilterSet):
    """Фильтр для рецептов."""
    is_favorited = BooleanFilter(method='filter_is_favorited')
    tags = AllValuesMultipleFilter(field_name='tags__slug')
    author = CharFilter(field_name='author__id')
    is_in_shopping_cart = BooleanFilter(method='filter_is_in_shopping_cart')

    def filter_favorites_or_shopping(
        self, queryset, name, value, filter_field
    ):
        """Обработка фильтра по избранным или списку покупок."""
        user = self.request.user
        if not user.is_authenticated and value:
            return queryset.none()
        if value:
            filter_dict = {filter_field: user}
            return queryset.filter(**filter_dict)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрует рецепты по избранным."""
        return (
            self.filter_favorites_or_shopping(
                queryset, name, value,
                'favorites_recipes__user'
            )
        )

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрует рецепты по списку покупок."""
        return (
            self.filter_favorites_or_shopping(
                queryset, name, value,
                'recipes_user_shopping_list__user'
            )
        )

    class Meta:
        model = Recipes
        fields = ('tags', 'is_favorited')


class IngredientsFilter(FilterSet):
    """Фильтр для ингредиентов."""
    name = CharFilter(method='filter_name')

    def filter_name(self, queryset, name, value):
        if value:
            return (
                queryset
                .filter(name__icontains=value)
                .annotate(
                    priority=Case(
                        When(name__istartswith=value, then=Value(0)),
                        When(
                            Q(name__icontains=value)
                            & ~Q(name__istartswith=value),
                            then=Value(1)
                        ),
                        default=Value(2),
                        output_field=IntegerField(),
                    )
                )
                .order_by('priority', 'name')
            )
        return queryset

    class Meta:
        model = Ingredients
        fields = ('name',)
