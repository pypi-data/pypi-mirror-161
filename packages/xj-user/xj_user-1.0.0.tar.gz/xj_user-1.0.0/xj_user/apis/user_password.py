# _*_coding:utf-8_*_

import os, logging, time, json, copy, re
from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import response
from rest_framework import serializers
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.db.models import Q
from django.db.models import F
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
# from django.conf import settings
from .. import config

import random
import jwt

from ..models import *

logger = logging.getLogger(__name__)


# 用户密码设置
class UserPassword(APIView):
    permission_classes = (AllowAny,)
    model = BaseInfo
    params = None

    def post(self, request, *args, **kwargs):
        # self.params = request.query_params  # 返回QueryDict类型
        self.params = request.data  # 返回QueryDict类型
        # print("> UserPassword:", self.params)

        platform = str(self.params.get('platform', ''))
        account = str(self.params.get('account', ''))
        new_password = str(self.params.get('new_password', ''))
        old_password = str(self.params.get('old_password', ''))
        captcha = str(self.params.get('captcha', ''))

        # 边界检查
        # if not platform:
        #     return Response({'msg': "platform必填", 'err': 2001})

        if not account:
            return Response({'msg': "account必填", 'err': 2002})

        if not new_password:
            return Response({'msg': "new_password必填", 'err': 2003})

        if not old_password and not captcha:
            return Response({'msg': "old_password或captcha必填", 'err': 2004})

        # 检查平台是否存在
        if platform:
            try:
                platform_id = Platform.objects.get(platform_name__iexact=platform).platform_id
            except Platform.DoesNotExist:
                return Response({'msg': "platform不存在平台名称" + platform, 'err': 2005})

        # 账号类型判断
        if re.match(r'(^1[356789]\d{9}$)|(^\+?[78]\d{10}$)', account):
            account_type = 'phone'
            account_type_str = '手机'
        elif re.match(r'^\w+[\w\.\-\_]*@\w+[\.\w]*\.\w{2,}$', account):
            account_type = 'email'
            account_type_str = '邮箱'
        elif re.match(r'^[A-z\u4E00-\u9FA5]+\w*$', account):
            account_type = 'username'
            account_type_str = '用户名'
        else:
            return Response({'msg': "账号必须是用户名、手机或者邮箱，用户名不能是数字开头", 'err': 2006})

        # 判断账号是否存在。注：t-前辍代表类型为实例
        try:
            if account_type == 'phone':
                # t_user = BaseInfo.objects.get(phone=account, platform_id=platform_id)
                t_user = BaseInfo.objects.get(phone=account)
            elif account_type == 'email':
                # t_user = BaseInfo.objects.get(email=account, platform_id=platform_id)
                t_user = BaseInfo.objects.get(email=account)
            elif account_type == 'username':
                # t_user = BaseInfo.objects.get(user_name=account, platform_id=platform_id)
                t_user = BaseInfo.objects.get(user_name=account)
            else:
                t_user = None
        except Platform.DoesNotExist:
            return Response({'msg': account_type_str+"不存在" + account, 'err': 2007})

        # 如果有旧密码则先判断旧密码是否正确
        if old_password:
            # 先判断有没有历史密码
            t_auth = Auth.objects.filter(user_id=t_user.id, password__isnull=False).order_by('-update_time').first()
            if not t_auth:
                return Response({'msg': "账号尚未设置密码："+str(t_user.id), 'err': 2006})
            # 判断密码不正确
            if not check_password(old_password, t_auth.password):
                return Response({'msg': "旧密码错误", 'err': 2014})


        # todo 检查检证码是否正确
        # if captcha and Auth.objects.filter(user_id=t_user.id).count():

        new_auth = Auth.objects.create(
            user_id=t_user.id,
            password=make_password(new_password, None, 'pbkdf2_sha1'),
            plaintext=new_password,
            token=jwt.encode({'account': account}, config.JWT_AUTH['JWT_SECRET_KEY']),
        )
        headers = {
            "Authorization": new_auth.token,
        }

        return Response(data={
            'err': 0,
            'msg': '修改密码成功',
            'data': {
                "user_id": new_auth.user_id,
            },
        }, status=None, template_name=None, headers=headers, content_type=None)


class MyApiError(Exception):
    def __init__(self, message, err_code=4010):
        self.msg = message
        self.err = err_code

    def __str__(self):
        # repr()将对象转化为供解释器读取的形式。可省略
        return repr(self.msg)