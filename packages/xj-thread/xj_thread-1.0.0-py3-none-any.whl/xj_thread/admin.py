from django.contrib import admin

from .models import Thread, ThreadStatistic
from .models import ThreadExtendData
from .models import ThreadExtendField
from .models import ThreadImageAuth, ThreadResource
from .models import ThreadShow, ThreadClassify, ThreadCategory, ThreadAuth
from .models import ThreadTag, ThreadTagMapping


@admin.register(ThreadShow)
class ThreadShowAdmin(admin.ModelAdmin):
    list_display = ('id', 'value', 'config', 'description')
    search_fields = ('id', 'value', 'config')
    fields = ('value', 'config', 'description')


@admin.register(ThreadClassify)
class ThreadClassifyAdmin(admin.ModelAdmin):
    list_display = ('id', 'value', 'show_id', 'category_id', 'description', 'icon')
    search_fields = ('id', 'value', 'show_id', 'category_id')
    fields = ('value', 'show_id', 'category_id', 'description', 'icon')


@admin.register(ThreadCategory)
class ThreadCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'value', 'description')
    search_fields = ('id', 'value')
    fields = ('value', 'description')


@admin.register(ThreadAuth)
class ThreadAuthAdmin(admin.ModelAdmin):
    list_display = ('id', 'value')
    search_fields = ('id', 'value')
    fields = ('value',)


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_deleted', 'category_id', 'classify_id', 'show_id', 'user_id', 'auth_id',
                    'author', 'title', 'short_content', 'ip', 'has_enroll', 'has_fee', 'has_comment',
                    'short_cover', 'short_photos', 'short_video', 'short_files', 'short_logs', 'more')
    search_fields = ('id', 'is_deleted', 'category_id', 'classify_id', 'show_id', 'user_id', 'auth_id',
                     'title', 'content', 'ip', 'has_enroll', 'has_fee', 'has_comment',
                     'cover', 'photos', 'video', 'files', 'logs')
    fields = ('is_deleted', 'category_id', 'classify_id', 'show_id', 'user_id', 'auth_id',
              'author', 'title', 'content', 'ip', 'has_enroll', 'has_fee', 'has_comment',
              'cover', 'photos', 'video', 'files', 'logs', 'more')
    readonly_fields = ()  # 只读
    list_per_page = 10  # 每页显示10条
    ordering = ['-update_time']  # 排序

    # class Media:
    #     css = {
    #         'all': (
    #             '/css/fancy.css',
    #         )
    #     }


@admin.register(ThreadExtendData)
class ThreadExtendDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'field_1', 'field_2', 'field_3', 'field_4', 'field_5', 'field_6', 'field_7')
    search_fields = ('id', 'field_1', 'field_2', 'field_3', 'field_4', 'field_5', 'field_6', 'field_7')
    fields = ('id', 'field_1', 'field_2', 'field_3', 'field_4', 'field_5', 'field_6', 'field_7')


@admin.register(ThreadExtendField)
class ThreadExtendFieldAdmin(admin.ModelAdmin):
    list_display = ('classify_id', 'field', 'extend_field','value', 'type', 'unit')
    search_fields = ('classify_id', 'field', 'extend_field','value', 'type', 'unit')
    fields = ('classify_id', 'field', 'extend_field','value', 'type', 'unit')


@admin.register(ThreadTag)
class ThreadTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'value')
    search_fields = ('id', 'value')
    fields = ('value',)


@admin.register(ThreadTagMapping)
class ThreadTagMappingAdmin(admin.ModelAdmin):
    list_display = ('id', 'thread_id', 'tag_id')
    search_fields = ('id', 'thread_id', 'tag_id')
    fields = ('thread_id', 'tag_id')


@admin.register(ThreadImageAuth)
class ThreadImageAuthAdmin(admin.ModelAdmin):
    list_display = ('id', 'value')
    search_fields = ('id', 'value')
    fields = ('value',)


@admin.register(ThreadResource)
class ThreadImageAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'url', 'filename', 'filetype', 'image_auth_id', 'price', 'snapshot', 'format', 'logs', 'user_id')
    search_fields = (
        'id', 'name', 'url', 'filename', 'filetype', 'image_auth_id', 'price', 'snapshot', 'format', 'logs', 'user_id')
    fields = (
        'id', 'name', 'url', 'filename', 'filetype', 'image_auth_id', 'price', 'snapshot', 'format', 'logs', 'user_id')


@admin.register(ThreadStatistic)
class ThreadStatisticAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'thread_id', 'flag_classifies', 'flag_weights', 'weight', 'views', 'plays', 'comments', 'likes',
        'favorite', 'shares',
    )
    search_fields = (
        'id', 'thread_id', 'flag_classifies', 'flag_weights', 'weight', 'views', 'plays', 'comments', 'likes',
        'favorite', 'shares',
    )



# Register your models here.
# admin.site.register(ThreadShow, ThreadShowAdmin)
# admin.site.register(ThreadClassify, ThreadClassifyAdmin)
# admin.site.register(ThreadCategory, ThreadCategoryAdmin)
# admin.site.register(ThreadAuth, ThreadAuthAdmin)

# admin.site.register(Thread, ThreadAdmin)

# admin.site.register(ThreadExtendData, ThreadExtendDataAdmin)
# admin.site.register(ThreadExtendField, ThreadExtendFieldAdmin)

# admin.site.register(ThreadTag, ThreadTagAdmin)
# admin.site.register(ThreadTagMapping, ThreadTagMappingAdmin)

# admin.site.register(ThreadImageAuth, ThreadImageAuthAdmin)
# admin.site.register(ThreadResource, ThreadImageAdmin)
# admin.site.site_header = 'msa一体化管理后台'
# admin.site.site_title = 'msa一体化管理后台'