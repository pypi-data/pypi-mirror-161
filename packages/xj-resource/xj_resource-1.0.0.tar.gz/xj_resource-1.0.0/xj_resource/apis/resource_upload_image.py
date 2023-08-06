from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..services.upload_image_service import UploadImageService
from ..models import *
from ..utils.model_handle import model_select


class UploadImage(APIView):
    def post(self, request):
        # 获取用户ID
        user_id = request.user.id or 0
        # if not user_id:
        #     return Response({'err': 4003, 'msg': '用户不存在', 'data': []}, status=status.HTTP_200_OK)
        file = request.FILES.get('image')
        title = request.POST.get('title', '')

        uploader = UploadImageService(input_file=file)
        info = uploader.info_detail()

        info['title'] = title
        info['user_id'] = user_id
        uploader.write_disk()
        image_instance = uploader.save_to_db(info)
        if image_instance:
            info['id'] = image_instance.id
        if not uploader.is_valid():
            return Response({'err': 4003, 'msg': uploader.get_error_message(), 'data': []}, status=status.HTTP_200_OK)
        return Response({'err': 0, 'msg': '/OK', 'data': info}, status=status.HTTP_200_OK)

    # 文件列表
    def get(self, request):
        return model_select(request, ResourceImage)
