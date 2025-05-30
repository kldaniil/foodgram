from django.contrib.auth import get_user_model
from django_filters.rest_framework import (
    AllValuesMultipleFilter, BooleanFilter, FilterSet
)
from recipes.models import Recipes


class RecipesFilter(FilterSet):
    is_favorited = BooleanFilter(method='filter_is_favorited')
    tags = AllValuesMultipleFilter(field_name='tags__slug')

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated and value:
            return queryset.none()
        if value:
            return queryset.filter(favorites_recipes__user=user)
        return queryset

    class Meta:
        model = Recipes
        fields = ('tags', 'is_favorited')
