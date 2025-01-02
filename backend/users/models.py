from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User as DjangoUser
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Subscription(models.Model):
    """Модель подписки."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Подписка"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followers",
        verbose_name="Автор"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата подписки."
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique_subscribe"
            )
        ]

    def __str__(self):
        return f"{self.user.username} подписан на {self.author.username}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.user.username}"