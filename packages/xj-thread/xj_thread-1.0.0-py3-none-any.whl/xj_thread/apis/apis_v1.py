"""
Created on 2022-04-11
@description:刘飞
@description:发布子模块逻辑分发
"""
from rest_framework.views import APIView
from xj_user.utils.custom_authorization import CustomAuthentication

from ..services.theard_v1 import ThreadServices
from ..utils.custom_authentication_wrapper import authentication_wrapper
from ..utils.custom_response import util_response

t = ThreadServices()


class ShowListAPIView(APIView):
    """
    get:展示类型列表
    """

    authentication_classes = (CustomAuthentication,)

    def get(self, request, *args, **kwargs):
        data, error_text = t.thread_show(request)
        return util_response(data=data)


class ClassifyListAPIView(APIView):
    """
    get:分类列表
    """

    # authentication_classes = (CustomAuthentication,)

    def get(self, request, *args, **kwargs):
        data, error_text = t.thread_classify(request)
        return util_response(data=data)


class CategoryListAPIView(APIView):
    """
    get:类别列表
    """

    # authentication_classes = (CustomAuthentication,)

    def get(self, request, *args, **kwargs):
        data, error_text = t.thread_category(request)
        return util_response(data=data)


class AuthListAPIView(APIView):
    """
    get:访问权限列表
    """

    # authentication_classes = (CustomAuthentication,)

    def get(self, request, *args, **kwargs):
        data, error_text = t.thread_auth(request)
        return util_response(data=data)


class TagListAPIView(APIView):
    """
    get:标签列表
    """

    # authentication_classes = (CustomAuthentication,)

    def get(self, request):
        data, error_text = t.thread_tag(request)
        return util_response(data=data)


class ThreadListAPIView(APIView):
    """
    get: 信息表列表
    post: 信息表新增
    """

    # authentication_classes = (CustomAuthentication,)

    # @authentication_wrapper
    def get(self, request, *args, **kwargs):
        data, error_text = t.thread_list_read(request)
        return util_response(data=data)

    @authentication_wrapper
    def post(self, request, *args, **kwargs):
        request.data['user_id'] = request.user.get('user_id', None)
        data, error_text = t.thread_list_create(request)
        return util_response(data=data)


class ThreadDetailAPIView(APIView):
    """
    get:信息表详情
    put:信息表编辑
    delete:信息表删除【假删除】
    """

    # authentication_classes = (CustomAuthentication,)

    def get(self, request, pk, *args, **kwargs):
        data, error_text = t.thread_main_info(request, pk)
        return util_response(data=data)

    @authentication_wrapper
    def put(self, request, pk, *args, **kwargs):
        request.data['user_id'] = request.user.get('user_id', None)
        data, error_text = t.thread_info_update(request, pk)
        return util_response(data=data)

    @authentication_wrapper
    def delete(self, request, pk, *args, **kwargs):
        data, error_text = t.thread_main_delete(request, pk)
        return util_response(data=data)
