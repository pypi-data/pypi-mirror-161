# encoding: utf-8
"""
@project: djangoModel->user_list
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 用户信息列表
@created_time: 2022/7/25 9:42
"""
from rest_framework.views import APIView

from ..services.user_service import UserService


class UserListAPIView(APIView):
    def get(self, request):
        return UserService.user_list(request, UserService.hjp_user_right_call)
