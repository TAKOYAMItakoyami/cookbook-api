"""Конфигурация приложения recipes."""

from django.apps import AppConfig


class RecipesConfig(AppConfig):
    """Определяет конфигурацию приложения рецептов."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "recipes"
    verbose_name = "Рецепты"
