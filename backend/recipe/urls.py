from django.urls import include, path
from rest_framework.routers import DefaultRouter
from shopping.views import FavoriteViewSet, ShoppingCartViewSet
from users.views import CustomUserViewSet

from .views import IngredientViewSet, RecipeViewSet, TagViewSet

router = DefaultRouter()
router.register("tags", TagViewSet, basename="tag")
router.register("ingredients", IngredientViewSet, basename="ingredient")
router.register("recipes", RecipeViewSet, basename="recipe")
router.register("users", CustomUserViewSet, basename="user")


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
