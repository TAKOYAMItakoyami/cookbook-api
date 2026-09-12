"""Представления API приложения."""

from django.db.models import Count, Exists, OuterRef, QuerySet, Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    BasePermission,
    IsAuthenticated,
)
from rest_framework.request import Request
from rest_framework.response import Response

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    ShortLink,
    Subscription,
    Tag,
)
from users.models import User

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (
    AvatarSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeShortSerializer,
    RecipeWriteSerializer,
    SubscriptionSerializer,
    TagSerializer,
)


def short_link_redirect(request: Request, code: str) -> HttpResponseRedirect:
    """Перенаправляет на API-эндпоинт рецепта по короткой ссылке.

    Пользователь, перейдя по короткой ссылке вида /s/<code>/,
    получает JSON-представление рецепта через /api/recipes/<id>/.
    """
    short_link: ShortLink = get_object_or_404(ShortLink, code=code)
    return redirect(f"/api/recipes/{short_link.recipe.id}/")


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Предоставляет доступ к просмотру
    списка ингредиентов и отдельных ингредиентов.
    """

    queryset: QuerySet[Ingredient] = Ingredient.objects.all()
    serializer_class: type[IngredientSerializer] = IngredientSerializer
    filterset_class: type[IngredientFilter] = IngredientFilter
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Предоставляет доступ к просмотру списка тегов и отдельных тегов."""

    queryset: QuerySet[Tag] = Tag.objects.all()
    serializer_class: type[TagSerializer] = TagSerializer
    pagination_class = None


