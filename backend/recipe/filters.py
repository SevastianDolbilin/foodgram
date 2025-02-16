from django_filters import AllValuesMultipleFilter
from django_filters import rest_framework as filters

from .models import Recipe


class RecipeFilter(filters.FilterSet):
    """
    Фильтр для фильтрации по тегам, авторам, списку покупок и избранному.
    """

    tags = AllValuesMultipleFilter(
        field_name="tags__slug",
        lookup_expr="in",
    )

    is_in_shopping_cart = filters.BooleanFilter(
        method="filter_in_shopping_cart"
    )
    is_favorited = filters.BooleanFilter(method="filter_favorited")

    class Meta:
        model = Recipe
        fields = ["author", "tags", "is_in_shopping_cart", "is_favorited"]

    def filter_in_shopping_cart(self, queryset, name, value):
        """
        Фильтрует рецепты, которые находятся в списке покупок пользователя.
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
