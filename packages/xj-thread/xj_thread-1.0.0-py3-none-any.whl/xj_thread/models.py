import socket

from DjangoUeditor.models import UEditorField

from django.db import models
from django.utils import timezone

# from apps.user.models import User
# from apps.user.models import BaseInfo

hostname = socket.gethostname()
my_ip_addr = socket.gethostbyname(hostname)


# 展示类型。用于对前端界面的显示样式进行分类
class ThreadShow(models.Model):
    class Meta:
        db_table = 'thread_show'
        verbose_name_plural = '13. 展示类型表 (样式)'

    id = models.AutoField(verbose_name='展示类型ID', primary_key=True)
    value = models.CharField(verbose_name='值', max_length=50)
    config = models.JSONField(verbose_name='前端配置', blank=True, null=True, default=list)  # 用于存放前端自定义的界面或样式相关的配置数据
    description = models.CharField(verbose_name='描述', max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.value}"


# 类别。类似于版块大类的概念，用于圈定信息内容所属的主要类别
class ThreadCategory(models.Model):
    class Meta:
        db_table = 'thread_category'
        verbose_name_plural = '11. 类别表 (页面类别)'

    id = models.AutoField(verbose_name='ID', primary_key=True)
    value = models.CharField(verbose_name='值', max_length=50)
    description = models.CharField(verbose_name='描述', max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.value}"


class ThreadClassify(models.Model):
    """
    @brief 分类。具体的分类，可以是按行业、兴趣、学科的分类，是主类别下的子分类。
    @note 考虑到多语言翻译的问题，不需要写接口，由运维在后台添加
    """

    class Meta:
        db_table = 'thread_classify'
        verbose_name_plural = '12. 分类表 (行业分类)'

    id = models.AutoField(verbose_name='分类ID', primary_key=True)
    # key = models.CharField(verbose_name='分类关键字', max_length=50, blank=True, null=True)
    value = models.CharField(verbose_name='分类', max_length=50, unique=True)
    show_id = models.ForeignKey(verbose_name='默认展示ID', to=ThreadShow, db_column='show_id', related_name='+',
                                on_delete=models.DO_NOTHING, default=1)
    description = models.CharField(verbose_name='描述', max_length=255, blank=True, null=True)
    category_id = models.ForeignKey(verbose_name='父类别', to=ThreadCategory, db_column='category_id', related_name='+',
                                    on_delete=models.DO_NOTHING, blank=True, null=True)
    icon = models.CharField(verbose_name='图标', max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.value}"


# 访问权限。作者指定允许哪里用户可以访问，例如私有、公开、好友、指定某些人可以访问等。
class ThreadAuth(models.Model):
    class Meta:
        db_table = 'thread_auth'
        verbose_name_plural = '权限类型表'

    id = models.AutoField(verbose_name='ID', primary_key=True)
    value = models.CharField(verbose_name='值', max_length=50)

    def __str__(self):
        return f"{self.value}"


# 扩展字段数据表。用于扩展一些自定义的版块功能的数据
class ThreadExtendData(models.Model):
    class Meta:
        db_table = 'thread_extend_data'
        verbose_name_plural = '扩展字段数据表'

    id = models.AutoField(verbose_name='信息ID', primary_key=True)
    field_1 = models.CharField(verbose_name='1', max_length=255, blank=True, null=True)
    field_2 = models.CharField(verbose_name='2', max_length=255, blank=True, null=True)
    field_3 = models.CharField(verbose_name='3', max_length=255, blank=True, null=True)
    field_4 = models.CharField(verbose_name='4', max_length=255, blank=True, null=True)
    field_5 = models.CharField(verbose_name='5', max_length=255, blank=True, null=True)
    field_6 = models.CharField(verbose_name='6', max_length=255, blank=True, null=True)
    field_7 = models.CharField(verbose_name='7', max_length=255, blank=True, null=True)
    field_8 = models.CharField(verbose_name='8', max_length=255, blank=True, null=True)
    field_9 = models.CharField(verbose_name='9', max_length=255, blank=True, null=True)
    field_10 = models.CharField(verbose_name='10', max_length=255, blank=True, null=True)
    field_11 = models.CharField(verbose_name='11', max_length=255, blank=True, null=True)
    field_12 = models.CharField(verbose_name='12', max_length=255, blank=True, null=True)
    field_13 = models.CharField(verbose_name='13', max_length=255, blank=True, null=True)
    field_14 = models.CharField(verbose_name='14', max_length=255, blank=True, null=True)
    field_15 = models.CharField(verbose_name='15', max_length=255, blank=True, null=True)
    field_16 = models.CharField(verbose_name='16', max_length=255, blank=True, null=True)
    field_17 = models.CharField(verbose_name='17', max_length=255, blank=True, null=True)
    field_18 = models.CharField(verbose_name='18', max_length=255, blank=True, null=True)
    field_19 = models.CharField(verbose_name='19', max_length=255, blank=True, null=True)
    field_20 = models.CharField(verbose_name='20', max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.id}"


