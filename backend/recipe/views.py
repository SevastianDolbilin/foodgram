from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from shopping.models import ShoppingCart

from .filters import RecipeFilter
from .models import Ingredient, Recipe, Tag
from .permissions import Administrator, Anonymous, Author
from .serializers import (IngredientSerializer, RecipeSerializer,
                          RecipeWriteSerializer, TagSerializer)

User = get_user_model()


class BaseViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        """Фильтрация по началу названия."""
        queryset = super().get_queryset()
        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class TagViewSet(BaseViewSet):
    queryset = Tag.objects.all().order_by("name")
    serializer_class = TagSerializer


class IngredientViewSet(BaseViewSet):
    queryset = Ingredient.objects.all().order_by("name")
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def update(self, request, *args, **kwargs):
        """Переопределенный метод update."""
        recipe = self.get_object()
        if recipe.author != request.user:
            raise PermissionDenied("Вы не можете редактировать чужой рецепт.")
        if "ingredients" not in request.data:
            raise ValidationError(
                "Поле ingredients обязательно для заполнения."
            )
        if "tags" not in request.data:
            raise ValidationError("Поле tags обязательно для заполнения.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Переопределенный метод destroy (для коррекции разрешений)."""
        recipe = self.get_object()
        if recipe.author != request.user:
            raise PermissionDenied("Вы не можете удалить чужой рецепт.")
        return super().destroy(request, *args, **kwargs)

    def get_permissions(self):
        """Получение разрешения в зависимости от типа запроса."""
        if self.request.method in ["POST", "PUT", "PATCH"]:
            permission_classes = [IsAuthenticated]
        elif self.request.method == "DELETE":
            permission_classes = [Author, Administrator]
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
        """Создание короткой ссылки на рецепт."""
        self.get_object()
        short_link = request.build_absolute_uri(
            "api:recipe-detail", kwargs={"id": id}
        )
        serializer = self.get_serializer(
            data={'original_url': short_link},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"short-link": short_link}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="download_shopping_cart")
    def download_shopping_cart(self, request):
        """Скачать список покупок в формате TXT."""
        shopping_cart = ShoppingCart.objects.filter(user=request.user)

        if not shopping_cart.exists():
            return Response(
                {"detail": "Список покупок пуст."},
                status=status.HTTP_400_BAD_REQUEST
            )

        shopping_list = []
        for item in shopping_cart:
            ingredients = ", ".join(
                (
                    f"{ingredient.name}"
                    f"{ingredient.measurement_unit}"
                )
                for ingredient in item.recipe.ingredients.all()
            )
            shopping_list.append(
                f"{ingredients} ({item.recipe.cooking_time} мин)"
            )

        response = HttpResponse(
            "\n".join(shopping_list), content_type="text/plain"
        )
        response[
            "Content-Disposition"
        ] = 'attachment; filename="shopping_cart.txt"'
        return response
