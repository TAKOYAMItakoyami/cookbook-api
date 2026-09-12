"""Пользовательские разрешения API."""

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import View

from recipes.models import Recipe


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    """Разрешает изменять рецепт только автору или администратору."""

    def has_object_permission(
        self, request: Request, view: View, obj: Recipe
    ) -> bool:
        """Проверяет права пользователя на выполнение операции над объектом."""

        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_staff
        )
