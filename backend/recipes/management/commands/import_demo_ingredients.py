import json

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredients


class Command(BaseCommand):
    """Импорт ингредиентов из файла"""
    help = 'Импорт ингредиентов из файла'

    def handle(self, *args, **options):
        """Импортирует ингредиенты из файла ingredients.json"""
        path = settings.BASE_DIR / 'data' / 'ingredients.json'
        with open(path, encoding='utf-8') as file:
            ingredients = json.load(file)

            ingredients_list = []
            for ingredient in ingredients:
                ingredients_list.append(
                    Ingredients(
                        name=ingredient['name'],
                        measurement_unit=ingredient['measurement_unit']
                    )
                )
            Ingredients.objects.bulk_create(
                ingredients_list,
                ignore_conflicts=True
            )

        self.stdout.write(self.style.SUCCESS('Ингредиенты импортированы'))
