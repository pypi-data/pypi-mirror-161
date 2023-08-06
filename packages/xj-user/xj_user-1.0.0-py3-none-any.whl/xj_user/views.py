# from django.db.models import Q
from django.shortcuts import render
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from .models import *
# from rest_framework.permissions import IsAuthenticated, AllowAny
# from django.db.models import Q
# from django.db.models import F

# Create your views here.


class UserAPISerializer(serializers.ModelSerializer):  # 继承自ModelSerializer类
    """ 序列化数据的类，根据model表来获取字段 """

    class Meta:
        model = BaseInfo
        fields = '__all__'


class UserListAPIView(APIView):
    permission_classes = (AllowAny,)  # 允许所有用户
    params = None

    def get(self, request, format=None):
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
