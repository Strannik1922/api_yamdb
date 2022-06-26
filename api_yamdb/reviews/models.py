from django.contrib.auth.models import AbstractUser
from django.db import models


USER = 'user'
ADMIN = 'admin'
MODERATOR = 'moderator'

ROLES = (
    (USER, 'user'),
    (ADMIN, 'admin'),
    (MODERATOR, 'moderator'),
)


class User(AbstractUser):
    """Модель пользователей."""

    first_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(
        max_length=30,
        choices=ROLES,
        default='user'
    )
    bio = models.TextField(
        blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_username_email'
            )
        ]


class Category(models.Model):
    """Модель категорий."""
    name = models.CharField(max_length=30)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.slug


class Genre(models.Model):
    """Модель жанров."""
    name = models.CharField(max_length=30)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.slug


class Title(models.Model):
    """Модель произведений."""
    name = models.CharField(max_length=50)
    year = models.IntegerField()
    description = models.TextField(
        max_length=200,
        null=True,
        blank=True,
    )
    genre = models.ManyToManyField(Genre)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель отзывов."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.PositiveSmallIntegerField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Модель комментариев."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    def __str__(self):
        return self.text
