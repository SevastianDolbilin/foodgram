from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from recipe.views import IngredientViewSet, RecipeViewSet, TagViewSet
from rest_framework.routers import DefaultRouter
from shopping.views import FavoriteViewSet, ShoppingCartViewSet
from users.views import CustomUserViewSet

router = DefaultRouter()
router.register("tags", TagViewSet, basename="tag")
router.register("ingredients", IngredientViewSet, basename="ingredient")
router.register("recipes", RecipeViewSet, basename="recipe")
router.register("users", CustomUserViewSet, basename="user")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(router.urls)),
    path("api/auth/", include("djoser.urls")),
    path("api/auth/token", include("djoser.urls.authtoken")),
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

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
