# encoding: utf-8
"""
@project: djangoModel->extend_service
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 扩展服务
@created_time: 2022/7/29 15:14
"""

from ..models import ThreadExtendField, Thread
from ..utils.model_handle import *


class InputExtend:
    thread_extend_filed = None

    def __init__(self, form_data, need_all_field=False):
        """
        :param form_data: 表单
        :param need_all_field: 是否需要全部的扩展字段（查询的时候会用到）
        """
        self.form_data = form_data
        classify_id = self.form_data.get('classify_id', None)
        category_id = self.form_data.get('category_id', None)
        if classify_id:
            self.form_data['classify_id_id'] = self.form_data['classify_id']
            del self.form_data['classify_id']

        if category_id:
            form_data['category_id_id'] = form_data['category_id']
            del form_data['category_id']

        if need_all_field:  # 查询时候
            self.thread_extend_filed = parse_model(ThreadExtendField.objects.all())
            self.thread_extend_filed = {item["field"]: item["extend_field"] for item in self.thread_extend_filed}
        else:  # 新增或者修改的时候
            if "id" in self.form_data.keys():  # 修改时候：传了id,没有传classify_id
                thread = parse_model(Thread.objects.filter(id=self.form_data['id']))
                try:
                    classify_id = thread[0]['classify_id']
                    self.thread_extend_filed = parse_model(ThreadExtendField.objects.filter(classify_id=classify_id))
                    self.thread_extend_filed = {item["field"]: item["extend_field"] for item in self.thread_extend_filed}
                    # 适配外键
                except Exception as e:
                    # 新闻ID不存在，或者没有绑定classfiy_id
                    pass
            if classify_id:  # 新增时候：通过分类classify_id匹配扩展字段
                self.thread_extend_filed = parse_model(ThreadExtendField.objects.filter(classify_id=classify_id))
                self.thread_extend_filed = {item["field"]: item["extend_field"] for item in self.thread_extend_filed}

    # 请求参数转换
    def transform_param(self):
        # 没有定义扩展映射直接返回，不进行扩展操作
        if self.thread_extend_filed is None:
            return self.form_data, None
        # 遍历取出扩展字段
        extend_param = {}
        form_data = json.loads(json.dumps(self.form_data))
        for k, v in self.form_data.items():
            if k in self.thread_extend_filed:
                extend_param[self.thread_extend_filed[k]] = v
                del form_data[k]
        return form_data, extend_param
