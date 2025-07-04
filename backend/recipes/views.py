from django.http import Http404
from django.shortcuts import redirect

from .models import Recipes


def short_link_redirect(request, short_link):
    """Перенаправляет по короткой ссылке."""
    try:
        recipe = Recipes.objects.get(short_link=short_link)
    except Recipes.DoesNotExist:
        raise Http404('Короткая ссылка не существует.')

    return redirect(f'/recipes/{recipe.id}/')
