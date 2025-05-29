import json
from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredients


class Command(BaseCommand):
    help = 'Импорт ингредиентов из файла'
    def handle(self, *args, **options):
        path = settings.BASE_DIR.parent / 'data' / 'ingredients.json'
        with open(path, encoding='utf-8') as file:
            ingredients = json.load(file)
            for ingredient in ingredients:
                Ingredients.objects.get_or_create(
                    name=ingredient['name'],
                    measurement_unit=['measurement_unit']
                )
        self.stdout.write(self.style.SUCCESS('Ингредиенты импортированы'))
