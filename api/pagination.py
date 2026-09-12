"""Класс пагинации API."""

from rest_framework.pagination import PageNumberPagination

from .constants import CUSTOM_PAGE_SIZE


class CustomPagination(PageNumberPagination):
    """Пагинация с настраиваемым количеством элементов на странице."""

    page_size: int = CUSTOM_PAGE_SIZE
    page_size_query_param: str = "limit"
