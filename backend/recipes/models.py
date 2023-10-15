from colorfield.fields import ColorField
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models import F, Q

from api.validator import cooking_time_validator
from constants import MAX_LENGHT_COLOR, MAX_LENGHT_NAME, MAX_LENGHT_TEXT
from .validator import validator_more_one

UsernameValidator = UnicodeUsernameValidator()


class User(AbstractUser):
    """Модель пользователя."""

    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    USERNAME_FIELD = 'email'

    username = models.CharField(
        verbose_name='username',
        max_length=MAX_LENGHT_NAME,
        unique=True,
        validators=(UsernameValidator, )
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=MAX_LENGHT_NAME,
    )
    last_name = models.CharField(
        verbose_name='Фамиоия',
        max_length=MAX_LENGHT_NAME,
    )
    email = models.EmailField(
        verbose_name='email',
        unique=True,
        max_length=MAX_LENGHT_NAME,
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=MAX_LENGHT_NAME,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return f'{self.username}'


class Subscriptions(models.Model):
    """Подписка."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
        related_name='following'
    )
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='follower',

    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [models.UniqueConstraint(fields=['author', 'subscriber'],
                                               name='author_subscriber'),
                       models.CheckConstraint(check=~Q(subscriber=F('author')),
                                              name='no_self_subscription')]

    def __str__(self):
        return f'Author({self.author}) - Subscriber({self.subscriber})'


class Tags(models.Model):
    """Модель тэга."""

    name = models.CharField(
        verbose_name='Имя',
        blank=False,
        unique=True,
        null=False,
        max_length=MAX_LENGHT_NAME
    )
    color = ColorField(
        verbose_name='Цвет',
        blank=False,
        null=False,
        db_index=True,
        unique=True,
        format='hex',
        default='#999999',
        max_length=MAX_LENGHT_COLOR,
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        blank=False,
        unique=True,
        null=False,
        max_length=MAX_LENGHT_NAME
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    """Ингредиенты."""

    name = models.CharField(
        verbose_name='Название ингридиента',
        max_length=MAX_LENGHT_NAME
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=MAX_LENGHT_NAME
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [models.UniqueConstraint(fields=['name',
                                                       'measurement_unit'],
                                               name='name_measurement_unit')]

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Recipes(models.Model):
    """Рецепт."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes',
    )
    image = models.ImageField(
        verbose_name='Картинка Блюда',
        upload_to='recipes/',
        blank=False,
    )
    name = models.CharField(
        verbose_name='Название блюда',
        blank=False,
        null=False,
        max_length=MAX_LENGHT_NAME
    )
    tags = models.ManyToManyField(
        Tags,
        verbose_name='Тэг',
        related_name='recipes',
    )
    text = models.CharField(
        verbose_name='Текст рецепта',
        blank=False,
        max_length=MAX_LENGHT_TEXT
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        validators=(cooking_time_validator, )
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        related_name='recipes',
        through='IngredientsOfRecipe',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}'


class IngredientsOfRecipe(models.Model):
    """Ингредиенты в рецепте."""

    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='ingredients_in_recipe',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients_in_recipe',
    )
    amount = models.IntegerField(
        verbose_name='Количество ингредиентов',
        default=1,
        validators=[validator_more_one]
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        constraints = [models.UniqueConstraint(fields=['recipe', 'ingredient'],
                                               name='ingredient_recipe')]

    def __str__(self):
        return f'{self.ingredient.name} {self.amount}'


class Favorite(models.Model):
    """Избранные рецепты."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Избранный пользователь',
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Рецепты избранного пользователя',
        related_name='favorites'
    )

    class Meta:
        verbose_name = 'Любимый рецепт'
        verbose_name_plural = 'Любимые рецепты'
        constraints = [models.UniqueConstraint(fields=['user', 'recipe'],
                                               name='favorite_recipe')]

    def __str__(self):
        return f'{self.user}-{self.recipe}'


class Cart(models.Model):
    """Корзина покупателя."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Владелец корзины',
        related_name='cart'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Рецепты в корзине',
        related_name='cart'
    )

    class Meta:
        verbose_name = 'Покупка в корзине'
        verbose_name_plural = 'Покупки в корзине'
        constraints = [models.UniqueConstraint(fields=['user', 'recipe'],
                                               name='cart_recipe')]

    def __str__(self):
        return f'{self.user}-{self.recipe}'
