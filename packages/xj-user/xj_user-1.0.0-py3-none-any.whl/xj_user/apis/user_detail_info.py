# encoding: utf-8
"""
@project: djangoModel->user_detail_info
@author: 孙楷炎
@synopsis: 用户详细信息操作
@created_time: 2022/6/27 19:42
"""
from rest_framework.views import APIView

from ..services.user_detail_info_service import DetailInfoService


# 列表
class getInfoList(APIView):
    def get(self, request):
        return DetailInfoService.get_info_list(request)


# 小程序用户调用
class getOwnInfo(APIView):
    def get(self, request):
        return DetailInfoService.get_own_info(request)


class createInfo(APIView):
    def post(self, request):
        return DetailInfoService.create_detail_info(request)


class editInfo(APIView):
    def post(self, request):
        return DetailInfoService.update_detail_info(request)
