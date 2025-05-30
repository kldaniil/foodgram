from django.contrib import admin

from recipes.models import (
    Favorites, Ingredients, Recipes, Tags
)

admin.site.register(Favorites)
admin.site.register(Ingredients)
admin.site.register(Recipes)
admin.site.register(Tags)
