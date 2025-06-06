from rest_framework.pagination import (
    LimitOffsetPagination, PageNumberPagination
)

DEFAULT_PAGE_SIZE = 6


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = DEFAULT_PAGE_SIZE


class SubscriptionsPagination(LimitOffsetPagination):
    limit_query_param = 'recipes_limit'
    default_limit = DEFAULT_PAGE_SIZE
