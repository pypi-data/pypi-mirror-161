# encoding: utf-8
"""
@project: djangoModel->wechet_login
@author: 孙楷炎
@created_time: 2022/7/14 10:55
"""

# 微信登录方法
from rest_framework.views import APIView

from ..services.wechat_service import WechatService
from ..utils.custom_response import util_response


class WechetLogin(APIView):
    # 微信手机号码登录
    def post(self, request):
        code = self.request.data.get('code', None)
        if not code:
            return util_response(err=6558, msg='参数错误')
        app = WechatService()
        err, data = app.phone_login(code=code)
        if err == 0:
            return util_response(data=data)
        else:
            return util_response(msg=err, err=6004)
