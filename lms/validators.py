import re

from django.core.exceptions import ValidationError


def validate_youtube_url(value):
    """
    Валидатор, проверяющий, что ссылка ведет на YouTube.

    Проверяет наличие 'youtube.com', 'youtu.be' или 'youtube-nocookie.com' в URL.
    Регистронезависимая проверка.

    Args:
        value (str): Ссылка на видео, введенная пользователем.

    Raises:
        ValidationError: Если ссылка не содержит домен YouTube.
    """

    if not re.search(r"(youtube\.com|youtu\.be|youtube-nocookie\.com)", value, re.IGNORECASE):
        raise ValidationError("Ссылка должна вести на YouTube. Пожалуйста, используйте ссылку с youtube.com.")
