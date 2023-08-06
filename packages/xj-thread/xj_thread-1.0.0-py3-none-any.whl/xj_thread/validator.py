# encoding: utf-8
"""
@project: djangoModel->validator
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 验证器
@created_time: 2022/7/29 11:44
"""
from .models import ThreadClassify, ThreadCategory
from .utils.model_handle import parse_model
from .utils.validator import *


def is_set_classify_id(value):
    res = parse_model(ThreadClassify.objects.filter(id=value))
    if not res:
        raise ValidationError('无法匹配到classify_id，请先创建')


def is_set_category_id(value):
    res = parse_model(ThreadCategory.objects.filter(id=value))
    if not res:
        raise ValidationError('无法匹配到category_id，请先创建')


class ThreadInsertValidator(Validate):
    category_id = forms.IntegerField(
        required=True,
        error_messages={
            "required": "category_id 必填",
        },
        validators=[is_set_category_id]
    )

    classify_id = forms.IntegerField(
        required=True,
        error_messages={
            "required": "classify_id 必填",
        },
        validators=[is_set_classify_id]
    )

    title = forms.CharField(
        required=True,
        error_messages={
            "required": "title 必填,请先设置然后进行绑定",
        })

    content = forms.CharField(
        required=True,
        error_messages={
            "required": "content 必填,请先设置然后进行绑定",
        })


class ThreadUpdateValidator(Validate):
    id = forms.IntegerField(
        required=True,
        error_messages={
            "required": "id 必填",
        }
    )
