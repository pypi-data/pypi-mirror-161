"""
Created on 2022-04-11
@author:刘飞
@description:发布子模块路由分发
"""
from django.conf.urls import url
from django.urls import re_path

from .apis.apis_v2 import ThreadStaticAPIView
from .apis.apis_v1 import ThreadListAPIView, ThreadDetailAPIView, AuthListAPIView, CategoryListAPIView, ClassifyListAPIView, ShowListAPIView, TagListAPIView
from .apis.apis_v2 import ThreadAPIView

# 应用名称
# app_name = 'thread'

urlpatterns = [
    # v1
    url(r'^list/?$', ThreadListAPIView.as_view(), name='list'),  # 信息列表/新增
    url(r'^list/(?P<pk>\d+)/?$', ThreadDetailAPIView.as_view(), name='detail'),  # 信息详情/编辑/删除
    url(r'^auth_list/?$', AuthListAPIView.as_view(), name='auth_list'),  # 权限列表
    url(r'^category_list/?$', CategoryListAPIView.as_view(), name='category_list'),  # 类别列表
    url(r'^classify_list/?$', ClassifyListAPIView.as_view(), name='classify_list'),  # 分类列表
    url(r'^show_list/?$', ShowListAPIView.as_view(), name='show_list'),  # 展示类型列表
    url(r'^tag_list/?$', TagListAPIView.as_view(), name='tag_list'),  # 展示类型列表

    # V2
    re_path("^v2/list/?$", ThreadAPIView.as_view()),  # 信息 增删改查 接口升级
    re_path(r'^detail/?$', ThreadAPIView.select_detail, name='content'),  # 信息内容
    url(r'^statistic/?$', ThreadStaticAPIView.as_view(), name='tag_list'),  # 计数统计，前端埋点接口
]
