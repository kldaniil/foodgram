from recipes.models import Ingredients
from rest_framework import serializers


def ingredients_validator(value):
    """Валидатор для ингредиентов. Проверяет, что ингредиенты не пустые,
    не повторяются и существуют в базе данных."""
    if not value:
        raise serializers.ValidationError(
            'Поле ingredients не может быть пустым'
        )
    ingredients = set()
    for item in value:
        if not item.get('id') in ingredients:
            ingredients.add(item.get('id'))
        else:
            raise serializers.ValidationError(
                'Ингредиенты повторяются'
            )
        if not Ingredients.objects.filter(id=item.get('id')).exists():
            raise serializers.ValidationError('Ингредиент не существует.')

    return value


def tags_validator(value):
    """Валидатор для тегов. Проверяет, что теги не пустые и не повторяются."""
    if not value:
        raise serializers.ValidationError(
            'Поле tags не может быть пустым'
        )
    tags = set()
    for item in value:
        if item not in tags:
            tags.add(item)
        else:
            raise serializers.ValidationError(
                'Теги повторяются'
            )

    return value

# TODO как-то объединить валидатор тегов и ингредиентов, так не красиво.
