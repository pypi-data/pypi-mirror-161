"""
Created on 2022-05-20
@author:刘飞
@description:用户验证装饰器，为单个请求方式做验证
"""
from rest_framework import exceptions
from xj_user.services.user_service import UserService


def authentication_wrapper(func):
    def inner(*args, **kwargs):
        request = args[1]
        token = request.headers.get('Authorization', None)
        user, error_text = UserService.check_token(token)
        if error_text:
            raise exceptions.AuthenticationFailed(error_text)

        request.user = user
        response = func(*args, **kwargs)
        return response

    return inner
