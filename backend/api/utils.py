import random
import string

from .constants import SHORT_LINK_LENGTH


def generate_short_link(length=SHORT_LINK_LENGTH):
    return (
        ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    )
def foo(): return  1