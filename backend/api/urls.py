from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AvatarViewSet, IngrediensViewSet,
    RecipesViewSet, SubscriptionsViewSet, TagsViewSet, 
)

v1_router = DefaultRouter()
v1_router.register(r'ingredients', IngrediensViewSet, basename='ingredients')
v1_router.register(r'tags', TagsViewSet, basename='tags')
v1_router.register(
    r'users/subscriptions', SubscriptionsViewSet, basename='subscriptions'
)
v1_router.register(r'recipes', RecipesViewSet, basename='recipes')

urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path(
        'users/me/avatar/',
        view=AvatarViewSet.as_view({'put': 'update', 'delete': 'destroy'}),
        name='Аватар'
    ),
    path('', include(v1_router.urls)),
]
