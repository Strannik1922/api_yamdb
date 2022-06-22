from django.db import models


class Categories(models.Model):
    name = models.CharField(
        max_length=250,
        verbose_name='Название категории'
    )
    slug = models.SlugField(
        unique=True,
        max_length=50,
        verbose_name='Уникальный адресс категории',
    )

    def __str__(self) -> str:
        return f'{self.name}'

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'категории'
        ordering = ['name']


class Genre(models.Model):
    name = models.CharField(
        max_length=250,
        verbose_name='Название жанра',
    )
    slug = models.SlugField(
        unique=True,
        max_length=50,
        verbose_name='Уникальный адресс жанра',
    )

    def __str__(self) -> str:
        return f'{self.name}'

    class meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name']


class Title(models.Model):
    name = models.CharField(
        max_length=250,
        verbose_name='Название произведения',
    )
    year = models.IntegerField(
        verbose_name='Год создания',
    )
    rating = models.IntegerField(
        null=True,
        default=None,
        verbose_name='Рейтинг',
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание произведения',
    )
    genre = models.ForeignKey(
        Genre,
        related_name='titles',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Жанр',

    )
    category = models.ForeignKey(
        Categories,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name='Категория',
    )

    def __str__(self) -> str:
        return f'{self.name}'

    class meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ['name']
