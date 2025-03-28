from django.conf import settings
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from shopping.models import ShoppingCart

from .filters import RecipeFilter
from .models import Ingredient, Recipe, RecipeIngredient, Tag
from .permissions import Anonymous, Author
from .serializers import (IngredientSerializer, RecipeSerializer,
                          RecipeWriteSerializer, TagSerializer)


class BaseViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    """Базовый вьюсет для наследования."""
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_fileds = ["name"]
    ordering_fields = ["name"]

    def list(self, request, *args, **kwargs):
        """Переопределение метода get."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TagViewSet(BaseViewSet):
    """ViewSet тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(BaseViewSet):
    """ViewSet ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet рецептов."""
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_permissions(self):
        """Получение разрешения в зависимости от типа запроса."""
        if self.request.method in ["POST"]:
            permission_classes = [IsAuthenticated]
        elif self.request.method in ["PUT", "PATCH", "DELETE"]:
            permission_classes = [Author]
        else:
            permission_classes = [Anonymous]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """Возвращаем разные сериализаторы для чтения и записи."""
        if self.action in ["create", "update", "partial_update"]:
            return RecipeWriteSerializer
        return RecipeSerializer

    @action(detail=True, methods=["delete"], url_path="delete-image")
    def delete_image(self, request, pk=None):
        """Удаление изображения из рецепта."""
        recipe = self.get_object()
        if not recipe.image:
            return Response({"detail": "Изображение уже удалено."})
        recipe.image.delete(save=True)
        return Response(
            {"detail": "Изображение удалено."},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=True, methods=["get"], url_path="get-link")
    def get_link(self, request, pk=None):
        """Получение ссылки на рецепт."""
        recipe = get_object_or_404(Recipe, pk=pk)
        base_url = settings.BASE_URL
        short_link = f"{base_url}/recipes/{recipe.id}"

        return Response({"short-link": short_link}, status=status.HTTP_200_OK)

    @action(
        detail=False, methods=["get"], url_path="download_shopping_cart"
    )
    def download_shopping_cart(self, request):
        """Скачать список покупок в формате TXT."""

        shopping_cart = ShoppingCart.objects.filter(user=request.user)

        if not shopping_cart.exists():
            return Response(
                {"detail": "Список покупок пуст."},
                status=status.HTTP_400_BAD_REQUEST
            )

        ingredient_totals = (
            RecipeIngredient.objects.filter(
                recipe__shoppingcart__user=request.user
            ).values(
                "ingredient__name", "ingredient__measurement_unit"
            ).annotate(total_amount=Sum("amount"))
        )

        shopping_list = ["Список покупок:\n"]
        for item in ingredient_totals:
            shopping_list.append(
                f"- {item['ingredient__name']}: "
                f"{item['total_amount']} "
                f"{item['ingredient__measurement_unit']}"
            )

        response = HttpResponse(
            "".join(shopping_list), content_type="text/plain"
        )
        response[
            "Content-Disposition"
        ] = 'attachment; filename="shopping_list.txt"'

        return response
