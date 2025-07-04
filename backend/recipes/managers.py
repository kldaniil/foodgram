from django.db import models
from django.db.models import BooleanField, Exists, OuterRef, Value


class RecipesQuerySet(models.QuerySet):
    """Кварисет для рецептов с аннотацией корзины и избранного."""
    def cart_and_favorites(self, user):
        from .models import Favorites, ShoppingList

        if user.is_authenticated:
            is_favorited = Favorites.objects.filter(
                user=user, recipe=OuterRef('pk')
            )
            is_in_shopping_cart = ShoppingList.objects.filter(
                user=user, recipe=OuterRef('pk')
            )
            return self.annotate(
                is_favorited=Exists(is_favorited),
                is_in_shopping_cart=Exists(is_in_shopping_cart)
            )
        return self.annotate(
            is_favorited=Value(False, output_field=BooleanField()),
            is_in_shopping_cart=Value(False, output_field=BooleanField())
        )
