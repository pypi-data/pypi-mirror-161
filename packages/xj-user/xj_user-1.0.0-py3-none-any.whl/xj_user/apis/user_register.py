# _*_coding:utf-8_*_

# import os, logging, time, json, copy
import re
import jwt

# from datetime import datetime, timedelta

from rest_framework.views import APIView
# from django.db.models import Q
# from django.db.models import F
from django.contrib.auth.hashers import make_password
# from django.contrib.auth.hashers import check_password
# from django.conf import settings

# from rest_framework.response import Response
from rest_framework import response
# from rest_framework import serializers
# from rest_framework import generics
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import AllowAny

from .. import config

# import random
from ..models import *

# logger = logging.getLogger(__name__)


# 用户注册
class UserRegister(APIView):
    permission_classes = (AllowAny,)
    model = BaseInfo
    params = None

    def post(self, request, *args, **kwargs):
        # self.params = request.query_params  # 返回QueryDict类型
        self.params = request.data  # 返回QueryDict类型
        # self.params.update(request.data)
        # print('> self.params:', self.params)
        token = None

        try:
            account = str(self.params.get('account', ''))
            password = str(self.params.get('password', ''))
            platform = str(self.params.get('platform', ''))
            full_name = str(self.params.get('full_name', ''))

            # 边界检查
            if not account:
                raise MyApiError("account必填", 2001)

            if not password:
                raise MyApiError("password必填", 2003)

            # if not platform:
            #     raise MyApiError("platform必填", 2007)

            if not full_name:
                raise MyApiError("full_name必填", 2008)

            # 检查平台是否存在
            # platform_set = Platform.objects.filter(platform_name__iexact=platform)
            # if platform_set.count() == 0:
            #     raise MyApiError("platform不存在平台名称："+platform, 2009)
            # platform_id = platform_set.first().platform_id

            # 账号类型判断
            if re.match(r'(^1[356789]\d{9}$)|(^\+?[78]\d{10}$)', account):
                account_type = 'phone'
            elif re.match(r'^\w+[\w\.\-\_]*@\w+[\.\w]*\.\w{2,}$', account):
                account_type = 'email'
            elif re.match(r'^[A-z\u4E00-\u9FA5]+\w*$', account):
                account_type = 'username'
            else:
                raise MyApiError("账号必须是用户名、手机或者邮箱，用户名不能是数字开头", 2009)
            # print('> account_type:', account_type)

            # 检查账号是否存在
            user_list = None
            if account_type == 'phone':
                user_list = BaseInfo.objects.filter(Q(phone=account))
            elif account_type == 'email':
                user_list = BaseInfo.objects.filter(Q(email=account))
            elif account_type == 'username':
                user_list = BaseInfo.objects.filter(Q(user_name=account))
            # print("> user_list:", user_list)

            if user_list.count() and account_type == 'phone':
                raise MyApiError("手机已被注册: " + account)
            elif user_list.count() and account_type == 'email':
                raise MyApiError("邮箱已被注册: " + account)
            elif user_list.count() and account_type == 'username':
                raise MyApiError("用户名已被注册: " + account)

            base_info = {
                # 'platform_uid': round(random.random()*1000000000),
                # 'platform_id': platform_id,
                'user_name': account if account_type == 'username' else '',
                'phone': account if account_type == 'phone' else '',
                'email': account if account_type == 'email' else '',
                'full_name': full_name,
            }
            # print("> base_info:", base_info)
            current_user = BaseInfo.objects.create(**base_info)
            # print("> current_user:", current_user.id)

            # SECURITY WARNING: keep the secret key used in production secret!
            SECRET_KEY = 'django-insecure-l1$-m!u=!f9&o2$f(cm#dasus&a=5i1#+kh)090_=p%+==%9o1'
            JWT_SECRET_KEY = '@xzm2021!'

            token = jwt.encode({'account': account}, config.JWT_AUTH['JWT_SECRET_KEY'])
            auth = {
                'user_id': current_user.id,
                'password': make_password(password, None, 'pbkdf2_sha1'),
                'plaintext': password,
                # 'token': jwt.encode(current_user.id, settings.JWT_SECRET_KEY),
                'token': token,
            }
            # print("> auth:", auth)
            # print("> check_password:", check_password(password, 'pbkdf2_sha1$260000$jNjzstMtWofWN0tmUzfQwh$02D9zbyiPyYHZwb2OdrpmTwN8zI='))

            current_auth = Auth.objects.create(**auth)

            res = {
                'err': 0,
                'msg': '注册成功',
                'data': {
                    "user_id": current_user.id,
                    # "token": token,
                },
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
        # 这里 result是一个类的对象，要用result.属性名来返回
        except Exception as valueError:
            # print('> Exception:', valueError)
            res = {
                'err': valueError.err if hasattr(valueError, 'err') else 4000,
                'msg': valueError.msg if hasattr(valueError, 'msg') else valueError.args,
                # 'request': self.params,
            }
        except:
            res = {
                'err': 4999,
                'msg': '未知错误'
            }

        # return super(UserLogin, self).patch(request, *args, **kwargs)

        # return super(UserLogin, self).patch(request, *args, **kwargs)
        headers = {
            "Authorization": token,
        }
        return response.Response(data=res, status=None, template_name=None, headers=headers, content_type=None)


class MyApiError(Exception):
    def __init__(self, message, err_code=4010):
        self.msg = message
        self.err = err_code

    def __str__(self):
        # repr()将对象转化为供解释器读取的形式。可省略
        return repr(self.msg)