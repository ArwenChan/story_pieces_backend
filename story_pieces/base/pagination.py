from rest_framework import pagination
from rest_framework.response import Response


class CustomPagination(pagination.PageNumberPagination):
    page_size_query_param = 'size'

    def get_paginated_response(self, data):
        return Response({
            'error_code': '0',
            'error_message': '',
            'result': {
                'count': self.page.paginator.count,
                'data': data
            }
        })