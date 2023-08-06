# _*_coding:utf-8_*_

# import os, logging, time, json, copy
import re
from datetime import datetime, timedelta
import jwt

# from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.db.models import Q
# from django.db.models import F
# from rest_framework import exceptions
from rest_framework import serializers

from .. import config
from ..models import Auth
from ..models import BaseInfo
from ..utils.custom_response import util_response
from ..utils.model_handle import parse_model, model_select


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
            'user_group_id',
            'get_group_desc',
            'user_name',
            'full_name',
            'phone',
            'email',
            'wechat',
            'user_info',
            'user_group',
            'permission'
        ]
        # exclude = ['platform_uid']

    # # 这里是调用了platform这个字段拼成了get_platform
    # def get_platform(self, obj):
    #     return obj.platform.platform_name
    #     # return {
    #     #     'id': obj.platform.platform_id,
    #     #     'name': obj.platform.platform_name,
    #     # }


class UserService:
    def __init__(self):
        pass

    # 检测账户
    @staticmethod
    def check_account(account):
        """
        @param account 用户账户，可以支持三种类型：手机、用户名、邮箱。自动判断
        @description 注意：用户名不推荐由纯数字构成，因为那样容易和11位手机号冲突
        """
        # 账号类型判断
        if re.match(r'(^1[356789]\d{9}$)|(^\+?[78]\d{10}$)', account):
            account_type = 'phone'
        elif re.match(r'^\w+[\w\.\-\_]*@\w+[\.\w]*\.\w{2,}$', account):
            account_type = 'email'
        elif re.match(r'^[A-z\u4E00-\u9FA5]+\w*$', account):
            account_type = 'username'
        else:
            return None, "账号必须是用户名、手机或者邮箱，用户名不能是数字开头"

        # 用户ID
        user_list = BaseInfo.objects.filter(Q(user_name=account) | Q(phone=account) | Q(email=account))
        if not user_list.count():
            return None, "账户不存在"
        if user_list.count() > 1:
            return None, "登录异常，请联系管理员，发现多账号冲突："
        # print("> user_list:", user_list)
        user_set = user_list.first()

        serializer = UserInfoSerializer(user_set, many=False)
        # print("> serializer:", serializer)
        return serializer.data, None

    # 验证密码
    @staticmethod
    def check_login(user_id, password, account):
        """
        @param user_id 用户ID
        @param password 用户密码。
        @param account 登陆账号，必填，用于生成Token令牌。
        @description 注意：目前密码是明文传输，今后都要改成密文传输
        """
        auth_set = Auth.objects.filter(user_id=user_id, password__isnull=False).order_by('-update_time').first()
        if not auth_set:
            return None, "账户尚未开通登录服务：" + account + "(" + str(user_id) + ")"

        # 判断密码不正确
        is_pass = check_password(password, auth_set.password)
        if not is_pass:
            return None, "密码错误"

        # 过期时间
        expire_timestamp = datetime.utcnow() + timedelta(days=config.EXPIRE_TIME['DAY'],
                                                         seconds=config.EXPIRE_TIME['SECOND'])
        # 为本次登录生成Token并记录
        # todo 漏洞，当用户修改用户名时，并可能导致account失效，是否存用户ID更好
        token = jwt.encode(payload={'account': account, 'user_id': user_id, "exp": expire_timestamp},
                           key=config.JWT_AUTH['JWT_SECRET_KEY'])
        payload = jwt.decode(token, key=config.JWT_AUTH['JWT_SECRET_KEY'], verify=True, algorithms=["RS256", "HS256"])
        print("> payload:", payload)
        auth_set.token = token
        auth_set.save()

        return {'token': token}, None

    # 验证密码
    @staticmethod
    def check_login_wechat(user_id, phone):
        """
        @param user_id 用户ID
        @param phone 登陆账号，必填，用于生成Token令牌。
        @description 注意：目前密码是明文传输，今后都要改成密文传输
        """
        auth_set = Auth.objects.filter(user_id=user_id, password__isnull=False).order_by('-update_time').first()
        if not auth_set:
            return None, "账户尚未开通登录服务：" + phone + "(" + str(user_id) + ")"

        # 过期时间
        expire_timestamp = datetime.utcnow() + timedelta(days=config.EXPIRE_TIME['DAY'], seconds=config.EXPIRE_TIME['SECOND'])
        # 为本次登录生成Token并记录
        # todo 漏洞，当用户修改用户名时，并可能导致account失效，是否存用户ID更好
        token = jwt.encode(payload={'account': phone, 'user_id': user_id, "exp": expire_timestamp}, key=config.JWT_AUTH['JWT_SECRET_KEY'])
        payload = jwt.decode(token, key=config.JWT_AUTH['JWT_SECRET_KEY'], verify=True, algorithms=["RS256", "HS256"])
        print("> payload:", payload)
        auth_set.token = token
        auth_set.save()

        return {'token': token}, None

    # 检测令牌
    @staticmethod
    def check_token(token):
        """
        @param token 用户令牌。
        @description 注意：用户令牌的载荷体payload中必须包含两个参数：account账号、exp过期时间，其中账号可以是手机、用户名、邮箱三种。
        @description BEARER类型的token是在RFC6750中定义的一种token类型，OAuth2.0协议RFC6749对其也有所提及，算是对RFC6749的一个补充。BEARER类型token是建立在HTTP/1.1版本之上的token类型，需要TLS（Transport Layer Security）提供安全支持，该协议主要规定了BEARER类型token的客户端请求和服务端验证的具体细节。
        @description 理论上，每次请求令牌后就更新一次令牌，以监测用户长期访问时，不至于到时间后掉线反复登陆。
        """
        # 检查是否有Bearer前辍，如有则截取
        # print("> token 1:", token)
        if not token:
            return None, "请登录"  # 缺少Token

        if re.match(r'Bearer(.*)$', token, re.IGNORECASE):
            token = re.match(r'Bearer(.*)$', token, re.IGNORECASE).group(1).strip()
        # print("> token 2:", token)

        if not token:
            return None, "您尚未登录"

        # # 验证token。另一种方式，从数据库核对Token，通过对比服务端的Token，以确定是否为服务器发送的。今后启用该功能。
        # auth_set = Auth.objects.filter(Q(token=token)).order_by('-update_time')
        # # print("> auth:", auth_set)
        # if not auth_set.count():
        #     raise MyApiError('token验证失败', 6002)
        # auth = auth_set.first()

        try:
            # jwt.decode会自动检查exp参数，如果超时则抛出jwt.ExpiredSignatureError超时
            jwt_payload = jwt.decode(token, key=config.JWT_AUTH['JWT_SECRET_KEY'], verify=True,
                                     algorithms=["RS256", "HS256"])
            # print("> jwt_payload:", jwt_payload)

        except jwt.ExpiredSignatureError:
            return None, "登录已过期，请重新登录"

        except jwt.InvalidTokenError:
            return None, "用户令牌无效，请重新登录"

        account = jwt_payload.get('account', None)
        user_id = jwt_payload.get('user_id', None)
        if not account:
            return {'payload': jwt_payload}, "错误：令牌载荷中未提供用户账户Account"

        # 检测用户令牌时不应该调用用户信息，这会导致任何接口都会查询用户表，时间会增加
        # user_info = UserService.check_account(account=account)

        return {'account': account, 'user_id': user_id}, None

    # 用户信息列表
    @staticmethod
    def user_list(request, call_back=None):
        token = request.META.get('HTTP_AUTHORIZATION', None)
        token_serv, error_text = UserService.check_token(token)
        if error_text:
            return util_response(err=6045, msg=error_text)
        user_info = parse_model(BaseInfo.objects.filter(id=token_serv['user_id']))
        if not user_info:
            return util_response(data=[], msg='该用户没有权限')
        # 支持自定义闭包判断用户权限
        if call_back:
            is_pass = call_back(user_info)
            if not is_pass:
                return util_response(err=6025, msg='该用户没有权限')
        return model_select(request, BaseInfo)

    # 胡家萍 用户权限判断闭包
    @staticmethod
    def hjp_user_right_call(user_info):
        # map = {1: "集团用户", 2: "村民用户没有权限"}
        try:
            if user_info[0]['user_group'] == 1:
                return True
            else:
                return False
        except Exception as e:
            return False
