from rest_framework import serializers
from rest_framework.validators import ValidationError


from drf_extra_fields.fields import Base64ImageField
from django.contrib.auth.models import User as DjoserUser


from foodgram_backend.constants import NAME_LENGTH, REGISTRATION_NAME
from recipe.models import Recipe
from .models import Subscription, User, UserProfile


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

    def update(self, instance, validated_data):
        avatar = validated_data.get("avatar", instance.avatar)
        instance.avatar = avatar
        instance.save()
        return instance


class AuthorSerializer(serializers.ModelSerializer):
    """Сериализатор автора."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(source="profile.avatar")

    class Meta:
        model = User
        fields = [
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar"
        ]

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на автора."""
        user = self.context["request"].user
        if user.is_authenticated:
            return user.subscriptions.filter(author=obj).exists()
        return False


class SubscribeReadSerializator(serializers.ModelSerializer):
    """Сериализатор вывода информации о подписках."""
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(source="profile.avatar")
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar",
            "recipes",
            "recipes_count"
        ]

    def get_recipes(self, obj):
        """Получение рецептов."""
        request = self.context.get("request")
        if not request:
            return []

        limit = request.query_params.get("recipes_limit")
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[: int(limit)]
        return RecipeShortSerializer(recipes, many=True).data

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на автора."""
        user = self.context["request"].user
        if user.is_authenticated:
            return user.subscriptions.filter(author=obj).exists()
        return False

    def get_recipes_count(self, obj):
        return len(obj.recipes.all())


class SubscribeSerializator(serializers.ModelSerializer):
    """Сериализатор подписок."""

    class Meta:
        model = Subscription
        fields = ["__all__"]

    def to_representation(self, instance):
        """Репрезентация данных."""
        serializer = SubscribeReadSerializator(
            instance.author, context=self.context
        )
        return serializer.data


class CustomUserCreateSerializer(serializers.ModelSerializer):
    """Кастомный вьсюет объекта User."""
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(max_length=NAME_LENGTH, required=True)
    username = serializers.RegexField(
        regex=r"^[\w.@+-]+$",
        max_length=REGISTRATION_NAME,
        required=True,
        error_messages={
            "invalid": (
                "Имя пользователя может содержать только"
                "буквы, цифры и символы @/./+/-/_"
            ),
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
        """Валидация почты."""
        if DjoserUser.objects.filter(email=value).exists():
            raise ValidationError("Пользователь с таким email уже существует.")
        return value

    def validate_username(self, value):
        """Валидация имение пользователя."""
        if DjoserUser.objects.filter(username=value).exists():
            raise ValidationError(
                "Пользователь с таким username уже существует."
            )
        return value

    def create(self, validated_data):
        """Создание пользователя."""
        user = DjoserUser.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        return user
