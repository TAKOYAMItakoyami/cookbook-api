"""Сериализаторы API приложения."""

from typing import Any

from django.db.models import QuerySet
from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
)
from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.utils.serializer_helpers import ReturnDict

from recipes.constants import (
    MAX_AMOUNT,
    MAX_COOKING_TIME,
    MIN_AMOUNT,
    MIN_COOKING_TIME,
)
from recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag,
)
from users.models import User

from .constants import (
    NAME_MAX_LENGTH,
)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = ("id", "name", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class UserSerializer(DjoserUserSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "avatar",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj: User) -> bool:
        """
        Возвращает статус подписки текущего пользователя на другого.

        Использует аннотированное поле is_subscribed, если оно
        доступно, иначе выполняет проверку через запрос к БД.
        """

        if hasattr(obj, "is_subscribed"):
            return obj.is_subscribed
        request: Request | None = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return request.user.subscriptions.filter(author=obj).exists()


class AvatarSerializer(serializers.Serializer):
    """Сериализатор загрузки аватара пользователя."""

    avatar = Base64ImageField()

    def update(self, instance: User, validated_data: dict[str, Any]) -> User:
        instance.avatar = validated_data["avatar"]
        instance.save()
        return instance

    def create(self, validated_data: dict[str, Any]) -> dict[str, Any]:
        """Возвращает валидированные переданные данные без создания объекта."""
        return validated_data


class CustomUserCreateSerializer(DjoserUserCreateSerializer):
    """Сериализатор регистрации пользователя."""

    first_name = serializers.CharField(
        required=True, max_length=NAME_MAX_LENGTH
    )
    last_name = serializers.CharField(
        required=True, max_length=NAME_MAX_LENGTH
    )

    class Meta(DjoserUserCreateSerializer.Meta):
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
        )
        read_only_fields = ("id",)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента рецепта с количеством."""

    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор чтения рецептов."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, read_only=True, source="ingredient_amounts"
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj: Recipe) -> bool:
        """
        Возвращает признак нахождения рецепта в избранном.

        Использует аннотированное поле is_favorited, если оно доступно,
        иначе выполняет проверку через запрос к БД.
        """

        if hasattr(obj, "is_favorited"):
            return obj.is_favorited
        request: Request | None = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj: Recipe) -> bool:
        """
        Возвращает признак нахождения рецепта в списке покупок.

        Использует аннотированное поле is_in_shopping_cart, если оно
        доступно, иначе выполняет проверку через запрос к БД.
        """

        if hasattr(obj, "is_in_shopping_cart"):
            return obj.is_in_shopping_cart
        request: Request | None = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user.shopping_carts.filter(recipe=obj).exists()


class IngredientWriteSerializer(serializers.Serializer):
    """Сериализатор ингредиента при создании и изменении рецепта."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        min_value=MIN_AMOUNT, max_value=MAX_AMOUNT
    )


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор создания и изменения рецепта."""

    ingredients = IngredientWriteSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        min_value=MIN_COOKING_TIME, max_value=MAX_COOKING_TIME
    )

    class Meta:
        model = Recipe
        fields = (
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
        )

    def _create_ingredients(
        self, recipe: Recipe, ingredients: list[dict[str, Any]]
    ) -> None:
        """
        Создает связи рецепта с ингредиентами.

        Использует bulk_create() для уменьшения количества запросов к БД.
        """

        recipe_ingredients: list[RecipeIngredient] = []
        for ingredient_data in ingredients:
            recipe_ingredients.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient_data["id"],
                    amount=ingredient_data["amount"],
                )
            )
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data: dict[str, Any]) -> Recipe:
        """Создает рецепт вместе с тегами и ингредиентами."""

        ingredients: list[dict[str, Any]] = validated_data.pop("ingredients")
        tags: list[Tag] = validated_data.pop("tags")
        recipe: Recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self._create_ingredients(recipe, ingredients)
        return recipe

    def update(
        self, instance: Recipe, validated_data: dict[str, Any]
    ) -> Recipe:
        """Обновляет рецепт, его теги и список ингредиентов."""

        ingredients: list[dict[str, Any]] | None = validated_data.pop(
            "ingredients", None
        )
        tags: list[Tag] | None = validated_data.pop("tags", None)
        if tags is not None:
            instance.tags.set(tags)
        if ingredients is not None:
            instance.ingredient_amounts.all().delete()
            self._create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance: Recipe) -> ReturnDict:
        """Возвращает рецепт в формате сериализатора чтения."""

        return RecipeSerializer(instance, context=self.context).data

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Проверяет корректность данных рецепта.

        Контролирует наличие изображения, ингредиентов и тегов,
        а также отсутствие их повторений.
        """

        image: Any | None = data.get("image")
        ingredients: list[dict[str, Any]] | None = data.get("ingredients")
        tags: list[Tag] | None = data.get("tags")
        if ("image" in data and not image) or (
            not self.instance and not image
        ):
            raise serializers.ValidationError(
                {"image": "Изображение обязательно."}
            )
        if not ingredients:
            raise serializers.ValidationError(
                {"ingredients": "Необходимо добавить хотя бы один ингредиент."}
            )
        if not tags:
            raise serializers.ValidationError(
                {"tags": "Необходимо выбрать хотя бы один тег."}
            )
        ingredient_ids: list[int] = [item["id"].id for item in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                {"ingredients": "Ингредиенты не должны повторяться."}
            )
        tag_ids: list[int] = [tag.id for tag in tags]
        if len(tag_ids) != len(set(tag_ids)):
            raise serializers.ValidationError(
                {"tags": "Теги не должны повторяться."}
            )
        return data


class RecipeShortSerializer(serializers.ModelSerializer):
    """Краткий сериализатор рецепта."""

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписки на автора."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
            "avatar",
        )

    def get_is_subscribed(self, obj: User) -> bool:
        """
        Возвращает признак подписки текущего пользователя.

        Использует аннотированное поле is_subscribed, если оно
        присутствует в объекте, иначе выполняет запрос к БД.
        """

        if hasattr(obj, "is_subscribed"):
            return obj.is_subscribed
        request: Request | None = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return request.user.subscriptions.filter(author=obj).exists()

    def get_recipes(self, obj: User) -> list[dict[str, Any]]:
        """
        Возвращает список рецептов автора.

        Поддерживает ограничение количества рецептов через параметр
        recipes_limit.
        """

        request: Request | None = self.context.get("request")
        recipes: QuerySet[Recipe] | list[Recipe] = obj.recipes.all()
        if request:
            limit_value: str | None = request.query_params.get("recipes_limit")
            if limit_value:
                try:
                    limit = int(limit_value)
                    recipes = recipes[:limit]
                except ValueError:
                    pass
        return RecipeShortSerializer(
            recipes, many=True, context=self.context
        ).data

    def get_recipes_count(self, obj: User) -> int:
        """
        Возвращает количество рецептов автора.

        Использует аннотированное поле recipes_count при наличии.
        """

        return getattr(obj, "recipes_count", obj.recipes.count())
