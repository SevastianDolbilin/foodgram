import base64
import uuid

from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator
from django.shortcuts import get_object_or_404
from foodgram_backend.constants import VALIDATOR_COUNT
from rest_framework import serializers
from shopping.models import Favorite, ShoppingCart
from shopping.serializers import FavoriteSerializer
from users.models import Subscription
from users.serializers import AuthorSerializer, Base64ImageField

from .models import Ingredient, Recipe, RecipeIngredient, Tag, User


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингридиентов."""

    class Meta:
        model = Ingredient
        fields = ["id", "name", "measurement_unit"]


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = ["id", "name", "slug"]


class IngredientReadSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиентов."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.CharField(source="ingredient.name")
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipeIngredient
        fields = ["id", "name", "measurement_unit", "amount"]


class IngredientWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи ингредиентов."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ["id", "amount"]


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов (для чтения)."""
    image = Base64ImageField()
    ingredients = IngredientReadSerializer(
        many=True, source='recipe_ingredients'
    )
    tags = TagSerializer(many=True)
    author = AuthorSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        ]

    def get_is_favorited(self, obj):
        """Проверяем, находится ли рецепт в избранном."""
        user = self.context.get("request").user
        if not user.is_authenticated:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверяем, находился ли объект в списке покупок."""
        user = self.context.get("request").user
        if not user.is_authenticated:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/обновления рецептов (для записи)."""
    image = Base64ImageField()
    ingredients = IngredientWriteSerializer(many=True, write_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = [
            "id",
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        ]

    def _save_ingredients(self, recipe, ingredients_data):
        """Сохраняем ингредиенты для рецепта."""
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=get_object_or_404(
                        Ingredient, id=ingredient_data["id"].id
                    ),
                    amount=ingredient_data["amount"],
                )
                for ingredient_data in ingredients_data
            ]
        )

    def create(self, validated_data):
        """Создание рецепта."""
        user = self.context["request"].user
        ingredients_data = validated_data.pop("ingredients", None)
        tags_data = validated_data.pop("tags")
        validated_data["author"] = user
        recipe = Recipe.objects.create(**validated_data)
        self._save_ingredients(recipe, ingredients_data)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта."""
        ingredients_data = validated_data.pop("ingredients", None)
        tags_data = validated_data.pop("tags", None)

        instance = super().update(instance, validated_data)

        if ingredients_data:
            instance.recipe_ingredients.all().delete()
            self._save_ingredients(instance, ingredients_data)

        if tags_data:
            instance.tags.set(tags_data)

        return instance
