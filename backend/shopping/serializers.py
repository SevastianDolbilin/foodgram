from rest_framework import serializers

from .models import Favorite, ShoppingCart


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор списка избранных рецептов."""
    class Meta:
        model = Favorite
        fields = ["user", "recipe", "added_at"]


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецептов в список покупок."""
    class Meta:
        model = ShoppingCart
        fields = ["id", "name", "image", "cooking_time"]
