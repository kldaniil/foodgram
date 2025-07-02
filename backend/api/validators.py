from rest_framework import serializers


def ingredients_validator(value):
    """Валидатор для ингредиентов. Проверяет, что ингредиенты не пустые,
    не повторяются и существуют в базе данных."""
    if not value:
        raise serializers.ValidationError(
            'Поле ingredients не может быть пустым'
        )
    print("ingredients_validator got:", value)
    print('Ключи первого элемента ingredients:', value[0].keys())
    ingredients = set()
    for item in value:
        obj = item['ingredient']
        if obj.id not in ingredients:
            ingredients.add(obj.id)
        else:
            raise serializers.ValidationError(
                'Ингредиенты повторяются'
            )

    return value


def tags_validator(value):
    """Валидатор для тегов. Проверяет, что теги не пустые и не повторяются."""
    if not value:
        raise serializers.ValidationError(
            'Поле tags не может быть пустым'
        )
    if len(value) != len(set(value)):
        raise serializers.ValidationError(
            'Теги повторяются'
        )
    return value
