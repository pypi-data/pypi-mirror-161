# encoding: utf-8
"""
@project: hujiaping->validator
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 用户模块验证器
@created_time: 2022/7/22 14:24
"""
from .utils.validator import *


class GroupValidator(Validate):
    group = forms.CharField(
        required=True,
        error_messages={
            "required": "分组必填 必填",
        })
    description = forms.CharField(
        required=True,
        error_messages={
            "required": "描述 必填",
        })
