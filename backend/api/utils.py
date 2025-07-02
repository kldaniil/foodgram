import random
import string

from recipes.constants import MAX_LINK_LENGTH
from recipes.models import Recipes

from .constants import SHORT_LINK_LENGTH


def generate_short_link(length=SHORT_LINK_LENGTH):
    """Генерирует короткую ссылку."""
    return (
        ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    )


def unique_link():
    """Возвращает уникальную короткую ссылку для рецепта."""
    for attempt in range(MAX_LINK_LENGTH - SHORT_LINK_LENGTH + 1):
        link_length = SHORT_LINK_LENGTH + attempt
        short_link = generate_short_link(link_length)
        if (
            not Recipes.objects.filter(short_link=short_link).exists()
        ):
            return short_link
    raise ValueError('Не удалось сгенерировать уникальную ссылку')
