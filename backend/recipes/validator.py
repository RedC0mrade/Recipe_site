from django.core.exceptions import ValidationError


def validator_more_one(value):
    if value < 1:
        raise ValidationError('Значение не должно быть меньше 0')
