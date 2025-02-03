from django.shortcuts import get_object_or_404, redirect
from django.urls import include, path, reverse
from rest_framework.routers import DefaultRouter
from shopping.views import FavoriteViewSet, ShoppingCartViewSet
from users.views import CustomUserViewSet

from .models import Recipe
from .views import IngredientViewSet, RecipeViewSet, TagViewSet

router = DefaultRouter()
router.register("tags", TagViewSet, basename="tag")
router.register("ingredients", IngredientViewSet, basename="ingredient")
router.register("recipes", RecipeViewSet, basename="recipe")
router.register("users", CustomUserViewSet, basename="user")


def short_link_redirect(request, recipe_id):
    """
    Редиректит с короткой ссылки на полную страницу рецепта.
    """
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    return redirect(reverse("recipe_detail", kwargs={"pk": recipe.id}))


urlpatterns = [
    path("", include(router.urls)),

    path(
        "api/auth/signup/",
        CustomUserViewSet.as_view({"post": "create"}),
        name="signup",
    ),
    path(
        "recipes/<int:recipe_id>/shopping_cart/",
        ShoppingCartViewSet.as_view({"post": "create", "delete": "destroy"}),
        name="recipe-shopping-cart",
    ),
    path(
        "recipes/<int:recipe_id>/favorite/",
        FavoriteViewSet.as_view({"post": "create", "delete": "destroy"}),
        name="recipe-favorite",
    ),
]
