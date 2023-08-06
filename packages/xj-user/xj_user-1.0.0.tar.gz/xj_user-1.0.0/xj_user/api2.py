# _*_coding:utf-8_*_

import os, logging, time, json, copy
from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import response
from rest_framework import serializers
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.db.models import Q
from django.db.models import F

from .models import *

logger = logging.getLogger(__name__)


def make_code():
    now = datetime.now()
    date_str = now.strftime('%Y%m%d')
    time_str: str = str(time.time())[5:10]
    ms_str = str(now)[-6:-3]
    code = '%s%s%s' % (date_str, time_str, ms_str)
    return code


# 获取用户信息
class UserLogin(APIView):  # 或继承APIView UpdateAPIView
    permission_classes = (AllowAny,)
    model = BaseInfo
    queryset = BaseInfo.objects.all()
    params = None

    def get(self, request, *args, **kwargs):
        self.params = request.query_params  # 返回QueryDict类型

        if 'account' not in self.params or self.params['account'].isspace():
            return Response({'err': 1001, 'msg': '缺少account', })
            # raise MyApiError("缺少account")
        if 'password' not in self.params or self.params['password'].isspace():
            return Response({'err': 1002, 'msg': '缺少password', })

        result = self.queryset.filter(Q(id=self.params['account']))
        response_data = result.values(
            'platform_uid',
            'platform',
            'user_name',
            'full_name',
            'phone',
            'email',
            'wechat',
            'user_info'
        )

        res = {
            'err': 0,
            'msg': 'OK',
            'data': response_data,
            'request': self.params,
            # 'serializer': serializer.data,
        }

        # try:

            # return super(UserLogin, self).patch(request, *args, **kwargs)
        #
        # except SyntaxError:
        #     print(">SyntaxError:")
        #     res = {
        #         'err': 4001,
        #         'msg': '语法错误'
        #     }
        # except LookupError:
        #     res = {
        #         'err': 4002,
        #         'msg': '无效数据查询'
        #     }
        # # 这里 result是一个类的对象，要用result.属性名来返回
        # except Exception as valueError:
        #     print('>Exception:', valueError)
        #     res = {
        #         'err': 4003,
        #         'msg': valueError.args
        #
        #     }
        # except:
        #     res = {
        #         'err': 4009,
        #         'msg': '未知错误'
        #     }

        return response.Response(res)


class UserInfoSerializer(serializers. ModelSerializer):
    class Meta:
        model = BaseInfo
        exclude = ['user_name', 'full_name',]


class UserInfo(generics.UpdateAPIView):  # 或继承(APIView)
    queryset = BaseInfo.objects.all()
    permission_classes = (AllowAny,)  # 允许所有用户 (IsAuthenticated,IsStaffOrBureau)
    serializer_class = UserInfoSerializer
    params = None

    def get(self, request, *args, **kwargs):
        self.params = request.query_params  # 返回QueryDict类型

        if 'uid' not in self.params or self.params['uid'].isspace():
            return Response({'err': 0, 'msg': '缺少uid', 'data': [], 'request': self.params, })

        base_info = BaseInfo.objects.all().filter(Q(id=self.params['uid']))
        data = base_info.values(
            'platform_uid',
            'platform',
            'user_name',
            'full_name',
            'phone',
            'email',
            'wechat',
            'user_info'
        )

        return Response({
            'err': 0,
            'msg': 'OK',
            'data': data,
            'request': self.params,
            # 'serializer': serializer.data,
        })
        # return super(UserLogin, self).patch(request, *args, **kwargs)


class MyApiError(Exception):
    def __init__(self, message):
        self.msg = message

    def __str__(self):
        # repr()将对象转化为供解释器读取的形式。可省略
        return repr(self.msg)