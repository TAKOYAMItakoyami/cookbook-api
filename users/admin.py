"""Настройка административной панели приложения users."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User

admin.site.site_header = "Администрирование Cookbook"
admin.site.site_title = "Cookbook"
admin.site.index_title = "Панель администратора"


@admin.register(User)
class CustomUserAdmin(DjangoUserAdmin):
    """Настраивает отображение пользователей в панели администратора."""

    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
    )
    search_fields = (
        "username",
        "email",
    )
    ordering = ("username",)

    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            "Дополнительно",
            {
                "fields": ("avatar",),
            },
        ),
    )
