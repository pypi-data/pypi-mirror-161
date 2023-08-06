"""
Created on 2022-04-11
@author:刘飞
@description:发布子模块逻辑处理
"""
import datetime
import logging
import zlib

from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator
from django.db.models import F
from rest_framework import serializers

from ..models import Thread
from ..models import ThreadAuth
from ..models import ThreadCategory
from ..models import ThreadClassify
from ..models import ThreadShow
from ..models import ThreadStatistic
from ..models import ThreadTag
from ..models import ThreadTagMapping
from ..serializers import ThreadAuthListSerializer
from ..serializers import ThreadCategoryListSerializer
from ..serializers import ThreadClassifyListSerializer
from ..serializers import ThreadDetailSerializer
from ..serializers import ThreadListSerializer
from ..serializers import ThreadShowListSerializer
from ..serializers import ThreadTagSerializer

log = logging.getLogger()


class ThreadServices:
    def __init__(self):
        pass

    @staticmethod
    def thread_show(request):
        """
        展示类型。用于对前端界面的显示样式进行分类
        """
        thread_show_obj = ThreadShow.objects.all()
        res = ThreadShowListSerializer(thread_show_obj, many=True)
        return res.data, None

    @staticmethod
    def thread_classify(request):
        """
        分类。具体的分类，可以是按行业、兴趣、学科的分类，是主类别下的子分类。
        """
        category_value = request.query_params.get('category_value', None)
        thread_classify_obj = ThreadClassify.objects.all()
        if category_value:
            thread_classify_obj = thread_classify_obj.filter(category_id__value=category_value)
        res = ThreadClassifyListSerializer(thread_classify_obj, many=True)
        return res.data, None

    @staticmethod
    def thread_category(request):
        """
        类别。类似于版块大类的概念，用于圈定信息内容所属的主要类别
        """
        thread_category_obj = ThreadCategory.objects.all()
        res = ThreadCategoryListSerializer(thread_category_obj, many=True)
        return res.data, None

    @staticmethod
    def thread_auth(request):
        """
        访问权限。作者指定允许哪里用户可以访问，例如私有、公开、好友、指定某些人可以访问等。
        """

        thread_auth_obj = ThreadAuth.objects.all()
        res = ThreadAuthListSerializer(thread_auth_obj, many=True)
        return res.data, None

    @staticmethod
    def thread_tag(request):
        """
        标签类型，存放预置标签。
        """
        size = request.query_params.get('size', 10)
        page = request.query_params.get('page', 1)
        thread_tag_obj = ThreadTag.objects.all()
        paginator = Paginator(thread_tag_obj, size)
        try:
            thread_tag_obj = paginator.page(page)
        except PageNotAnInteger:
            thread_tag_obj = paginator.page(1)
        except EmptyPage:
            thread_tag_obj = paginator.page(paginator.num_pages)
        except Exception as e:
            log.error(f'信息主表分页:{str(e)}')
            raise serializers.ValidationError(str(e))
        res = ThreadTagSerializer(thread_tag_obj, many=True)
        data = {'total': paginator.count, 'list': res.data}
        return data, None

    @staticmethod
    def thread_list_read(request):
        """
        信息主表列表读取
        """
        size = request.query_params.get('size', 10)
        page = request.query_params.get('page', 1)
        # category_id = request.query_params.get('category_id')
        category_value = request.query_params.get('category_value')
        classify_id = request.query_params.get('classify_id')
        classify_value = request.query_params.get('classify_value')
        title = request.query_params.get('title')
        content = request.query_params.get('content')
        tag_list = request.query_params.get('tag_list')  # 列表[1,2,3,4]
        tags = request.query_params.get('tags')  # 列表['同城', '圣诞节']查询不用这个
        start_time = request.query_params.get('start_time')
        end_time = request.query_params.get('end_time')
        user_id = request.query_params.get('user_id')
        is_deleted = False
        # 时间格式验证
        try:
            if start_time:
                datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            if end_time:
                datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise serializers.ValidationError(f'时间格式错误:它的格式应该是YYYY-MM-DD HH:MM:SS')
        # 边界检查，不写这行，当size为0时，页面会报分母不能为零
        if int(size) <= 0:
            raise serializers.ValidationError(f'请求每页数量(size)不能为零。')

        keys = 'category_id__value classify_id classify_id__value title__icontains content__icontains create_time__gte create_time__lte is_deleted user_id'.split()
        values = [category_value, classify_id, classify_value, title, content, start_time, end_time, is_deleted,
                  user_id]
        conditions = {k: v for k, v in zip(keys, values) if v or v is False}
        # 根据是否朋友圈预查询出所有[除了朋友圈，其他打乱顺序随机返回]
        if category_value and category_value == 'moment':
            thread_obj = Thread.objects.all()
        else:
            thread_obj = Thread.objects.all().order_by('?')
        # 这里先处理标签查询
        if tag_list:
            try:
                thread_id_list = ThreadTagMapping.objects.filter(tag_id__in=tag_list.split(',')).values_list(
                    'thread_id', flat=True)
                thread_obj = thread_obj.filter(id__in=thread_id_list)
            except ValueError as e:
                log.error(f'信息表标签查询{e}')
                pass

        thread_main_obj = thread_obj.filter(**conditions)
        paginator = Paginator(thread_main_obj, size)

        try:
            thread_main_obj = paginator.page(page)
        except PageNotAnInteger:
            thread_main_obj = paginator.page(1)
        except EmptyPage:
            thread_main_obj = paginator.page(paginator.num_pages)
        except Exception as e:
            log.error(f'信息主表分页:{str(e)}')
            raise serializers.ValidationError(str(e))
        res = ThreadListSerializer(thread_main_obj, many=True)
        data = {'total': paginator.count, 'list': res.data}
        return data, None

    @staticmethod
    def thread_list_create(request):
        """
        信息表新增
        """
        serializer = ThreadListSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            raise serializers.ValidationError(serializer.errors)
        res = serializer.save()  # 这个返回的是对象，后续处理使用

        # 信息统计表创建一条数据
        ThreadStatistic.objects.create(thread_id=res)

        # 处理信息标签
        tag_list = request.data.get('tag_list', [])
        tags = request.data.get('tags', [])
        for t_id in tag_list:
            t_obj = ThreadTag.objects.filter(id=t_id).first()
            if t_obj:
                conditions = {'thread_id': res, 'tag_id': t_obj}
                ThreadTagMapping.objects.create(**conditions)
        for t_value in tags:
            t_obj = ThreadTag.objects.filter(value=t_value).first()
            if not t_obj:
                t_obj = ThreadTag.objects.create(value=t_value)
            conditions = {'thread_id': res, 'tag_id': t_obj}
            ThreadTagMapping.objects.create(**conditions)
        return None, None

    @staticmethod
    def thread_info_update(request, pk):
        thread_obj = Thread.objects.filter(id=pk, is_deleted=False).first()
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # 获取到更新前的数据
        old_data_list = [thread_obj.is_deleted,
                         thread_obj.category_id,
                         thread_obj.classify_id,
                         thread_obj.show_id,
                         thread_obj.user_id,
                         thread_obj.auth_id,
                         thread_obj.title,
                         thread_obj.content,
                         thread_obj.has_enroll,
                         thread_obj.has_fee,
                         thread_obj.has_comment,
                         thread_obj.cover,
                         thread_obj.video,
                         thread_obj.photos,
                         thread_obj.files]

        # 更新数据
        serializer = ThreadDetailSerializer(thread_obj, data=request.data)
        if not serializer.is_valid(raise_exception=True):
            raise serializers.ValidationError(serializer.errors)
        res = serializer.save()  # 这个返回的是对象，后续处理使用

        # 处理信息标签
        ThreadTagMapping.objects.filter(thread_id=res).delete()  # 先删除掉原有关联
        tag_list = request.data.get('tag_list', [])
        tags = request.data.get('tags', [])
        for t_id in tag_list:
            t_obj = ThreadTag.objects.filter(id=t_id).first()
            if t_obj:
                conditions = {'thread_id': res, 'tag_id': t_obj}
                ThreadTagMapping.objects.create(**conditions)
        for t_value in tags:
            t_obj = ThreadTag.objects.filter(value=t_value).first()
            if not t_obj:
                t_obj = ThreadTag.objects.create(value=t_value)
            conditions = {'thread_id': res, 'tag_id': t_obj}
            ThreadTagMapping.objects.create(**conditions)

        # 更新成功记录日志
        # 获取更新后数据集
        new_data_list = [res.is_deleted,
                         res.category_id,
                         res.classify_id,
                         res.show_id,
                         res.user_id,
                         res.auth_id,
                         res.title,
                         res.content,
                         res.has_enroll,
                         res.has_fee,
                         res.has_comment,
                         res.cover,
                         res.video,
                         res.photos,
                         res.files]
        logs = thread_obj.logs if thread_obj.logs else []
        update_data = {"update_time": now}
        keys = ['is_deleted', 'category_id', 'classify_id', 'show_id', 'user_id', 'auth_id', 'title', 'content',
                'has_enroll', 'has_fee', 'has_comment', 'cover', 'video', 'photos', 'files']
        for k, o, n in zip(keys, old_data_list, new_data_list):
            if zlib.crc32(str(o).encode('utf8')) != zlib.crc32(str(n).encode('utf8')):
                update_data[k] = {"before": o, "after": n}
        # logs = [{"update_time": "2022-05-05 16:02:00", "title": {"before": "修改前", "after": "修改后"}}]
        logs.append(update_data)
        # Thread.objects.filter(id=res.id).update(logs=logs)
        res.logs = logs
        res.save()
        return None, None

    @staticmethod
    def thread_main_info(request, pk):
        thread_obj = Thread.objects.filter(id=pk, is_deleted=False).first()
        # 信息统计表更新数据
        ThreadStatistic.objects.filter(thread_id=thread_obj).update(views=F('views') + 1)
        res = ThreadDetailSerializer(thread_obj)
        return res.data, None

    @staticmethod
    def thread_main_delete(request, pk):
        thread_obj = Thread.objects.filter(id=pk, is_deleted=False).first()
        thread_obj.is_deleted = True
        thread_obj.save()
        return None, None

    # 已拆分上面三个子方法
    # @staticmethod
    # def thread_main_detail(request, pk):
    #     thread_obj = Thread.objects.filter(id=pk, is_deleted=False).first()
    #     if not thread_obj:
    #         raise serializers.ValidationError('资源不存在')
    #     if request.method == 'GET':
    #         # 信息统计表更新数据
    #         ThreadStatistic.objects.filter(thread_id=thread_obj).update(views=F('views') + 1)
    #         res = ThreadDetailSerializer(thread_obj)
    #         return res.data, None
    #     elif request.method == 'PUT':
    #         now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #         # 获取到更新前的数据
    #         old_data_list = [thread_obj.is_deleted,
    #                          thread_obj.category_id,
    #                          thread_obj.classify_id,
    #                          thread_obj.show_id,
    #                          thread_obj.user_id,
    #                          thread_obj.auth_id,
    #                          thread_obj.title,
    #                          thread_obj.content,
    #                          thread_obj.has_enroll,
    #                          thread_obj.has_fee,
    #                          thread_obj.has_comment,
    #                          thread_obj.cover,
    #                          thread_obj.video,
    #                          thread_obj.photos,
    #                          thread_obj.files]
    #
    #         # 更新数据
    #         serializer = ThreadDetailSerializer(thread_obj, data=request.data)
    #         if not serializer.is_valid(raise_exception=True):
    #             raise serializers.ValidationError(serializer.errors)
    #         res = serializer.save()  # 这个返回的是对象，后续处理使用
    #
    #         # 处理信息标签
    #         ThreadTagMapping.objects.filter(thread_id=res).delete()  # 先删除掉原有关联
    #         tag_list = request.data.get('tag_list', [])
    #         tags = request.data.get('tags', [])
    #         for t_id in tag_list:
    #             t_obj = ThreadTag.objects.filter(id=t_id).first()
    #             if t_obj:
    #                 conditions = {'thread_id': res, 'tag_id': t_obj}
    #                 ThreadTagMapping.objects.create(**conditions)
    #         for t_value in tags:
    #             t_obj = ThreadTag.objects.filter(value=t_value).first()
    #             if not t_obj:
    #                 t_obj = ThreadTag.objects.create(value=t_value)
    #             conditions = {'thread_id': res, 'tag_id': t_obj}
    #             ThreadTagMapping.objects.create(**conditions)
    #
    #         # 更新成功记录日志
    #         # 获取更新后数据集
    #         new_data_list = [res.is_deleted,
    #                          res.category_id,
    #                          res.classify_id,
    #                          res.show_id,
    #                          res.user_id,
    #                          res.auth_id,
    #                          res.title,
    #                          res.content,
    #                          res.has_enroll,
    #                          res.has_fee,
    #                          res.has_comment,
    #                          res.cover,
    #                          res.video,
    #                          res.photos,
    #                          res.files]
    #         logs = thread_obj.logs if thread_obj.logs else []
    #         update_data = {"update_time": now}
    #         keys = ['is_deleted', 'category_id', 'classify_id', 'show_id', 'user_id', 'auth_id', 'title', 'content',
    #                 'has_enroll', 'has_fee', 'has_comment', 'cover', 'video', 'photos', 'files']
    #         for k, o, n in zip(keys, old_data_list, new_data_list):
    #             if zlib.crc32(str(o).encode('utf8')) != zlib.crc32(str(n).encode('utf8')):
    #                 update_data[k] = {"before": o, "after": n}
    #         # logs = [{"update_time": "2022-05-05 16:02:00", "title": {"before": "修改前", "after": "修改后"}}]
    #         logs.append(update_data)
    #         # Thread.objects.filter(id=res.id).update(logs=logs)
    #         res.logs = logs
    #         res.save()
    #         return None, None
    #     elif request.method == 'DELETE':
    #         thread_obj.is_deleted = True
    #         thread_obj.save()
    #         return None, None
