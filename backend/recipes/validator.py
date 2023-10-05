from django.core.exceptions import ValidationError


def validator_more_one(value):
    """Проверка на отрицательное значение или 0."""
    if value < 1:
        raise ValidationError('Значение не должно быть меньше или равно 0')
