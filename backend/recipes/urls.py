from django.urls import path

from .views import short_link_redirect

urlpatterns = [
    path(
        '<str:short_link>/',
        short_link_redirect,
        name='short_link_redirect'
    ),
]
