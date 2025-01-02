from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

from .models import Subscription

User = get_user_model()


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    """Настройка отображения пользователей в админке."""
    
    list_display = (
        "id", "username", "email", "first_name", "last_name", "is_active"
    )
    search_fields = ("username", "email")
    list_filter = ("is_active", "is_staff")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Настройка отображения подписок в админке."""

    list_display = ("id", "user", "author", "created_at")
    search_fields = ("user__username", "author__username")
    list_filter = ("created_at",)
    ordering = ("-created_at",)
