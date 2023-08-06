# encoding: utf-8
"""
@project: djangoModel->api_v2
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 扩展第二版
@created_time: 2022/7/29 15:25
"""
from rest_framework.views import APIView

from ..services.thread_v2 import StatisticsService, ThreadNewServices
from ..utils.custom_authentication_wrapper import authentication_wrapper
from ..utils.model_handle import *


# 计数统计API
class ThreadStaticAPIView(APIView):
    # 单条自增
    def post(self, request):
        thread_id = request.data.get('thread_id', None)
        tag = request.data.get('tag', None)
        step = request.data.get('step', None)
        tag_list = ['step', 'views', 'plays', 'comments', 'likes', 'favorite', 'shares']
        if not thread_id or not tag in tag_list:
            return StatisticsService.response(use_in_service=False, err=2045, msg="参数错误")
        return StatisticsService.increment(thread_id, tag, step)

    # 多字段自增
    def put(self, request):
        thread_id = request.data.get('thread_id', None)
        if not thread_id:
            return StatisticsService.response(use_in_service=False, err=2045, msg="参数错误")
        form_data = parse_data(request)
        del form_data['thread_id']
        return StatisticsService.increments(thread_id, form_data)


# 统计服务V2
class ThreadAPIView(APIView):
    def get(self, request):
        """列表"""
        return ThreadNewServices.select(request)

    def get_extend(self, request):
        """获取单条的扩展信息"""
        id = request.data.get('id', None)
        if id is None:
            return util_response(err=4015, msg="ID必填")
        return ThreadNewServices.select_extend(id)

    def select_detail(self):
        # 查看信息详情
        return ThreadNewServices.select_detail(self)

    @authentication_wrapper
    def post(self, request):
        """新增"""
        return ThreadNewServices.create(request)

    @authentication_wrapper
    def put(self, request):
        """修改"""
        return ThreadNewServices.update(request)

    @authentication_wrapper
    def delete(self, request):
        """删除"""
        thread_id = request.data.get('id', None)
        if not thread_id:
            return util_response(msg="参数错误", err=2045)
        return ThreadNewServices.delete(id=thread_id)
