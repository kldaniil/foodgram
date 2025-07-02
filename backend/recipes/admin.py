from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from .models import (Favorites, Ingredients, Recipes,
                     RecipesIngredients, ShoppingList, Tags)


class IngredientsAdminInLine(admin.TabularInline):
    """Inline для ингредиентов в рецепте."""
    model = RecipesIngredients
    fields = ('ingredient', 'amount')
    verbose_name = 'Ингредиент'
    verbose_name_plural = 'Ингредиенты'
    extra = 1
    autocomplete_fields = ('ingredient',)


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    """Админка для рецептов."""
    list_display = ('id', 'name', 'author', 'favorites_recipes_count')
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)
    list_display_links = ('id', 'name')
    filter_horizontal = ('tags',)
    readonly_fields = ('preview', 'favorites_recipes_count')
    inlines = (IngredientsAdminInLine,)
    fields = (
        'name', 'author', 'image', 'preview', 'text',
        'cooking_time', 'tags', 'favorites_recipes_count'
    )

    def get_queryset(self, request):
        """
        Переопределяем метод get_queryset для добавления счетчика
        избранных рецептов.
        """
        return Recipes.objects.annotate(
            favorites_recipes_count=Count('favorites_recipes')
        )

    @admin.display(description='Добавлено в избранное раз:')
    def favorites_recipes_count(self, obj):
        """Возвращает количество добавлений в избранное."""
        return obj.favorites_recipes_count

    @admin.display(description='Фото блюда')
    def preview(self, obj):
        """Показывает превью блюда."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px;" />', obj.image.url
            )
        return 'Нет изображения'


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    """Админка для ингредиентов."""
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_display_links = ('id', 'name')


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    """Админка для тегов."""
    list_display = ('id', 'name', 'slug')
    search_fields = ('name',)
    list_display_links = ('id', 'name', 'slug')


admin.site.register(Favorites)
admin.site.register(ShoppingList)
