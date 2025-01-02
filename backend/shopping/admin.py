from django.contrib import admin

from .models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Настройка отображения избранного в админке."""

    list_display = ("id", "user", "recipe", "added_at")
    search_fields = ("user__username", "recipe__name")
    list_filter = ("added_at",)
    readonly_fields = ("added_at",)
