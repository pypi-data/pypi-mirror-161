# _*_coding:utf-8_*_

import logging

from rest_framework import generics
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ..models import BaseInfo
# from apps.finance.models import *
from ..services.user_service import UserService

logger = logging.getLogger(__name__)


class UserContactBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseInfo
        fields = [
            'id',
            'full_name',
        ]


# 获取平台列表
class UserContactBook(generics.UpdateAPIView):  # 或继承(APIView)
    """ REST framework的APIView实现获取card列表 """
    # authentication_classes = (TokenAuthentication,)  # token认证
    # permission_classes = (IsAuthenticated,)   # IsAuthenticated 仅通过认证的用户
    permission_classes = (AllowAny,)  # 允许所有用户 (IsAuthenticated,IsStaffOrBureau)
    serializer_class = UserContactBookSerializer

    def get(self, request, *args, **kwargs):
        token = self.request.META.get('HTTP_AUTHORIZATION', '')
        if not token:
            return Response({'err': 4001, 'msg': '缺少Token', })

        user_id = UserService.check_token(token)
        if not user_id:
            return Response({'err': 4002, 'msg': 'token验证失败', })

        user_base_info_list = BaseInfo.objects.all()

        serializer = UserContactBookSerializer(user_base_info_list, many=True)
        return Response({
            'err': 0,
            'msg': 'OK',
            'data': serializer.data,
        })
