from django.core.exceptions import ValidationError

from constants import MIN_COOKING_TIME, MAX_COOKING_TIME


def cooking_time_validator(value):
    """Валидатор времени приготовления."""
    try:
        if value <= MIN_COOKING_TIME or value >= MAX_COOKING_TIME:
            raise ValidationError('Неверно указано время!')
    except ValueError:
        raise ValidationError('Неверный формат')