class UserViewSet(DjoserUserViewSet):
    """Обрабатывает операции с пользователями и подписками."""

    queryset: QuerySet[User] = User.objects.all()
    permission_classes: tuple[type[BasePermission], ...] = (AllowAny,)

    def get_queryset(self) -> QuerySet[User]:
        """Возвращает queryset пользователей с необходимыми аннотациями."""

        queryset: QuerySet[User] = User.objects.prefetch_related(
            "recipes"
        ).order_by("id")
        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                is_subscribed=Exists(
                    self.request.user.subscriptions.filter(
                        author=OuterRef("pk")
                    )
                ),
                recipes_count=Count("recipes"),
            )
        return queryset

    def get_permissions(self) -> tuple[BasePermission, ...]:
        """Назначает права доступа в зависимости от выполняемого действия."""

        if self.action in ("list", "retrieve"):
            return (AllowAny(),)
        if self.action in (
            "me",
            "avatar",
            "subscriptions",
            "subscribe",
        ):
            return (IsAuthenticated(),)
        return super().get_permissions()

    @action(
        methods=("put",),
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path="me/avatar",
    )
    def avatar(self, request: Request) -> Response:
        """Загружает или обновляет аватар текущего пользователя."""

        serializer: AvatarSerializer = AvatarSerializer(
            request.user, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"avatar": request.user.avatar.url})

    @avatar.mapping.delete
    def delete_avatar(self, request: Request) -> Response:
        """Удаляет аватар текущего пользователя."""

        request.user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=("post", "delete"),
        detail=True,
        permission_classes=(IsAuthenticated,),
        url_path="subscribe",
    )
    def subscribe(self, request: Request, id: int | None = None) -> Response:
        """Создает или удаляет подписку на автора."""

        author: User = get_object_or_404(User, id=id)
        if request.method == "POST":
            if request.user == author:
                return Response(
                    {"errors": ("Нельзя подписаться на самого себя.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if request.user.subscriptions.filter(author=author).exists():
                return Response(
                    {"errors": "Вы уже подписаны."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            request.user.subscriptions.create(author=author)
            serializer: SubscriptionSerializer = SubscriptionSerializer(
                author, context=self.get_serializer_context()
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subscription: QuerySet[Subscription] = (
            request.user.subscriptions.filter(author=author)
        )
        if not subscription.exists():
            return Response(
                {"errors": "Вы не подписаны."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=("get",),
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path="subscriptions",
    )
    def subscriptions(self, request: Request) -> Response:
        """Возвращает список авторов, на которых подписан пользователь."""

        users: QuerySet[User] = (
            self.get_queryset()
            .filter(subscribers__subscriber=request.user)
            .distinct()
        )
        page = self.paginate_queryset(users)
        serializer: SubscriptionSerializer = SubscriptionSerializer(
            page, many=True, context=self.get_serializer_context()
        )
        return self.get_paginated_response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Предоставляет CRUD-операции для рецептов и связанные
    пользовательские действия.
    """

    queryset: QuerySet[Recipe] = Recipe.objects.all()
    filterset_class: type[RecipeFilter] = RecipeFilter

    def get_queryset(self) -> QuerySet[Recipe]:
        """
        Возвращает queryset рецептов с оптимизированной
        загрузкой связанных данных.
        """

        queryset: QuerySet[Recipe] = Recipe.objects.select_related(
            "author"
        ).prefetch_related("tags", "ingredient_amounts__ingredient")
        request: Request = self.request
        if request.user.is_authenticated:
            queryset = queryset.annotate(
                is_favorited=Exists(
                    request.user.favorites.filter(recipe=OuterRef("pk"))
                ),
                is_in_shopping_cart=Exists(
                    request.user.shopping_carts.filter(recipe=OuterRef("pk"))
                ),
            )
        return queryset

    def get_serializer_class(
        self,
    ) -> type[RecipeSerializer | RecipeWriteSerializer]:
        """Выбирает сериализатор в зависимости от выполняемого действия."""

        if self.action in ("list", "retrieve"):
            return RecipeSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer: RecipeWriteSerializer) -> None:
        """Сохраняет рецепт, назначая текущего пользователя автором."""

        serializer.save(author=self.request.user)

    def get_permissions(self) -> tuple[BasePermission, ...]:
        """Назначает права доступа в зависимости от выполняемого действия."""

        if self.action in ("list", "retrieve", "get_link"):
            return (AllowAny(),)
        if self.action in (
            "create",
            "favorite",
            "shopping_cart",
            "download_shopping_cart",
        ):
            return (IsAuthenticated(),)
        return (IsAuthorOrAdminOrReadOnly(),)

    @action(
        methods=("get",),
        detail=True,
        permission_classes=(AllowAny,),
        url_path="get-link",
    )
    def get_link(self, request: Request, pk: int | None = None) -> Response:
        """Возвращает короткую ссылку на рецепт."""

        recipe: Recipe = get_object_or_404(Recipe, pk=pk)
        short_link: ShortLink
        short_link, _ = ShortLink.objects.get_or_create(recipe=recipe)
        return Response(
            {
                "short-link": (
                    f"{request.scheme}://"
                    f"{request.get_host()}/s/{short_link.code}"
                )
            }
        )

    @action(
        methods=("post", "delete"),
        detail=True,
        permission_classes=(IsAuthenticated,),
        url_path="favorite",
    )
    def favorite(self, request: Request, pk: int | None = None) -> Response:
        """Добавляет рецепт в избранное или удаляет его из него."""

        recipe: Recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == "POST":
            if request.user.favorites.filter(recipe=recipe).exists():
                return Response(
                    {"errors": "Рецепт уже добавлен в избранное."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            request.user.favorites.create(recipe=recipe)
            serializer: RecipeShortSerializer = RecipeShortSerializer(
                recipe, context=self.get_serializer_context()
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        favorite: QuerySet[Favorite] = request.user.favorites.filter(
            recipe=recipe
        )
        if not favorite.exists():
            return Response(
                {"errors": "Рецепта нет в избранном."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=("post", "delete"),
        detail=True,
        permission_classes=(IsAuthenticated,),
        url_path="shopping_cart",
    )
    def shopping_cart(
        self, request: Request, pk: int | None = None
    ) -> Response:
        """Добавляет рецепт в список покупок или удаляет его из него."""

        recipe: Recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == "POST":
            if request.user.shopping_carts.filter(recipe=recipe).exists():
                return Response(
                    {"errors": "Рецепт уже добавлен в список покупок."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            request.user.shopping_carts.create(recipe=recipe)
            serializer: RecipeShortSerializer = RecipeShortSerializer(
                recipe, context=self.get_serializer_context()
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        shopping_cart: QuerySet[ShoppingCart] = (
            request.user.shopping_carts.filter(recipe=recipe)
        )
        if not shopping_cart.exists():
            return Response(
                {"errors": "Рецепта нет в списке покупок."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=("get",),
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path="download_shopping_cart",
    )
    def download_shopping_cart(self, request: Request) -> HttpResponse:
        """Формирует и возвращает список покупок в текстовом формате."""

        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__shopping_carts__user=request.user
            )
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(amount=Sum("amount"))
            .order_by("ingredient__name")
        )
        shopping_list: list[str] = ["Нужно купить:\n"]
        for ingredient in ingredients:
            shopping_list.append(
                f"{ingredient['ingredient__name']} "
                f"— {ingredient['amount']} "
                f"{ingredient['ingredient__measurement_unit']}"
            )
        response: HttpResponse = HttpResponse(
            "\n".join(shopping_list), content_type="text/plain"
        )
        response["Content-Disposition"] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response