# 扩展字段表。用于声明扩展字段数据表中的(有序)字段具体对应的什么键名。注意：扩展字段是对分类的扩展，而不是主类别的扩展
class ThreadExtendField(models.Model):
    class Meta:
        db_table = 'thread_extend_field'
        verbose_name_plural = '扩展字段表'
        unique_together = (("classify_id", "field"),)  # 组合唯一，分类+字段

    id = models.AutoField(verbose_name='信息ID', primary_key=True)

    # 数据库生成classify_id字段
    classify_id = models.ForeignKey(verbose_name='分类ID', to=ThreadClassify, db_column='classify_id', related_name='+',
                                    on_delete=models.DO_NOTHING)
    field = models.CharField(verbose_name='字段', max_length=255)  # 眏射ThreadExtendData表的键名
    extend_field = models.CharField(verbose_name='映射字段', max_length=255)  # 眏射ThreadExtendData表的键名
    value = models.CharField(verbose_name='内容', max_length=255, null=True, blank=True)
    type = models.CharField(verbose_name='类型', max_length=255, blank=True, null=True)
    unit = models.CharField(verbose_name='参数单位', max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.id}"


# 信息表，即主表
class Thread(models.Model):
    class Meta:
        ordering = ['-create_time']
        db_table = 'thread'  # 指定数据库的表名，否则默认会显示app名+class名。
        verbose_name_plural = '1. 信息表'  # 指定管理界面的别名，否则默认显示class名。末尾不加s。

    # ID 默认自增
    id = models.BigAutoField(verbose_name='ID', primary_key=True)
    is_deleted = models.BooleanField(verbose_name='是否删除', default=False)
    category_id = models.ForeignKey(verbose_name='类别ID', to=ThreadCategory, db_column='category_id', related_name='+',
                                    on_delete=models.DO_NOTHING, default=1)
    classify_id = models.ForeignKey(verbose_name='分类ID', to=ThreadClassify, db_column='classify_id', related_name='+',
                                    on_delete=models.DO_NOTHING, null=True, blank=True)
    show_id = models.ForeignKey(verbose_name='展示ID', to=ThreadShow, db_column='show_id', related_name='+',
                                on_delete=models.DO_NOTHING, null=True, blank=True,
                                default=1)  # 如果没有传入显示类型，则使用分类表中的默认显示类型
    # user_id = models.ForeignKey(verbose_name='用户ID', to=User, db_column='user_id', related_name='+', on_delete=models.DO_NOTHING)  # 登录后，自动填。
    user_id = models.BigIntegerField(verbose_name='用户ID', db_index=True)  # 登录后，自动填。
    auth_id = models.ForeignKey(verbose_name='权限ID', to=ThreadAuth, db_column='auth_id', related_name='+',
                                on_delete=models.DO_NOTHING, default=1)

    title = models.CharField(verbose_name='标题', max_length=200, blank=True, null=True, db_index=True)
    content = UEditorField(verbose_name='内容', blank=True, null=True)
    # content = models.TextField(verbose_name='内容', blank=True, null=True)
    summary = models.CharField(verbose_name='任务摘要', max_length=150, blank=True, null=True, default="")
    ip = models.GenericIPAddressField(verbose_name='IP地址', protocol='both',
                                      default=socket.gethostbyname(socket.gethostname()))  # 只记录创建时的IP

    has_enroll = models.BooleanField(verbose_name='开启报名', default=False)
    has_fee = models.BooleanField(verbose_name='开启小费', default=False)
    has_comment = models.BooleanField(verbose_name='开启评论', default=True)

    cover = models.CharField(verbose_name='封面', max_length=1024, blank=True, null=True)
    video = models.CharField(verbose_name='视频', max_length=1024, blank=True, null=True)
    photos = models.JSONField(verbose_name='照片集', blank=True, null=True)  # 对象数组，存放{id, url} 获取列表时使用，查看详细时再匹配资源表
    files = models.JSONField(verbose_name='文件集', blank=True, null=True)  # 对象数组，存放{id, url}

    price = models.DecimalField(verbose_name='价格', max_digits=32, decimal_places=8, db_index=True, null=True,
                                blank=True)  # add-2022-05-20
    author = models.CharField(verbose_name='作者', max_length=255, blank=True, null=True)  # add-2022-05-20
    is_original = models.BooleanField(verbose_name='是否原创', default=True)  # add-2022-05-20

    create_time = models.DateTimeField(verbose_name='创建时间', default=timezone.now)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)  # 不显示，系统自动填。

    # 用户的修改记录等日志信息，数组对象类型 使用CRC32来比较哪些字段被修改过，并记录
    logs = models.JSONField(verbose_name='日志', blank=True, null=True, default=list)
    more = models.JSONField(verbose_name='更多信息', blank=True, null=True)
    extend = models.ForeignKey(ThreadExtendData, on_delete=models.DO_NOTHING, null=True, blank=True,
                               verbose_name='扩展ID')

    def __str__(self):
        return f"{self.id}"

    # 判断指定字段长度,超出部分用省略号代替
    def short_content(self):
        if len(str(self.content)) > 50:
            return '{}...'.format(str(self.content)[0:50])
        else:
            return str(self.content)

    # 字段数据处理后,字段verbose_name参数失效
    # 需要重新指定,否则列表页字段名显示的是方法名(short_content)
    short_content.short_description = '内容'

    def short_cover(self):
        if len(str(self.cover)) > 15:
            return '{}...'.format(str(self.cover)[0:15])
        else:
            return str(self.cover)

    short_cover.short_description = '封面'

    def short_video(self):
        if len(str(self.video)) > 15:
            return '{}...'.format(str(self.video)[0:15])
        else:
            return str(self.video)

    short_video.short_description = '视频'

    def short_photos(self):
        if len(str(self.photos)) > 15:
            return '{}...'.format(str(self.photos)[0:15])
        else:
            return str(self.photos)

    short_photos.short_description = '照片集'

    def short_files(self):
        if len(str(self.files)) > 15:
            return '{}...'.format(str(self.files)[0:15])
        else:
            return str(self.files)

    short_files.short_description = '文件集'

    def short_logs(self):
        if len(str(self.logs)) > 15:
            return '{}...'.format(str(self.logs)[0:15])
        else:
            return str(self.logs)

    short_logs.short_description = '日志'

    def short_more(self):
        if len(str(self.more)) > 30:
            return '{}...'.format(str(self.more)[0:30])
        else:
            return str(self.logs)

    short_more.short_description = '更多信息'


