import random
import string

from .constants import MAX_LINK_LENGTH, SHORT_LINK_LENGTH


def generate_short_link(length=SHORT_LINK_LENGTH):
    """Генерирует короткую ссылку."""
    return (
        ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    )


def unique_link():
    """Возвращает уникальную короткую ссылку для рецепта."""
    from .models import Recipes

    for attempt in range(MAX_LINK_LENGTH - SHORT_LINK_LENGTH + 1):
        link_length = SHORT_LINK_LENGTH + attempt
        short_link = generate_short_link(link_length)
        if (
            not Recipes.objects.filter(short_link=short_link).exists()
        ):
            return short_link
    raise ValueError('Не удалось сгенерировать уникальную ссылку')
