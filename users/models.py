"""Модели приложения users."""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя проекта."""

    email = models.EmailField(
        unique=True,
        verbose_name="Адрес электронной почты",
    )
    avatar = models.ImageField(
        upload_to="users/avatars/",
        default="users/avatars/default.jpg",
        blank=True,
        verbose_name="Аватар",
        help_text="Изображение профиля пользователя",
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = (
        "username",
        "first_name",
        "last_name",
    )

    class Meta:
        ordering = ("username",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self) -> str:
        return self.username