class ThreadStatistic(models.Model):
    thread_id = models.OneToOneField(Thread, verbose_name='信息主表', on_delete=models.DO_NOTHING, related_name='statistic',
                                     null=True, blank=True)
    flag_classifies = models.CharField(verbose_name='分类**', max_length=255, null=True, blank=True)
    flag_weights = models.CharField(verbose_name='权重**', max_length=255, null=True, blank=True)
    weight = models.FloatField(verbose_name='权重', default=0, db_index=True)
    views = models.IntegerField(verbose_name='浏览数', default=0)
    plays = models.IntegerField(verbose_name='完阅数', default=0)
    comments = models.IntegerField(verbose_name='评论数', default=0)
    likes = models.IntegerField(verbose_name='点赞数', default=0)
    favorite = models.IntegerField(verbose_name='收藏数', default=0)
    shares = models.IntegerField(verbose_name='分享数', default=0)

    class Meta:
        db_table = 'thread_statistic'
        verbose_name = '信息统计表'
        verbose_name_plural = verbose_name


# 标签类型，存放预置标签。用于智能化推送信息，以及关键字检索。未来应设计成根据信息内容自动生成标签。
class ThreadTag(models.Model):
    class Meta:
        db_table = 'thread_tag'
        verbose_name_plural = '标签类型表'

    id = models.AutoField(verbose_name='ID', primary_key=True)
    value = models.CharField(verbose_name='标签名', max_length=255, blank=True, null=True)
    thread = models.ManyToManyField(to='Thread', through='ThreadTagMapping', through_fields=('tag_id', 'thread_id'),
                                    blank=True)

    def __str__(self):
        return f"{self.value}"


