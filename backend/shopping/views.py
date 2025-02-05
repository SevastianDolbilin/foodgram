from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from recipe.models import Recipe
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.serializers import RecipeShortSerializer

from .models import Favorite, ShoppingCart

User = get_user_model()


class ShoppingCartViewSet(viewsets.ModelViewSet):
    """Вьюсет списка покупок."""
    permission_classes = [IsAuthenticated]

    def create(self, request, recipe_id=None):
        """Добавить рецепт в список покупок."""
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if ShoppingCart.objects.filter(
            user=request.user, recipe=recipe
        ).exists():
            return Response(
                {"detail: Рецепт уже добавлен в список покупок."},
                status=status.HTTP_400_BAD_REQUEST
            )
        ShoppingCart.objects.create(user=request.user, recipe=recipe)
        serializer = RecipeShortSerializer(
            recipe, context={"request": request}
        )
        return Response(
            serializer.data, status=status.HTTP_201_CREATED
        )

    def destroy(self, request, recipe_id=None):
        """Удалить рецепт из списка покупок."""
        recipe = get_object_or_404(Recipe, id=recipe_id)
        shopping_item = ShoppingCart.objects.filter(
            user=request.user, recipe=recipe
        ).first()
        if not shopping_item:
            return Response(
                {"detail: Рецепт отсутствует в списке покупок."},
                status=status.HTTP_400_BAD_REQUEST
            )
        shopping_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(viewsets.ModelViewSet):
    """Вьюсет избранного."""
    permission_classes = [IsAuthenticated]

    def create(self, request, recipe_id=None):
        """Добавляет рецепт в избранное."""
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = request.user

        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError("Рецепт уже добавлен в избранное.")

        Favorite.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(
            recipe, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, recipe_id=None):
        """Удаляет рецепт из избранного."""
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = request.user

        favorite = Favorite.objects.filter(user=user, recipe=recipe).first()
        if not favorite:
            raise ValidationError("Рецепт не найден в избранном.")

        favorite.delete()

        return Response(
            {"detail": "Рецепт удален из избранного."},
            status=status.HTTP_204_NO_CONTENT,
        )
