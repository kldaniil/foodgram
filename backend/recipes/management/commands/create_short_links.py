from django.core.management.base import BaseCommand
from django.db.models import Q

from recipes.models import Recipes
from recipes.utils import unique_link


class Command(BaseCommand):
    """Проходит по рецептам и генерирует short_links, если они пустые."""
    help = 'Создает короткие ссылки для рецептов без них.'

    def handle(self, *args, **options):
        recipes = Recipes.objects.filter(
            Q(short_link__isnull=True)
            | Q(short_link='')
        )
        for recipe in recipes:
            recipe.short_link = unique_link()
            recipe.save(update_fields=['short_link'])
        self.stdout.write(
            self.style.SUCCESS('Отсутствующие короткие cсылки добавлены.')
        )
