from rest_framework.pagination import PageNumberPagination


class UserPagination(PageNumberPagination):
    """Принимает параметр лимит вместо значения по-умолчанию."""

    page_size_query_param = 'limit'
