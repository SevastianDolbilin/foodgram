from django_filters import rest_framework as filters

from .models import Recipe


class RecipeFilter(filters.FilterSet):
    """Кастомный фильтр для фильтрации по тегам, авторам, спискам покупок."""

    tags = filters.CharFilter(
        field_name="tags__slug", method="filter_by_tags", distinct=True
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method="filter_in_shopping_cart"
    )
    is_favorited = filters.BooleanFilter(method="filter_favorited")

    class Meta:
        model = Recipe
        fields = ["author", "tags", "is_in_shopping_cart", "is_favorited"]

    def filter_by_tags(self, queryset, name, value):
        """
        Фильтрует рецепты по тегам.
        """
        tags = self.request.query_params.getlist("tags")
        return queryset.filter(tags__slug__in=tags).distinct()

    def filter_in_shopping_cart(self, queryset, name, value):
        """
        Фильтрует рецепты, которые находятся в списке покупок.
        """
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shoppingcart__user=user).distinct()
        return queryset

    def filter_favorited(self, queryset, name, value):
        """
        Фильтрует рецепты, которые находятся в избранном.
        """
        if value:
            return queryset.filter(favorite__isnull=False).distinct()
        return queryset
