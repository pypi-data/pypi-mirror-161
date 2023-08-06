# _*_coding:utf-8_*_

import os, logging, time, json, copy
import re
from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import response
from rest_framework import serializers
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.db.models import Q
from django.db.models import F

from ..models import *

logger = logging.getLogger(__name__)


class UserInfoSerializer(serializers.ModelSerializer):
    # 方法一：使用SerializerMethodField，并写出get_platform, 让其返回你要显示的对象就行了
    # p.s.SerializerMethodField在model字段显示中很有用。
    # platform = serializers.SerializerMethodField()

    # # 方法二：增加一个序列化的字段platform_name用来专门显示品牌的name。当前前端的表格columns里对应的’platform’列要改成’platform_name’
    user_id = serializers.ReadOnlyField(source='id')

    # platform_id = serializers.ReadOnlyField(source='platform.platform_id')
    # platform_name = serializers.ReadOnlyField(source='platform.platform_name')

    class Meta:
        model = BaseInfo
        fields = [
            'user_id',
            # 'platform',
            # 'platform_uid',
            # 'platform__platform_name',
            # 'platform_id',
            # 'platform_name',
            'user_name',
            'full_name',
            'phone',
            'email',
            'wechat',
            'user_info',
        ]
        # exclude = ['platform_uid']

    # 这里是调用了platform这个字段拼成了get_platform
    def get_platform(self, obj):
        return obj.platform.platform_name
        # return {
        #     'id': obj.platform.platform_id,
        #     'name': obj.platform.platform_name,
        # }


# 获取用户信息
class UserEdit(generics.UpdateAPIView):  # 或继承(APIView)
    permission_classes = (AllowAny,)  # 允许所有用户 (IsAuthenticated,IsStaffOrBureau)
    serializer_class = UserInfoSerializer
    params = None

    def post(self, request, *args, **kwargs):
        # self.params = request.query_params.copy()  # 返回QueryDict类型
        self.params = request.data.copy()  # 返回QueryDict类型
        # print("> params:", self.params)
        # print("> params: user_info:", self.params.get('user_info', ''))
        # print("> params: user_info:", type(self.params.get('user_info', '')))

        try:
            token = self.request.META.get('HTTP_AUTHORIZATION', '')
            if re.match(r'Bearer (.*)', token):
                token = re.match(r'Bearer (.*)', token).group(1)
            # print("> token:", token)

            if not token:
                raise MyApiError('缺少Token', 3001)

            # 判断token是否失效
            t_auth = Auth.objects.filter(token=token).order_by('-update_time').first()
            # print("> t_auth:", t_auth)
            if not t_auth:
                raise MyApiError('token失效', 3002)

            # 如果有用户ID则找到该ID，没有则修改自己的ID
            # print("> self.params['user_id']:", self.params)
            if 'user_id' in self.params:
                user_id = self.params.get('user_id', '')
            else:
                user_id = t_auth.user_id
            # print("> user_id:", user_id)

            t_user = BaseInfo.objects.get(id=user_id)
            # print("> t_user:", t_user)

            # 检查必填项
            # if not self.params.get('platform_uid', ''):
            #     self.params['platform_uid'] = t_user.platform_uid
            if not self.params.get('user_name', ''):
                self.params['user_name'] = t_user.user_name

            serializer = UserInfoSerializer(instance=t_user, data=self.params, )
            if not serializer.is_valid():
                raise MyApiError(serializer.errors, 3003)
            serializer.save()

            res = {
                'err': 0,
                'msg': '修改成功',
            }

        except SyntaxError:
            # print("> SyntaxError:")
            res = {
                'err': 4001,
                'msg': '语法错误'
            }
        except LookupError:
            res = {
                'err': 4002,
                'msg': '无效数据查询'
            }
        # 这里 error是一个类的对象，要用error.属性名来返回
        except Exception as error:
            res = {
                'err': error.err if hasattr(error, 'err') else 4000,  # 发生系统异常时报4000
                'msg': error.msg if hasattr(error, 'msg') else error.args,  # 发生系统异常时捕获error.args
            }
            if not hasattr(error, 'err'):
                res['file'] = error.__traceback__.tb_frame.f_globals["__file__"],  # 发生异常所在的文件
                res['line'] = error.__traceback__.tb_lineno,  # 发生异常所在的行数
        except:
            res = {
                'err': 4999,
                'msg': '未知错误'
            }

        # return super(UserLogin, self).patch(request, *args, **kwargs)
        return response.Response(res)


class MyApiError(Exception):
    def __init__(self, message, err_code=4010):
        self.msg = message
        self.err = err_code

    def __str__(self):
        # repr()将对象转化为供解释器读取的形式。可省略
        return repr(self.msg)
