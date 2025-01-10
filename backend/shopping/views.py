from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipe.models import Recipe
from recipe.serializers import RecipeWriteSerializer

from .models import Favorite, ShoppingCart
from .serializers import FavoriteSerializer, ShoppingCartSerializer

User = get_user_model()


class ShoppingCartViewSet(viewsets.ModelViewSet):
    """Вьюсет списка покупок."""
    permission_classes = [IsAuthenticated]

    @action(
        detail=False, methods=["get"], url_path="download_shopping_cart"
    )
    def download_shopping_cart(self, request):
        """Скачать список покуп в формате ТХТ."""
        shopping_cart = ShoppingCart.objects.filter(user=request.user)

        if not shopping_cart:
            return Response(
                {"detail": "Список покупок пуст."},
                status=status.HTTP_400_BAD_REQUEST
            )
        shopping_list = [
            f"{item.recipe.name}"
            f"({item.recipe.cooking_time} мин\n" for item in shopping_cart
        ]
        response = HttpResponse(
            "\n".join(shopping_list),
            content_type="text/plain"
        )
        response["Content-Disposition"] = (
            'attachment filename="shopping_cart.txt"'
        )
        return response

    @action(detail=True, methods="post", url_path="shopping_cart")
    def add_to_cart(self, request, pk=None):
        """Добавить рецепт в список покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        if ShoppingCart.objects.filter(
            user=request.user, recipe=recipe
        ).exists():
            return Response(
                {"detail: Рецепт уже добавлен в список покупок."},
                status=status.HTTP_400_BAD_REQUEST
            )
        ShoppingCart.objects.create(user=request.user, recipe=recipe)
        return Response(
            RecipeWriteSerializer(recipe).data, status=status.HTTP_201_CREATED
        )

    @add_to_cart.mapping.delete
    def remove_from_cart(self, request, pk=None):
        """Удалить рецепт из списка покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        shopping_item = ShoppingCart.objects.filter(
            user=request.user, recipe=recipe
        ).first()
        if not shopping_item():
            return Response(
                {"detail: Рецепт отсутствует в списке покупок."},
                status=status.HTTP_400_BAD_REQUEST
            )
        shopping_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(viewsets.ModelViewSet):
    """Вьюсет избранного."""
    permissions_classes = [IsAuthenticated]

    def create(self, request, recipe_id=None):
        """Добавляет рецепт в избранное."""
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = request.user

        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError("Рецепт уже добавлен в избранное.")

        Favorite.objects.create(user=user, recipe=recipe)
        return Response(
            {"detail": "Рецепт добавлен в избранное."},
            status=status.HTTP_201_CREATED
        )

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
