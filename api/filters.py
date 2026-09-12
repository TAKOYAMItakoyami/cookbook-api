"""Фильтры для API рецептов и ингредиентов."""

from django.db.models import QuerySet
from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe

from .constants import FILTER_TRUE


class IngredientFilter(filters.FilterSet):
    """Фильтр ингредиентов по началу названия."""

    name = filters.CharFilter(field_name="name", lookup_expr="istartswith")

    class Meta:
        model = Ingredient
        fields = ("name",)


class RecipeFilter(filters.FilterSet):
    """Фильтр рецептов по автору, тегам и пользовательским признакам."""

    is_favorited = filters.NumberFilter(method="filter_favorited")
    is_in_shopping_cart = filters.NumberFilter(method="filter_shopping_cart")
    author = filters.NumberFilter(field_name="author")
    tags = filters.CharFilter(method="filter_tags")

    class Meta:
        model = Recipe
        fields = (
            "is_favorited",
            "is_in_shopping_cart",
            "author",
            "tags",
        )

    def filter_favorited(
        self, queryset: QuerySet[Recipe], name: str, value: int
    ) -> QuerySet[Recipe]:
        """Возвращает рецепты, добавленные пользователем в избранное."""

        if value == FILTER_TRUE and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_shopping_cart(
        self, queryset: QuerySet[Recipe], name: str, value: int
    ) -> QuerySet[Recipe]:
        """Возвращает рецепты, находящиеся в списке покупок пользователя."""

        if value == FILTER_TRUE and self.request.user.is_authenticated:
            return queryset.filter(shopping_carts__user=self.request.user)
        return queryset

    def filter_tags(
        self, queryset: QuerySet[Recipe], name: str, value: str
    ) -> QuerySet[Recipe]:
        """Фильтрует рецепты по одному или нескольким тегам."""

        tags: list[str] = self.request.query_params.getlist("tags")
        return queryset.filter(tags__slug__in=tags).distinct()
