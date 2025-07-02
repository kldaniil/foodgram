from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (ExtendedUsersViewSet, IngrediensViewSet, RecipesViewSet,
                    TagsViewSet, short_link_redirect)

router = DefaultRouter()
router.register('ingredients', IngrediensViewSet, basename='ingredients')
router.register('tags', TagsViewSet, basename='tags')
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('users', ExtendedUsersViewSet, basename='users')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
    path(
        's/<str:short_link>/',
        short_link_redirect,
        name='short_link_redirect'
    ),
]
