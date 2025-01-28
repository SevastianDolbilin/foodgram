from rest_framework import permissions


class Anonymous(permissions.BasePermission):
    """Разрешения для анонимных пользователей."""
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS


class RegictredUser(permissions.BasePermission):
    """Разрешения для зарегестрированных пользователей."""
    def has_permission(self, request, view):
        return request.user.is_aunthenticated


class Author(permissions.BasePermission):
    """Разрешения для пользователей с ролью автор."""

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return getattr(obj, "author", None)


class IsAuthorOrAdminForPatch(permissions.BasePermission):
    """
    Разрешение, позволяющее только авторам или администраторам
    изменять рецепты через PATCH-запрос.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method == "PATCH":
            return obj.author == request.user or request.user.is_staff

        return True


class Administrator(permissions.BasePermission):
    """Разрешения для пользователей с ролью суперюзер"""
    def is_admin(self, request):
        return request.user.is_authenticated and request.user.is_staff

    def has_permission(self, request, view):
        return self.is_admin(request)

    def has_object_permission(self, request, view, obj):
        return self.is_admin(request)
