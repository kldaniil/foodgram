from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)

DEFAULT_PAGE_SIZE = 6


class CustomPagination(PageNumberPagination):
    '''Кастомная пагинация для API.'''
    page_size_query_param = 'limit'
    page_size = DEFAULT_PAGE_SIZE


class SubscriptionsPagination(LimitOffsetPagination):
    '''Пагинация для подписок.'''
    limit_query_param = 'recipes_limit'
    default_limit = DEFAULT_PAGE_SIZE
