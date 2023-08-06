# encoding: utf-8
"""
@project: djangoModel->tool
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: CURD 工具
@created_time: 2022/6/15 14:14
"""

# ===========  工具方法 start =============
import json

from django.core import serializers
from django.core.paginator import Paginator

from .custom_response import *


def parse_data(data):
    # 解析请求参数
    requestData = {}
    for k, v in data.items():
        requestData[k] = v if not v == "" else None
    return requestData


def parse_model(res_set, is_simple=False):
    json_data = json.loads(serializers.serialize('json', res_set))
    if not json_data:
        return None
    else:
        if is_simple:
            return json_data[0]['fields']
        else:
            res_set = []
            for i in json_data:
                fields = i['fields']
                fields['id'] = i['pk']
                res_set.append(fields)
            return res_set


def model_select(request, model, is_need_delete=False, json_parse_key=None):
    # 模型快速分页查询  分页+条件
    page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 20)
    params = parse_data(request.GET)
    if 'page' in params.keys():
        del params['page']
    if 'limit' in params.keys():
        del params['limit']

    if is_need_delete:
        params['is_delete'] = 0
    try:
        list_set = model.objects.filter(**params)
        count = model.objects.filter(**params).count()
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
        if not json_parse_key is None:
            fields[json_parse_key] = json.loads(fields[json_parse_key])
        final_res_dict.append(fields)
    # 数据拼装
    result = {'data': final_res_dict, 'limit': int(limit), 'page': int(page), 'count': count}
    return util_response(result, 0, status.HTTP_200_OK, "ok")


def model_del(request, model, is_real_delete=True):
    # 删除设备
    id = request.POST.get('id')
    if not id:
        return util_response("", 7557, status.HTTP_400_BAD_REQUEST, 'ID不能为空')
    from_data = parse_data(request.POST)
    if is_real_delete:
        res = model.objects.filter(**from_data)
        if not res:
            return util_response("", 7557, status.HTTP_400_BAD_REQUEST, '数据已不存在')
        res.delete()
    else:
        from_data['is_delete'] = 0
        res = model.objects.filter(**from_data)
        if not res:
            return util_response("", 7557, status.HTTP_400_BAD_REQUEST, '数据已不存在')
        res.update(is_delete=1)
    return util_response('', 0, status.HTTP_200_OK, "ok")


def model_create(request, model, validate):
    try:
        requestData = parse_data(request.POST)
        validator = validate(requestData)
        is_pass, error = validator.validate()
        if not is_pass:
            return util_response("", 7557, status.HTTP_400_BAD_REQUEST, error)
        model.objects.create(**requestData)
    except Exception as e:
        return util_response("", 7557, status.HTTP_400_BAD_REQUEST, e.__str__())
    return util_response('', 0, status.HTTP_200_OK, "ok")


def model_update(request, model, is_need_delete=False):
    # 模型修改
    id = request.POST.get('id')
    if not id:
        return util_response('', 7557, status.HTTP_200_OK, "ID不能为空")
    from_data = parse_data(request.POST)

    del from_data['id']
    if from_data == {}:
        return util_response('', 7557, status.HTTP_200_OK, "修改项为空")

    if is_need_delete:
        res = model.objects.filter(id=id, is_delete=0)
    else:
        res = model.objects.filter(id=id)
    if not res:
        return util_response('', 7557, status.HTTP_200_OK, "数据已不存在")
    try:
        res.update(**from_data)
        return util_response('', 0, status.HTTP_200_OK, "ok")
    except Exception as e:
        return util_response("", 7557, status.HTTP_400_BAD_REQUEST, e.__str__())
