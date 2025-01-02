from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework import status


from .filters import RecipeFilter
from .models import Ingredient, Recipe, Tag
from .serializers import (
    IngredientSerializer,
    RecipeWriteSerializer,
    TagSerializer,
    RecipeReadSerializer,
)

User = get_user_model()


class BaseViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
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

    def get_serializer_class(self):
        """Возвращаем разные сериализаторы для чтения и записи."""
        if self.action in ["create", "update", "partial_update"]:
            return RecipeWriteSerializer
        return RecipeReadSerializer

    @action(detail=True, methods=["delete"],url_path="delete-image")
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