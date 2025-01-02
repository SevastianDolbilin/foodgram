import base64
import uuid

from django.contrib.auth.models import User as DjoserUser
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from foodgram_backend.constants import NAME_LENGTH, REGISTRATION_NAME
from recipe.models import Recipe
from rest_framework import serializers
from rest_framework.validators import ValidationError

from .models import Subscription, User, UserProfile


class Base64ImageField(serializers.ImageField):
    """Кастомный тип поля для декодирования base64."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(
                base64.b64decode(imgstr), name=f'{uuid.uuid4()}.{ext}'
            )
        return super().to_internal_value(data)


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор короткой информации о рецетпе."""

    class Meta:
        model = Recipe
        fields = ["id", "name", "image", "cooking_time"]


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор аватара."""
    avatar = Base64ImageField(required=True)

    class Meta:
        model = UserProfile
        fields = ["avatar"]


class AuthorSerializer(serializers.ModelSerializer):
    """Сериализатор автора."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        ]

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на автора."""
        user = self.context["request"].user
        if user.is_authenticated:
            return user.subscriptions.filter(author=obj).exists()
        return False


class SubscribeSerializator(serializers.ModelSerializer):
    """Сериализатор подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source="author.recipes.count", read_only=True
    )

    class Meta:
        model = Subscription
        fields = ["id", "author", "recipes", "recipes_count"]

    def get_recipes(self, obj):
        request = self.context.get("request")
        if not request:
            return []

        limit = request.query_params.get("recipes_limit")
        recipes = obj.author.recipes.all()
        if limit:
            recipes = recipes[: int(limit)]
        return RecipeShortSerializer(recipes, many=True).dat


class CustomUserCreateSerializer(serializers.ModelSerializer):
    """Кастомный вьсюет объекта User."""
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(max_length=NAME_LENGTH, required=True)
    username = serializers.RegexField(
        regex=r"^[\w.@+-]+$",
        max_length=150,
        required=True,
        error_messages={
            "invalid": "Имя пользователя может содержать только"
            + "буквы, цифры и символы @/./+/-/_",
            "max_length": "Длина этого поля не должна превышать 150 символов.",
        },
    )
    first_name = serializers.CharField(
        max_length=REGISTRATION_NAME, required=True
    )
    last_name = serializers.CharField(
        max_length=REGISTRATION_NAME, required=True
    )

    class Meta:
        model = DjoserUser
        fields = [
            "id", "username", "email", "first_name", "last_name", "password"
        ]

    def validate_email(self, value):
        if DjoserUser.objects.filter(email=value).exists():
            raise ValidationError("Пользователь с таким email уже существует.")
        return value

    def validate_username(self, value):
        if DjoserUser.objects.filter(username=value).exists():
            raise ValidationError(
                "Пользователь с таким username уже существует."
            )
        return value

    def create(self, validated_data):
        user = DjoserUser.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        return user
