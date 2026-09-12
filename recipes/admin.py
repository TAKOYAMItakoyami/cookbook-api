"""Настройка административной панели приложения recipes."""

from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    ShortLink,
    Subscription,
    Tag,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настраивает отображение тегов в панели администратора."""

    list_display = (
        "id",
        "name",
        "slug",
    )
    search_fields = ("name",)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настраивает отображение ингредиентов в панели администратора."""

    list_display = (
        "id",
        "name",
        "measurement_unit",
    )
    search_fields = ("name",)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настраивает отображение рецептов в панели администратора."""

    list_display = (
        "id",
        "author",
        "name",
        "cooking_time",
        "pub_date",
        "favorites_count",
    )
    search_fields = (
        "name",
        "author__username",
    )
    list_filter = ("tags",)
    list_select_related = ("author",)

    @admin.display(description="В избранном")
    def favorites_count(self, obj) -> int:
        """
        Возвращает количество пользователей,
        добавивших рецепт в избранное.
        """

        return obj.favorites.count()


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Настраивает отображение связей рецептов с ингредиентами."""

    list_display = (
        "id",
        "recipe",
        "ingredient",
        "amount",
    )
    search_fields = (
        "recipe__name",
        "ingredient__name",
    )
    list_select_related = (
        "recipe",
        "ingredient",
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Настраивает отображение избранных рецептов."""

    list_display = (
        "id",
        "user",
        "recipe",
    )
    search_fields = (
        "user__username",
        "user__email",
        "recipe__name",
    )
    list_select_related = (
        "user",
        "recipe",
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Настраивает отображение списка покупок."""

    list_display = (
        "id",
        "user",
        "recipe",
    )
    search_fields = (
        "user__username",
        "user__email",
        "recipe__name",
    )
    list_select_related = (
        "user",
        "recipe",
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Настраивает отображение подписок пользователей."""

    list_display = (
        "id",
        "subscriber",
        "author",
    )
    search_fields = (
        "subscriber__username",
        "subscriber__email",
        "author__username",
        "author__email",
    )
    list_select_related = (
        "subscriber",
        "author",
    )


@admin.register(ShortLink)
class ShortLinkAdmin(admin.ModelAdmin):
    """Настраивает отображение коротких ссылок."""

    list_display = (
        "id",
        "code",
        "recipe",
    )
    search_fields = (
        "code",
        "recipe__name",
    )
    list_select_related = ("recipe",)
