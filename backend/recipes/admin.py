from django.contrib import admin

from recipes.models import (
    Ingredients, Recipes, Tags
)


class RecipesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'favorites_recipes_count')
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)

    @admin.display(description='Добавлено в избранное раз:')
    def favorites_recipes_count(self, obj):
        return obj.favorites_recipes.count()


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)


class TagsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name',)


admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(Recipes, RecipesAdmin)
admin.site.register(Tags, TagsAdmin)
