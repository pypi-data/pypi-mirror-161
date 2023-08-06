# _*_coding:utf-8_*_
from django.conf import settings
from django.conf.urls import static
from django.conf.urls import url
from django.urls import re_path

from .apis.resource_upload_file import UploadFile
from .apis.resource_upload_image import UploadImage

# 应用名称
app_name = 'resource'

urlpatterns = [
    url(r'upload_file/?$', UploadFile.as_view(), name='st_upload_file'),  # 文件上传
    url(r'upload_image/?$', UploadImage.as_view(), name='st_upload_image'),  # 图片上传
    # re_path(r'^_upload_image/?$', UploadImage.as_view(), ),

    # 这里要填写/static/和/media/路径，否则django不会返回静态文件。
    re_path("static/(?P<path>.*)$", static.serve, {"document_root": settings.STATIC_ROOT, "show_indexes": False}, "static"),
    re_path("media/(?P<path>.*)$", static.serve, {"document_root": settings.MEDIA_ROOT, "show_indexes": False}, "media"),
]
