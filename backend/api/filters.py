from django.contrib.auth import get_user_model
from django.db.models import Case, IntegerField, Q, Value, When
from django_filters.rest_framework import (CharFilter, FilterSet,
                                           ModelMultipleChoiceFilter)

from recipes.models import Ingredients, Recipes, Tags

User = get_user_model()


class RecipesFilter(FilterSet):
    """Фильтр для рецептов."""
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tags.objects.all(),
    )

    class Meta:
        model = Recipes
        fields = ('author', 'tags')


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