# 标签映射，存放数据。即将标签和信息关联起来
class ThreadTagMapping(models.Model):
    class Meta:
        db_table = 'thread_tag_mapping'
        verbose_name_plural = '标签映射表'

    id = models.AutoField(verbose_name='ID', primary_key=True)
    thread_id = models.ForeignKey(verbose_name='信息ID', to=Thread, db_column='thread_id', related_name='+',
                                  on_delete=models.DO_NOTHING)
    tag_id = models.ForeignKey(verbose_name='标签ID', to=ThreadTag, db_column='tag_id', related_name='+',
                               on_delete=models.DO_NOTHING)

    def __str__(self):
        return f"{self.id}"


# 图片权限。作者可以指定上传的图片的访问权限。如公开照片、阅后即焚、已焚毁、红包、红包阅后即焚、红包阅后已焚毁
class ThreadImageAuth(models.Model):
    class Meta:
        db_table = 'thread_image_auth'
        verbose_name_plural = '图片权限表'

    id = models.AutoField(verbose_name='ID', primary_key=True)
    value = models.CharField(verbose_name='值', max_length=255, blank=True, null=True)


# 图片信息表。用于存放图片的各种信息，存放图片地址但不存放图。
class ThreadResource(models.Model):
    class Meta:
        db_table = 'thread_resource'
        verbose_name_plural = '图片表'

    id = models.BigIntegerField(verbose_name='ID', primary_key=True)
    name = models.CharField(verbose_name='图片名称', max_length=255, null=True, blank=True)
    url = models.CharField(verbose_name='图片链接', max_length=1024, null=True, blank=True)
    filename = models.CharField(verbose_name='文件名', max_length=255, null=True, blank=True)
    filetype = models.SmallIntegerField(verbose_name='文件类型', null=True, blank=True)  # 文件类型0:图片，1:视频，2:文件
    format = models.CharField(verbose_name='文件格式', max_length=50)
    image_auth_id = models.ForeignKey(verbose_name='图片权限ID', to=ThreadImageAuth, db_column='image_auth_id',
                                      related_name='+', on_delete=models.DO_NOTHING, null=True, blank=True)
    price = models.DecimalField(verbose_name='价格', max_digits=32, decimal_places=8, db_index=True, null=True,
                                blank=True)
    snapshot = models.JSONField(verbose_name='快照', blank=True, null=True)  # 存放图片的快照数据，如缩略图等。json对象
    logs = models.JSONField(verbose_name='日志', blank=True, null=True)  # 用于存放点击量，点赞量等,数组对象
    # user_id = models.ForeignKey(verbose_name='用户ID', to=User, db_column='user_id', related_name='+', on_delete=models.DO_NOTHING)
    user_id = models.BigIntegerField(verbose_name='用户ID', )
    thread = models.ManyToManyField(to='Thread', through='ThreadToResource',
                                    through_fields=('resource_id', 'thread_id'), blank=True)


# 标签映射，存放数据。即将标签和信息关联起来
class ThreadToResource(models.Model):
    class Meta:
        db_table = 'thread_to_resource'
        verbose_name_plural = '图文关联表'

    id = models.AutoField(verbose_name='ID', primary_key=True)
    thread_id = models.ForeignKey(verbose_name='信息ID', to=Thread, db_column='thread_id', related_name='+',
                                  on_delete=models.DO_NOTHING)
    resource_id = models.ForeignKey(verbose_name='图片ID', to=ThreadResource, db_column='resource_id', related_name='+',
                                    on_delete=models.DO_NOTHING)
