from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from foodgram_backend.constants import PAGINTAION_NUMBER


class CustomPagination(PageNumberPagination):
    """Кастомный пагинатор с переопределенным полем."""

    page_size = PAGINTAION_NUMBER
    page_size_query_param = "limit"

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )
