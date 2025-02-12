from django.shortcuts import get_object_or_404
from foodgram_backend.constants import VALIDATOR_COUNT
from rest_framework import serializers, status
from rest_framework.response import Response
from shopping.models import Favorite, ShoppingCart
from users.serializers import AuthorSerializer, Base64ImageField

from .models import Ingredient, Recipe, RecipeIngredient, Tag


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
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit", read_only=True
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


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""
    image = Base64ImageField()
    ingredients = IngredientReadSerializer(
        many=True, source="recipe_ingredients", required=True
    )
    tags = TagSerializer(many=True)
    author = AuthorSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    cooking_time = serializers.IntegerField(min_value=VALIDATOR_COUNT)

    class Meta:
        model = Recipe
        fields = [
            "id",
            "ingredients",
            "tags",
            "author",
            "is_favorited",
            "is_in_shopping_cart",
            "image",
            "name",
            "text",
            "cooking_time",
        ]

    def get_is_favorited(self, obj):
        """Проверка наличия рецепта в избранном у пользователя."""
        user = self.request.user
        if not user.is_authenticated:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверка наличия рецепта в списке покупок у пользователя"""
        user = self.context["request"].user
        if not user.is_authenticated:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/обновления рецептов (для записи)."""
    image = Base64ImageField()
    ingredients = IngredientWriteSerializer(
        many=True, write_only=True, required=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )

    class Meta:
        model = Recipe
        fields = [
            "tags",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        ]

    def to_representation(self, instance):
        """Репрезентация данных."""
        serializer = RecipeSerializer(instance, context=self.context)
        return serializer.data

    def validate_ingredients(self, ingredients):
        """Валидируем ингредиенты."""
        if not ingredients:
            raise serializers.ValidationError(
                "Поле ingredients не может быть пустым."
            )
        repeat_ingredients = set()
        for ingredient in ingredients:
            if ingredient["id"] in repeat_ingredients:
                raise serializers.ValidationError(
                    "Ингредиенты повторяются."
                )
            repeat_ingredients.add(ingredient["id"])
        return ingredients

    def validate_tags(self, tags):
        """Валидируем теги."""
        if not tags:
            raise serializers.ValidationError(
                "Поле tags не может быть пустым."
            )
        repeat_tags = set()
        for tag in tags:
            if tag.id in repeat_tags:
                raise serializers.ValidationError(
                    "Теги повторяются."
                )
            repeat_tags.add(tag.id)
        return tags

    def _save_ingredients(self, recipe, ingredients):
        """Сохраняем ингредиенты для рецепта."""
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=get_object_or_404(
                        Ingredient, id=ingredient["id"].id
                    ),
                    amount=ingredient["amount"],
                )
                for ingredient in ingredients
            ]
        )

    def create(self, validated_data):
        """Создание рецепта."""
        user = self.context["request"].user
        ingredients = validated_data.pop("ingredients", None)
        tags_data = validated_data.pop("tags")
        if ingredients is None:
            return Response(
                {"detail": "Поля ingredients не может быть пустым."},
                status=status.HTTP_400_BAD_REQUEST
            )
        validated_data["author"] = user
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        recipe.save()
        self._save_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта."""
        ingredients = validated_data.pop("ingredients", None)
        tags_data = validated_data.pop("tags", None)

        instance = super().update(instance, validated_data)

        if ingredients:
            instance.recipe_ingredients.all().delete()
            self._save_ingredients(instance, ingredients)

        if tags_data:
            instance.tags.set(tags_data)

        return instance
