from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from foodgram_backend.constants import (NAME_LENGTH, UNIT_LENGTH,
                                        VALIDATOR_COUNT)

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингридиента."""

    name = models.CharField(
        max_length=NAME_LENGTH, unique=True, verbose_name="Название"
    )
    measurement_unit = models.CharField(
        max_length=UNIT_LENGTH, verbose_name="Единица измерения"
    )

    class Meta:
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"

    def __str__(self):
        return f"{self.name}({self.measurement_unit})"


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        max_length=NAME_LENGTH, unique=True, verbose_name="Название"
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="Идентификатор",
        help_text=(
            "Идентификатор страницы для URL; "
            "разрешены символы латиницы, цифры, дефис и подчёркивание."
        ),
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор"
    )
    name = models.TextField(max_length=NAME_LENGTH, verbose_name="Название")
    image = models.ImageField(upload_to="recipes/")
    text = models.TextField(verbose_name="Описание")
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        related_name="recipes",
        through_fields=("recipe", "ingredient"),
        verbose_name="Ингридиенты"
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
        verbose_name="Теги"
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name="Время приготовления (минуты)",
        validators=[MinValueValidator(VALIDATOR_COUNT)],
        help_text="Минимальное время приготовление - 1 минута."
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["-id"]

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Промежуточная модель дял рецептов и ингредиентов."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Рецепты"
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredient_recipes",
        verbose_name="Ингридиенты"
    )
    amount = models.IntegerField(
        verbose_name="Количество",
        validators=[MinValueValidator(VALIDATOR_COUNT)],
    )

    class Meta:
        verbose_name = "Ингридиент рецетпа"
        verbose_name_plural = "Ингридиенты рецепта"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_recipe_ingredient"
            )
        ]

    def __str__(self):
        return (
            f"{self.ingredient.name} — {self.amount} "
            f"{self.ingredient.measurement_unit}"
        )
