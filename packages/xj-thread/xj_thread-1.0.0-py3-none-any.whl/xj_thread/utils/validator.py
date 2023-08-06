# encoding: utf-8
"""
@project: hydrology-station-python-4.0->validate
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 表单验证基类
@created_time: 2022/5/25 11:43
"""
import json

from django import forms
from django.core.exceptions import ValidationError


class Validate(forms.Form):
    """检验基类，子类编写规则，调用父类的validate方法"""

    def validate(self):
        """
        request 请求参数验证
        :return {'code': 'err': self.errors}:
        """
        if self.is_valid():
            return True, None
        else:
            error = json.dumps(self.errors)
            error = json.loads(error)
            temp_error = {}
            # 统一展示小写 提示，中文转义回来
            for k, v in error.items():
                temp_error[k.lower()] = v[0]
            return False, temp_error


class Rule:
    """表单验证规则"""

    @staticmethod
    def credit_code(code):
        """企业信用编码"""
        re_patt = "/^[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}$/"
        res = code.match(re_patt)
        if not res:
            raise ValidationError('不是合理有效的企业信用编码')

    @staticmethod
    def chinese_name(code):
        """中文名字"""
        re_patt = "/^(?:[\u4e00-\u9fa5·]{2,16})$/"
        res = code.match(re_patt)
        if not res:
            raise ValidationError('不是合理有效的中文名字')

    @staticmethod
    def plate_number(code):
        """车牌号"""
        re_patt = "/^[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领][A-HJ-NP-Z](?:((\d{5}[A-HJK])|([A-HJK][A-HJ-NP-Z0-9][0-9]{4}))|[A-HJ-NP-Z0-9]{4}[A-HJ-NP-Z0-9挂学警港澳])$/"
        res = code.match(re_patt)
        if not res:
            raise ValidationError('不是合理有效的 车牌号')

    @staticmethod
    def id_card(code):
        """身份证号"""
        re_patt = "/^[1-9]\d{7}(?:0\d|10|11|12)(?:0[1-9]|[1-2][\d]|30|31)\d{3}$/"
        res = code.match(re_patt)
        if not res:
            raise ValidationError('不是合理有效的 身份证号')


# 案例使用自定义验证方法
def log_unit_id(value):
    res = True
    if not res:
        raise ValidationError('unit_id不存在')


class ExampleValidate(Validate):
    """验证查询表单"""
    region_code = forms.CharField(
        required=True,
        error_messages={
            "required": "行政编码 必填",
        })
    unit_id = forms.IntegerField(  # 自定义方法
        validators=[log_unit_id],
    )
