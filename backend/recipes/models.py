from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from .validator import validator_more_one

UsernameValidator = UnicodeUsernameValidator()


class User(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        verbose_name='Имя пользователя',
        blank=False,
        unique=True,
        validators=(UsernameValidator,),
        max_length=150,
        null=False
    )
    email = models.EmailField(
        verbose_name='email address',
        blank=False,
        unique=True,
        max_length=254,
        null=False
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=False
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=False
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=150,
        blank=False,
        null=False
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
                                               name='author_subscriber')]

    def __str__(self):
        return f'Author({self.author}) - Subscriber({self.subscriber})'


class Tags(models.Model):
    """Модель тэга."""

    name = models.CharField(
        verbose_name='Имя',
        blank=False,
        unique=True,
        null=False,
        max_length=150
    )
    color = models.CharField(
        verbose_name='Цвет',
        blank=False,
        null=False,
        max_length=7,
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        blank=False,
        unique=True,
        null=False,
        max_length=150
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
        max_length=200
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=200
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

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
        max_length=200
    )
    tags = models.ManyToManyField(
        Tags,
        verbose_name='Тэг',
        related_name='recipes',
    )
    text = models.CharField(
        verbose_name='Текст рецепта',
        blank=False,
        max_length=1000
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        validators=[validator_more_one],
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
