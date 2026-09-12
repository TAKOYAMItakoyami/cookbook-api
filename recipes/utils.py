"""Вспомогательные функции приложения recipes."""

import random
import string


def generate_short_code(length: int = 6) -> str:
    """Возвращает случайный короткий код для ссылки на рецепт."""

    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))
