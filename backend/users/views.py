from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from django.shortcuts import get_object_or_404
from recipe.models import Recipe
from recipe.paginations import CustomPagination
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from shopping.models import Favorite, ShoppingCart
from shopping.serializers import FavoriteSerializer, ShoppingCartSerializer

from .models import Subscription
from .serializers import AuthorSerializer, SubscribeSerializator

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Кастомный вьюсет для реализации функций подписки через djoser."""
    queryset = User.objects.all()
    serializer_class = AuthorSerializer
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        elif self.action in ["subscribe", "delete_subscribe"]:
            return [IsAuthenticated()]
        return super().get_permissions()

    def retrieve(self, request, *args, **kwargs):
        """Получение информации о пользователе."""
        instance = self.get_object()
        serializer = AuthorSerializer(instance, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        """Подписка на пользователя."""
        user = self.request.user
        author = self.get_object()

        if user == author:
            return Response(
                {"detail": "Нельзя подписаться на самого себя."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Subscription.objects.filter(user=user, author=author).exists():
            return Response(
                {"detail": "Вы уже подписаны на этого автора."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription = Subscription.objects.create(user=user, author=author)
        return Response(
            {
                "detail": "Подписка успешно создана.",
                "subscription": SubscribeSerializator(subscription).data,
            },
            status=status.HTTP_201_CREATED,
        )

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        """Отписка от пользователя."""
        user = self.request.user
        author = self.get_object()

        try:
            subscription = Subscription.objects.get(user=user, author=author)
        except Subscription.DoesNotExist:
            return Response(
                {"detail": "Вы не подписаны на этого автора."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription.delete()
        return Response(
            {"detail": "Успешная отписка."}, status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        user = request.user
        serializer = AuthorSerializer(user, context={"request": request})
        return Response(serializer.data)

