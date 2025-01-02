from foodgram_backend.constants import PAGINTAION_NUMBER
from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Кастомный пагинатор с переопределенным полем."""
    page_size = PAGINTAION_NUMBER
    page_size_query_param = "limit"
