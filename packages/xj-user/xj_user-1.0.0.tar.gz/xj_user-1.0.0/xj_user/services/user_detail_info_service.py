# encoding: utf-8
"""
@project: djangoModel->user_info_service
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 用户信息服务
@created_time: 2022/6/27 19:51
"""

from .user_service import UserService
from ..models import ExtendFiled, DetailInfo
from ..utils.model_handle import *


class DetailInfoService:
    @staticmethod
    def transform_params(request_dict):
        # 冗余字段 请求参数转换
        filed_map = parse_model(ExtendFiled.objects.all())
        filed_map = {item['key_name']: item['field'] for item in filed_map}
        transformed_dict = {}
        for k, v in request_dict.items():
            if k in filed_map.keys():
                transformed_dict[filed_map[k]] = v
            else:
                transformed_dict[k] = v
        return transformed_dict

    @staticmethod
    def transform_result(result):
        # 冗余字段 结果集转换
        filed_map = parse_model(ExtendFiled.objects.all())
        filed_map = {item['field']: item['key_name'] for item in filed_map}
        transformed_list = []
        for item in result:
            transformed_dict = {}
            for k, v in item.items():
                if k in filed_map.keys():
                    transformed_dict[filed_map[k]] = v
                else:
                    transformed_dict[k] = v
            transformed_list.append(transformed_dict)
        return transformed_list

    @staticmethod
    def get_info_list(request):
        # 查询用户详细信息列表
        params = parse_data(request.data)
        transformed_dict = DetailInfoService.transform_params(params)
        page = request.data.get('page', 1)
        limit = request.data.get('limit', 20)
        if 'page' in params.keys():
            del transformed_dict['page']
        if 'limit' in params.keys():
            del transformed_dict['limit']

        try:
            list_set = DetailInfo.objects.filter(**transformed_dict)
            count = DetailInfo.objects.filter(**transformed_dict).count()
        except Exception as e:
            return util_response("", 7557, status.HTTP_400_BAD_REQUEST, e.__str__())
        # 分页数据
        limit_set = Paginator(list_set, limit)
        page_set = limit_set.get_page(page)

        # 数据序列化操作
        json_data = json.loads(serializers.serialize('json', page_set))
        final_res_dict = []
        for i in json_data:
            fields = i['fields']
            fields['id'] = i['pk']
            final_res_dict.append(fields)
        final_res_dict = DetailInfoService.transform_result(final_res_dict)

        # 数据拼装
        result = {'data': final_res_dict, 'limit': int(limit), 'page': int(page), 'count': count}
        return util_response(result, 0, status.HTTP_200_OK, "ok")

    @staticmethod
    def get_own_info(request):
        token = request.META.get('HTTP_AUTHORIZATION', None)
        token_serv, error_text = UserService.check_token(token)
        if error_text:
            return util_response(err=6045, msg=error_text)
        user_info = parse_model(DetailInfo.objects.filter(user_id=token_serv['user_id']))
        if not user_info:
            return util_response(data=[], msg='该用户没用填写详细信息')
        final_res_dict = DetailInfoService.transform_result(user_info)
        return util_response(data=final_res_dict[0])

    @staticmethod
    def create_detail_info(request):
        # 用户绑定详细信息，新增详细信息
        try:
            # 身份验证，传user_id使用传的，没有传使用token获取的
            user_id = request.data.get('user_id', None)
            token = request.META.get('HTTP_AUTHORIZATION', None)
            token_serv, error_text = UserService.check_token(token)
            if error_text:
                return util_response(err=6045, msg=error_text)
            if not user_id:
                user_id = token_serv['user_id']
            requestData = parse_data(request.data)
            transformed_dict = DetailInfoService.transform_params(requestData)
            transformed_dict["user_id"] = user_id
            # 判断是否创建
            is_set = DetailInfo.objects.filter(user=transformed_dict['user_id'])
            if is_set:
                return util_response("", 7557, status.HTTP_200_OK, '您已绑定，请勿重复提交')
            DetailInfo.objects.create(**transformed_dict)
        except Exception as e:
            return util_response("", 7557, status.HTTP_400_BAD_REQUEST, e.__str__())
        return util_response('', 0, status.HTTP_200_OK, "ok")

    @staticmethod
    def update_detail_info(request):
        # 用户绑定详细信息，新增详细信息
        try:
            id = request.POST.get('id', None)
            if id is None:
                return util_response("", 7557, status.HTTP_200_OK, '参数错误')
            requestData = parse_data(request.POST)
            transformed_dict = DetailInfoService.transform_params(requestData)
            result = DetailInfo.objects.filter(id=id)
            if result is None:
                return util_response("", 7557, status.HTTP_200_OK, '数据不存在')
            del requestData['id']
            result.update(**transformed_dict)
        except Exception as e:
            return util_response("", 7557, status.HTTP_400_BAD_REQUEST, e.__str__())
        return util_response('', 0, status.HTTP_200_OK, "ok")
