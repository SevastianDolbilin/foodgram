from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from api.paginations import CustomPagination
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Subscription
from .serializers import (AuthorSerializer, AvatarSerializer,
                          SubscribeSerializator)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Кастомный вьюсет для модели пользователей."""
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

    @action(detail=True, methods=["post"])
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
            SubscribeSerializator(
                subscription, context={"request": request}
            ).data, status=status.HTTP_201_CREATED
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

    @action(detail=False, methods=["put", "delete"], url_path="me/avatar")
    def avatar(self, request):
        user = request.user
        user_profile = user.profile

        if request.method == "DELETE":
            if user_profile.avatar:
                user_profile.avatar.delete(save=False)
                user_profile.avatar = None
                user_profile.save()
                return Response(
                    {
                        "detail": "Аватар удален."
                    },
                    status=status.HTTP_204_NO_CONTENT
                )
            return Response(
                {"detail": "Аватар отсутствует."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if "avatar" not in request.data:
            return Response(
                {
                    "error": "Поле avatar обязательно к заполнению."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AvatarSerializer(
            instance=user_profile,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()

            avatar_url = request.build_absolute_uri(
                user_profile.avatar.url
            ) if user_profile.avatar else None
            response_data = {
                "avatar": avatar_url
            }
            return Response(response_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"], url_path="subscriptions")
    def subscriptions(self, request):
        """Получение списка подписок текущего пользователя."""
        user = request.user
        subscriptions = Subscription.objects.filter(user=user)

        paginator = CustomPagination()
        page = paginator.paginate_queryset(subscriptions, request)
        serializer = SubscribeSerializator(
            page, many=True, context={"request": request}
        )

        return paginator.get_paginated_response(serializer.data)
