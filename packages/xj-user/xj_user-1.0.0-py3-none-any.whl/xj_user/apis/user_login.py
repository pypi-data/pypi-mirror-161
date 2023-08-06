# _*_coding:utf-8_*_
import os, logging, time, json, copy, re
from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

from ..services.user_service import UserService

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
    params = None

    def post(self, request, *args, **kwargs):
        # self.params = request.query_params  # 返回QueryDict类型
        self.params = request.data  # 返回QueryDict类型
        # self.params.update(request.data)
        # print("> UserLogin:", self.params)
        token = None

        try:
            account = str(self.params.get('account', ''))
            password = str(self.params.get('password', ''))
            # platform = str(self.params.get('platform', ''))

            # 边界检查
            if not account:
                raise MyApiError("account必填", 2001)

            if not password:
                raise MyApiError("password必填", 2003)

            # if not platform:
            #     raise MyApiError("platform必填", 2004)

            # 检查平台是否存在
            # platform_set = Platform.objects.filter(platform_name__iexact=platform)
            # if platform_set.count() is 0:
            #     raise MyApiError("platform不存在平台名称："+platform, 2009)
            # platform_id = platform_set.first().platform_id

            account_serv, error_text = UserService.check_account(account)
            if error_text:
                raise MyApiError(error_text, 6010)
            # print("> account_serv:", account_serv)
            user_id = account_serv['user_id']

            auth_serv, error_text = UserService.check_login(user_id=user_id, password=password, account=account)
            if error_text:
                raise MyApiError(error_text, 6020)
            token = auth_serv['token']

            # print("> check:", auth_serv)

            res = {
                'err': 0,
                'msg': 'OK',
                'data': {
                    'user_id': user_id,
                    'token': token,
                },
            }

        except SyntaxError:
            print(">SyntaxError:")
            res = {
                'err': 4001,
                'msg': '语法错误',
            }
        except LookupError:
            res = {
                'err': 4002,
                'msg': '无效数据查询',
            }
        # 这里 error是一个类的对象，要用error.属性名来返回
        except Exception as error:
            res = {
                'err': error.err if hasattr(error, 'err') else 4000,  # 发生系统异常时报4000
                'msg': error.msg if hasattr(error, 'msg') else error.args,  # 发生系统异常时捕获error.args
            }
            if not hasattr(error, 'err'):  # 仅系统异常时才提示行号
                res['file'] = error.__traceback__.tb_frame.f_globals["__file__"],  # 发生异常所在的文件
                res['line'] = error.__traceback__.tb_lineno,  # 发生异常所在的行数
        except:
            res = {
                'err': 4999,
                'msg': '未知错误'
            }

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
