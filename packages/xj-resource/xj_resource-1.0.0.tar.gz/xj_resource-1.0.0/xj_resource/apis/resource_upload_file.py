# encoding: utf-8
"""
@project: djangoModel->resource_upload_file
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 文件上传接口
@created_time: 2022/8/2 10:28
"""
# encoding: utf-8
from rest_framework.views import APIView

from ..config import host
from ..models import ResourceFile
from ..services.upload_file_service import UploadFileService
from ..utils.model_handle import *


class UploadFile(APIView):
    def post(self, request):
        user_id = request.user.id or 0
        # if not user_id:
        #     return Response({'err': 4003, 'msg': '用户不存在', 'data': []}, status=status.HTTP_200_OK)
        file = request.FILES.get('file')
        title = request.POST.get('title', '')
        group_id = request.POST.get('group_id', 0)

        uploader = UploadFileService(input_file=file)
        info = uploader.info_detail()
        info['title'] = title or info['snapshot']['old_filename']
        info['user_id'] = user_id
        info['group_id'] = group_id
        uploader.write_disk()
        image_instance = uploader.save_to_db(info)
        info['url'] = host + info['url']
        if not image_instance is None:
            info['id'] = image_instance.id
        if not uploader.is_valid():
            return util_response(err=4003, msg=uploader.get_error_message())
        return util_response(data=info)

    # 文件列表
    def get(self, request):
        return model_select(request, ResourceFile)
