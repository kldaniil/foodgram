from rest_framework import serializers

from recipes.models import Ingredients


def ingredients_validator(value):
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
    if not value:
        raise serializers.ValidationError(
            'Поле tags не может быть пустым'
        )
    tags = set()
    for item in value:
        if not item in tags:
            tags.add(item)
        else:
            raise serializers.ValidationError(
                'Теги повторяются'
            )

    return value

# TODO как-то объединить валидатор тегов и ингредиентов, так не красиво.
