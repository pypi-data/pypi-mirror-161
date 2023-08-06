"""
Created on 2022-01-19
@auth:刘飞
@description:自定义用户验证
"""

import jwt
from django.conf import settings
from rest_framework import authentication
from rest_framework import exceptions
from xj_user.models import BaseInfo


class Authentication(authentication.BaseAuthentication):
    """用户认证，之后将移植到用户模块"""

    def authenticate(self, request):
        # 验证是否已经登录，函数名必须为：authenticate
        token = request._request.headers.get('Authorization')
        if not token:
            raise exceptions.AuthenticationFailed('用户认证失败！')
        try:
            token = token.split(" ")[-1]
            payload = jwt.decode(token, key=settings.JWT_SECRET_KEY, verify=True, algorithms=["RS256", "HS256"])
            user = BaseInfo.objects.filter(user_name=payload.get('username')).first()
            if not user:
                raise exceptions.AuthenticationFailed('用户认证失败。')
            # 在rest_framework内部会将以下两个元素赋值到request，以供后续使用
            return (user, None)
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('验证信息已过期，请重新获取！')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('无效令牌！')

    def authenticate_header(self, request):
        # 这个函数可以没有内容，但是必须要有这个函数
        pass
