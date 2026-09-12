"""Модели приложения recipes."""

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .constants import (
    INGREDIENT_NAME_MAX_LENGTH,
    MAX_AMOUNT,
    MAX_COOKING_TIME,
    MEASUREMENT_UNIT_MAX_LENGTH,
    MIN_AMOUNT,
    MIN_COOKING_TIME,
    RECIPE_NAME_MAX_LENGTH,
    SLUG_MAX_LENGTH,
    TAG_NAME_MAX_LENGTH,
)
from .utils import generate_short_code

User = get_user_model()


class Tag(models.Model):
    """Модель тега рецепта."""

    name = models.CharField(
        max_length=TAG_NAME_MAX_LENGTH,
        unique=True,
        verbose_name="Название тега",
    )
    slug = models.SlugField(
        max_length=SLUG_MAX_LENGTH,
        unique=True,
        verbose_name="Слаг тега",
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        max_length=INGREDIENT_NAME_MAX_LENGTH,
        verbose_name="Название ингредиента",
    )
    measurement_unit = models.CharField(
        max_length=MEASUREMENT_UNIT_MAX_LENGTH,
        verbose_name="Единица измерения ингредиента",
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

        constraints = [
            models.UniqueConstraint(
                fields=("name", "measurement_unit"), name="unique_ingredient"
            )
        ]

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )
    name = models.CharField(
        max_length=RECIPE_NAME_MAX_LENGTH,
        verbose_name="Название рецепта",
    )
    image = models.ImageField(
        upload_to="recipes/images/",
        verbose_name="Фотография",
        help_text="Изображение готового блюда",
    )
    text = models.TextField(verbose_name="Описание рецепта")
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(MIN_COOKING_TIME),
            MaxValueValidator(MAX_COOKING_TIME),
        ],
        verbose_name="Время приготовления",
    )
    tags = models.ManyToManyField(
        Tag, related_name="recipes", verbose_name="Теги"
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        related_name="recipes",
        verbose_name="Ингредиенты",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Дата публикации",
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-pub_date",)

    def __str__(self) -> str:
        return self.name


class RecipeIngredient(models.Model):
    """Связывает рецепт с ингредиентом и хранит его количество."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredient_amounts",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="recipe_links",
        verbose_name="Ингредиент",
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(MIN_AMOUNT),
            MaxValueValidator(MAX_AMOUNT),
        ],
        verbose_name="Количество",
    )

    class Meta:
        verbose_name = "Ингредиент рецепта"
        verbose_name_plural = "Ингредиенты рецептов"
        ordering = ("recipe",)
        constraints = [
            models.UniqueConstraint(
                fields=("recipe", "ingredient"),
                name="unique_ingredient_in_recipe",
            )
        ]

    def __str__(self) -> str:
        return f"{self.recipe} — {self.ingredient} ({self.amount})"


class Favorite(models.Model):
    """Хранит рецепты, добавленные пользователем в избранное."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        ordering = ("user", "recipe")
        constraints = [
            models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_recipe_in_favorites"
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} -> {self.recipe}"


class ShoppingCart(models.Model):
    """Хранит рецепты, добавленные пользователем в список покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_carts",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_carts",
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
        ordering = ("user", "recipe")
        constraints = [
            models.UniqueConstraint(
                fields=("user", "recipe"),
                name="unique_recipe_in_shopping_cart",
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} -> {self.recipe}"


class Subscription(models.Model):
    """Модель подписки пользователя на автора рецептов."""

    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscribers",
        verbose_name="Автор",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=("subscriber", "author"),
                name="unique_user_subscription",
            ),
            models.CheckConstraint(
                check=~models.Q(subscriber=models.F("author")),
                name="prevent_self_subscription",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.subscriber} -> {self.author}"


class ShortLink(models.Model):
    """Модель короткой ссылки на рецепт."""

    recipe = models.OneToOneField(
        Recipe, on_delete=models.CASCADE, related_name="short_link"
    )
    code = models.CharField(
        max_length=10, unique=True, default=generate_short_code
    )

    class Meta:
        verbose_name = "Короткая ссылка"
        verbose_name_plural = "Короткие ссылки"

    def __str__(self) -> str:
        return self.code
