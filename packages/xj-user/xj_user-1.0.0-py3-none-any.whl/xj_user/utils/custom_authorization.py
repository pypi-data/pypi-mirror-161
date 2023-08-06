"""
Created on 2022-01-19
@auth:刘飞
@description:自定义用户验证
"""

# import jwt
# from django.conf import settings
from rest_framework import authentication
# from apps.xj_user.models import BaseInfo
from rest_framework import exceptions
from ..services.user_service import UserService


class CustomAuthentication(authentication.BaseAuthentication):
    """用户认证"""

    def authenticate(self, request):
        # 验证是否已经登录，函数名必须为：authenticate
        # print("> Authentication: token:", request._request)
        token = request._request.headers.get('Authorization', None)
        # print("> Authentication: token:", token)

        user, error_text = UserService.check_token(token)
        # print("> check_token_server:", xj_user, error_text)

        if error_text:
            raise exceptions.AuthenticationFailed(error_text)

        return user, None

    def authenticate_header(self, request):
        # 这个函数可以没有内容，但是必须要有这个函数
        pass
