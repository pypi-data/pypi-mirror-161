# encoding: utf-8
"""
@project: hydrology-station-python-4.0->validate
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 表单验证基类
@created_time: 2022/5/25 11:43
"""
import json

from django import forms
from django.core.exceptions import ValidationError


class Validate(forms.Form):
    """检验基类，子类编写规则，调用父类的validate方法"""

    def validate(self):
        """
        request 请求参数验证
        :return {'code': 'err': self.errors}:
        """
        if self.is_valid():
            return True, None
        else:
            error = json.dumps(self.errors)
            error = json.loads(error)
            temp_error = {}
            # 统一展示小写 提示，中文转义回来
            for k, v in error.items():
                temp_error[k.lower()] = v[0]
            return False, temp_error


# 案例使用自定义验证方法
def log_unit_id(value):
    res = True
    if not res:
        raise ValidationError('unit_id不存在')


class ExampleValidate(Validate):
    """验证查询表单"""
    region_code = forms.CharField(
        required=True,
        error_messages={
            "required": "行政编码 必填",
        })
    unit_id = forms.IntegerField(  # 自定义方法
        validators=[log_unit_id],
    )
