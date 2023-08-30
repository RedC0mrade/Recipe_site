from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

UsernameValidator = UnicodeUsernameValidator()


class User(AbstractUser):

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


class Tags(models.Model):
    name = models.CharField(
        verbose_name='Тэги',
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


class Recipes(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    image = models.ImageField(
        upload_to='recipes/',
        blank=False,
        verbose_name='Картинка Блюда'
    )
    name = models.CharField(
        verbose_name='Название блюда',
        blank=False,
        null=False,
        max_length=200
    )
    tag = models.ManyToManyField(
        Tags,
        related_name='recipes',
        verbose_name='Тэг')
    text = models.CharField(
        verbose_name='Текст рецепта',
    )
    cooking_time = models.IntegerField()