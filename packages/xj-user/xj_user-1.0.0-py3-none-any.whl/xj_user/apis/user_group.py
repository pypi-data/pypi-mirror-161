# encoding: utf-8
"""
@project: djangoModel->user_group
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 用户分组接口
@created_time: 2022/7/22 14:10
"""
from rest_framework.views import APIView

from ..models import Group
from ..utils.model_handle import *
from ..validator import GroupValidator


class GroupAPIView(APIView):
    def get(self, request):
        return model_select(request, Group)

    def post(self, request):
        return model_create(request, Group, GroupValidator)

    def put(self, request):
        return model_update(request, Group)

    def delete(self, request):
        return model_del(request, Group)
