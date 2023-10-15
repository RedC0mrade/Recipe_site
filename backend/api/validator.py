from django.core.exceptions import ValidationError


def cooking_time_validator(value):
    """Валидатор времени приготовления."""
    try:
        if (int(value) <= 0) or (int(value) >= 1000):
            raise ValidationError('Неверно указано время!')
    except ValueError:
        raise ValidationError('Неверный формат')
