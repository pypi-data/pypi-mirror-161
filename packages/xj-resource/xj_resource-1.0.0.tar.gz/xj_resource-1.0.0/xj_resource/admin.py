from django.contrib import admin

from .models import ResourceImage, ResourceImageMap, ResourceFile, ResourceFileMap


# Register your models here.


class ResourceImageAdmin(admin.ModelAdmin):
    fields = ('user_id', 'title', 'url', 'filename', 'format', 'md5', 'snapshot', 'thumb')
    list_display = ('id', 'user_id', 'title', 'url', 'filename', 'format', 'md5', 'snapshot')
    search_fields = ('id', 'user_id', 'title', 'url', 'filename', 'format', 'md5', 'snapshot')


class ResourceImageMapAdmin(admin.ModelAdmin):
    fields = ('id', 'image_id', 'source_id', 'source_table', 'price',)
    list_display = ('id', 'image_id', 'source_id', 'source_table', 'price',)
    search_fields = ('id', 'image_id', 'source_id', 'source_table', 'price',)


class ResourceFileAdmin(admin.ModelAdmin):
    fields = ('user_id', 'title', 'url', 'filename', 'format', 'md5', 'snapshot', 'thumb')
    list_display = ('id', 'user_id', 'title', 'url', 'filename', 'format', 'md5', 'snapshot')
    search_fields = ('id', 'user_id', 'title', 'url', 'filename', 'format', 'md5', 'snapshot')


class ResourceFileMapAdmin(admin.ModelAdmin):
    fields = ('id', 'file_id', 'source_id', 'source_table', 'price',)
    list_display = ('id', 'file_id', 'source_id', 'source_table', 'price',)
    search_fields = ('id', 'file_id', 'source_id', 'source_table', 'price',)


admin.site.register(ResourceImage, ResourceImageAdmin)
admin.site.register(ResourceImageMap, ResourceImageMapAdmin)

admin.site.register(ResourceFile, ResourceFileAdmin)
admin.site.register(ResourceFileMap, ResourceFileMapAdmin)

admin.site.site_header = '资源模块'
admin.site.site_title = '资源模块'