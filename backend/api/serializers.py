from rest_framework import serializers

from ..recipes.models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password')
