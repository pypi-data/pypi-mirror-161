"""
Created on 2022-04-12
@author:刘飞
@description:自定义异常捕获
"""
from rest_framework.views import exception_handler
from django.http import JsonResponse


def custom_exception_handler(exc, context):
    """
    自定义异常返回
    """

    response = exception_handler(exc, context)

    def get_data():
        res_dic = ''
        for k in list(response.data.keys()):
            if k != 'detail':
                res_dic = str(k) + ':' + str(response.data[k])
                response.data.pop(k, None)
        return res_dic

    if response is not None:
        if isinstance(response.data, list):  # 兼容serializers
            res = {
                "msg": response.data[0],
                "err": response.status_code,
                "data": {}
            }
            return JsonResponse(res)
        elif isinstance(response.data, dict):  # 兼容serializers, 抛出的ValidationError
            msg = ''
            for _k, _v in zip(response.data.keys(), response.data.values()):
                msg += f"{_k}: {_v[0] if isinstance(_v, list) else _v}"
            res = {
                "msg": msg,
                "err": response.status_code,
                "data": {}
            }
            return JsonResponse(res)
        else:
            response.data['msg'] = response.data.pop('detail') if response.data.get('detail') else get_data()
            response.data['err'] = response.status_code
            response.data['data'] = {}

    return response
