from django_filters import rest_framework as filters

from .models import Recipe, Tag


class RecipeFilter(filters.FilterSet):
    """Кастомный фильтр для фильтрации по тегам и авторам."""

    author = filters.NumberFilter(field_name="author__id", lookup_expr="exact")
    tags = filters.CharFilter(
        field_name="tags__slug", method="filter_by_tags", distinct=True
    )

    class Meta:
        model = Recipe
        fields = ["author", "tags"]

    def filter_by_tags(self, queryset, name, value):
        """
        Фильтрует рецепты по тегам.
        """
        tags = self.request.query_params.getlist("tags")
        return queryset.filter(tags__slug__in=tags).distinct()
