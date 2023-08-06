# _*_coding:utf-8_*_

import os, logging, time, json, copy
import re
from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import response
# from rest_framework import serializers
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.utils.translation import gettext as tr


from ..models import BaseInfo
from ..services.user_service import UserService, UserInfoSerializer

logger = logging.getLogger(__name__)


def make_code():
    now = datetime.now()
    date_str = now.strftime('%Y%m%d')
    time_str: str = str(time.time())[5:10]
    ms_str = str(now)[-6:-3]
    code = '%s%s%s' % (date_str, time_str, ms_str)
    return code


# 获取用户信息
class UserInfo(generics.UpdateAPIView):  # 或继承(APIView)
    permission_classes = (AllowAny,)  # 允许所有用户 (IsAuthenticated,IsStaffOrBureau)
    serializer_class = UserInfoSerializer  # 继承generics.UpdateAPIView需要设置此属性覆盖get_serializer_class()方法
    queryset = BaseInfo.objects.all()  # 继承generics.UpdateAPIView需要设置此属性覆盖get_queryset()方法
    # lookup_field = 'id'
    params = None

    def get(self, request, *args, **kwargs):
        self.params = request.query_params  # 返回QueryDict类型
        # print("> params:", self.params)
        # print("> language:", request.LANGUAGE_CODE)

        try:
            token = self.request.META.get('HTTP_AUTHORIZATION', None)
            # print("> token:", token)

            token_serv, error_text = UserService.check_token(token)
            # print("> token_serv:", token_serv)
            if error_text:
                raise MyApiError(error_text, 6010)
            account = token_serv['account']

            account_serv, error_text = UserService.check_account(account)
            if error_text:
                raise MyApiError(error_text, 6020)
            # print("> account_serv:", account_serv)
            user_info = account_serv

            res = {
                'err': 0,
                'msg': 'OK',
                'data': user_info,
                # 'tr': tr('HELLO'),
                # 'request': self.params,
                # 'serializer': serializer.data,
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