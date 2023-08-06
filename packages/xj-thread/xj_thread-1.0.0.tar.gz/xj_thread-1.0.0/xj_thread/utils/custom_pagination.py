"""
Created on 2022-01-17
@auth:刘飞
@description:自定义分页
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class MyPageNumberPagination(PageNumberPagination):
    page_size = 10  # 数字，页面显示的记录条数，不设置的就默认setting配置的全局PAGE_SIZE值
    page_size_query_param = 'size'  # 字符串，请求设置页面大小的参数名称，默认是None
    max_page_size = 10000  # 最大允许请求的页面大小，仅在page_size_query_param被设置时有效

    def get_paginated_response(self, data):
        return Response({
            'total': self.page.paginator.count,
            # 'list': add_order(data),
            'list': data,
        })


def add_order(lst):
    for i, j in enumerate(lst):
        j['order'] = i + 1
    return lst
