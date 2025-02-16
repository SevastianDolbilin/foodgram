from django.contrib import admin

from foodgram_backend.constants import VALIDATOR_COUNT
from shopping.models import Favorite
from .models import Ingredient, Recipe, RecipeIngredient, Tag


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = VALIDATOR_COUNT
    fields = ("ingredient", "amount")

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админ модель рецептов."""

    list_display = ("id", "name", "author", "favorites_count")
    search_fields = ("name", "author__username")
    list_filter = ("tags",)
    readonly_fields = ("favorites_count",)
    inlines = [RecipeIngredientInline]

    @admin.display(description="Число добавлений в избранное")
    def favorites_count(self, obj):
        """Возвращает общее число добавлений рецепта в избранное."""
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(Ingredient)
class IngregientAdmin(admin.ModelAdmin):
    """Админ модель ингридиентов."""

    list_display = ("id", "name", "measurement_unit")
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админ модель тегов."""

    list_display = ("id", "name", "slug")
    search_fields = ("name", "slug")
