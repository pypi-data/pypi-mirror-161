# encoding: utf-8
"""
@project: djangoModel->thread_v2
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis:
@created_time: 2022/7/29 15:11
"""

from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse

from ..validator import ThreadInsertValidator
from .extend_service import InputExtend
from .extend_service import serializers_to_list
from ..models import Thread
from ..models import ThreadExtendData
from ..models import ThreadExtendField
from ..models import ThreadStatistic
from ..serializers import ThreadV2ListSerializer
from ..utils.custom_response import util_response
from ..utils.model_handle import parse_data
from ..utils.model_handle import parse_model


# 信息服务CURD(支持扩展字段配置)  V2版本
class ThreadNewServices:
    @staticmethod
    def create(request):
        form_data = parse_data(request)
        # 数据有效行判断（验证器）
        validator = ThreadInsertValidator(form_data)
        is_pass, error = validator.validate()
        if not is_pass:
            return util_response(err=4022, msg=error)
        # 扩展字段与主表字段拆分
        extend_service = InputExtend(form_data)
        form_data, extend_form_data = extend_service.transform_param()
        # 开启事务，防止脏数据 TODO 在这之前可以验证一下有效性
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                if extend_form_data:
                    extend_obj = ThreadExtendData.objects.create(**extend_form_data)
                    form_data['extend_id'] = extend_obj.id
                Thread.objects.create(**form_data)
                transaction.savepoint_commit(save_id)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return util_response(err=55447, msg=str(e))
        return util_response()

    @staticmethod
    def update(request):
        form_data = parse_data(request=request, except_field=['extend_id'])
        id = request.data.get('id', None)
        if id is None:
            return util_response(msg="ID 不能为空", err=2554)
        extend_service = InputExtend(form_data)
        # 扩展字段与主表字段拆分
        form_data, extend_form_data = extend_service.transform_param()
        # 开启事务，防止脏数据
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                # 主表修改
                main_res = parse_model(Thread.objects.filter(id=form_data['id']))
                if not main_res:
                    return util_response(err=5547, msg="数据不存在，无法进行修改")
                thread_id = form_data['id']
                extend_form_id = main_res[0]["extend"]
                del form_data['id']
                Thread.objects.filter(id=thread_id).update(**form_data)
                # 扩展表修改
                if extend_form_id:
                    extend_res = ThreadExtendData.objects.filter(id=extend_form_id)
                    if extend_res:
                        extend_res.update(**extend_form_data)
                transaction.savepoint_commit(save_id)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return util_response(err=75447, msg=str(e))
        return util_response()

    @staticmethod
    def delete(id):
        main_res = Thread.objects.filter(id=id)
        if not main_res:
            return util_response(err=5547, msg="数据不存在，无法进行修改")
        main_res.update(is_deleted=1)
        return util_response()

    @staticmethod
    def select(request):
        page = request.GET.get('page', 1)
        limit = request.GET.get('limit', 20)
        if int(limit) > 100:
            return util_response(msg='每一页不可以超过200条', err=40225)
        params = parse_data(request)
        params['is_deleted'] = 0
        if 'page' in params.keys():
            del params['page']
        if 'limit' in params.keys():
            del params['limit']
        try:
            list_set = Thread.objects.filter(**params)
            count = Thread.objects.filter(**params).count()
        except Exception as e:
            return util_response(err=7557, msg=e.__str__())
        # 分页数据
        page_set = ThreadV2ListSerializer(data=Paginator(list_set, limit).get_page(page), many=True)
        if page_set.is_valid(): pass
        res = final_res = serializers_to_list(page_set.data)
        # 扩展字段替换
        for index, item in enumerate(res):
            if item['extend']:
                filed = parse_model(ThreadExtendField.objects.filter(classify_id=item['classify_id']))
                if filed:  # 找不到 扩展字段映射配置时候
                    filed = {item['extend_field']: item['field'] for item in filed}
                    for k, v in item['extend_child'].items():
                        if v and not k == "id":
                            final_res[index][filed[k]] = v
            del final_res[index]['extend_child']
            del final_res[index]['extend']
        return util_response(data={'data': final_res, 'limit': int(limit), 'page': int(page), 'count': count})

    @staticmethod
    def select_extend(id):
        """单独查询 查询扩展字段"""
        return util_response(parse_model(ThreadExtendData.objects.filter(id=id)))

    @staticmethod
    def select_detail(request):
        """获取信息内容"""
        id = request.GET.get('id')
        if id is None:
            return JsonResponse({'err': 40225, 'msg': '参数错误', 'data': ''})
        res = parse_model(Thread.objects.filter(id=id).values('title', 'content', 'summary', 'cover', 'create_time'))
        # 查看计数自增1
        if res:
            StatisticsService.increment(thread_id=id, tag="views", step=1, use_in_service=True)
        return util_response(data=res)


# 统计服务
class StatisticsService:
    @staticmethod
    def increment(thread_id, tag, step=1, use_in_service=False):
        """
        增量计数
        :param thread_id:
        :param tag: 递增的字段
        :param step:  递增的步长
        :param use_in_service: 是否使用在服务中
        :return: （err, data） 或者 util_response({'err': err, 'msg': msg, 'data': data})
        """
        query_obj = ThreadStatistic.objects.filter(thread_id=thread_id)
        match_data = query_obj.first()
        if match_data:
            form = {tag + "": getattr(match_data, tag) + int(step)}
            query_obj.update(**form)
        else:
            form = {"thread_id_id": thread_id, tag: step}
            print(form)
            ThreadStatistic.objects.create(**form)
        return StatisticsService.response(use_in_service)

    @staticmethod
    def increments(thread_id, increment_dict, use_in_service=False):
        """
        批量计数增量统计
        :param thread_id:  关联主键
        :param increment_dict: {递增字段：递增的值}
        :param use_in_service: 是：否用在服务，是返回服务协议，否：返回响应对象
        :return:（err, data） 或者 util_response({'err': err, 'msg': msg, 'data': data})
        """
        is_set_thread = Thread.objects.filter(id=thread_id)
        if not is_set_thread:
            return StatisticsService.response(use_in_service=use_in_service, err=4588, msg='不存该条信息')
        # 事务回滚
        with transaction.atomic():
            sid = transaction.savepoint()
            try:
                for k, v in increment_dict.items():
                    StatisticsService.increment(thread_id, k, v, use_in_service)
                return StatisticsService.response(use_in_service=use_in_service)
            except Exception as e:
                transaction.savepoint_rollback(sid)
                return StatisticsService.response(use_in_service=use_in_service, err=2455, msg=str(e))

    # 返回格式化
    @staticmethod
    def response(use_in_service, err=0, msg="", data=None):
        if not use_in_service:
            return util_response({'err': err, 'msg': msg, 'data': data})
        else:
            if not err == 0:
                err = msg
            return err, data
