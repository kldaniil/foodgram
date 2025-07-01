from django.contrib import admin
from django.utils.html import format_html
from recipes.models import Ingredients, Recipes, Tags

from .models import Ingredients, Recipes, RecipesIngredients


class IngredientsAdminInLine(admin.TabularInline):
    '''Inline для ингредиентов в рецепте.'''
    model = RecipesIngredients
    fields = ('ingredient', 'amount')
    verbose_name = 'Ингредиент'
    verbose_name_plural = 'Ингредиенты'
    extra = 1
    autocomplete_fields = ('ingredient',)


class RecipesAdmin(admin.ModelAdmin):
    '''Админка для рецептов.'''
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

    @admin.display(description='Добавлено в избранное раз:')
    def favorites_recipes_count(self, obj):
        '''Считает количество добавлений в избранное.'''
        return obj.favorites_recipes.count()

    @admin.display(description='Фото блюда')
    def preview(self, obj):
        '''Показывает превью блюда.'''
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px;" />', obj.image.url
            )
        return 'Нет изображения'


class IngredientsAdmin(admin.ModelAdmin):
    '''Админка для ингредиентов.'''
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_display_links = ('id', 'name')


class TagsAdmin(admin.ModelAdmin):
    '''Админка для тегов.'''
    list_display = ('id', 'name', 'slug')
    search_fields = ('name',)
    list_display_links = ('id', 'name', 'slug')


admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(Recipes, RecipesAdmin)
admin.site.register(Tags, TagsAdmin)
