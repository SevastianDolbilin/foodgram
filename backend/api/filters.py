from django_filters import rest_framework as filters

from .models import Recipe


class RecipeFilter(filters.FilterSet):
    """
    Фильтр для фильтрации по тегам, авторам, спискам покупок и избранным.
    """

    author = filters.NumberFilter(field_name="author__id", lookup_expr="exact")
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
        if value:
            return queryset.filter(shoppingcart__isnull=False).distinct()
        return queryset

    def filter_favorited(self, queryset, name, value):
        """
        Фильтрует рецепты, которые находятся в избранном.
        """
        if value:
            return queryset.filter(favorite__isnull=False).distinct()
        return queryset
