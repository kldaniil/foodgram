from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AvatarViewSet
)

urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path(
        'users/me/avatar/',
        view=AvatarViewSet.as_view({'put': 'update', 'delete': 'destroy'}),
        name='Аватар'
    ),
]
