"""
Created on 2022-04-11
@author:刘飞
@description:发布子模块序列化器
"""
from django.utils.translation import gettext as tr
from rest_framework import serializers

from xj_user.models import BaseInfo, DetailInfo
from .models import (ThreadShow,
                     ThreadClassify,
                     ThreadCategory,
                     ThreadAuth,
                     Thread,
                     ThreadStatistic,
                     ThreadTag,
                     ThreadTagMapping, ThreadExtendData)
from .utils.model_handle import parse_model


class ThreadShowListSerializer(serializers.ModelSerializer):
    """展示类型序列化器"""
    label = serializers.SerializerMethodField()

    class Meta:
        model = ThreadShow
        fields = '__all__'

    def get_label(self, instance):
        return tr(instance.value)


class ThreadClassifyListSerializer(serializers.ModelSerializer):
    """分类序列化器"""
    label = serializers.SerializerMethodField()

    class Meta:
        model = ThreadClassify
        fields = '__all__'

    def get_label(self, instance):
        return tr(instance.value)


class ThreadCategoryListSerializer(serializers.ModelSerializer):
    """类别序列化"""
    label = serializers.SerializerMethodField()

    class Meta:
        model = ThreadCategory
        fields = '__all__'

    def get_label(self, instance):
        return tr(instance.value)


class ThreadAuthListSerializer(serializers.ModelSerializer):
    """访问权限序列化"""
    label = serializers.SerializerMethodField()

    class Meta:
        model = ThreadAuth
        fields = '__all__'

    def get_label(self, instance):
        return tr(instance.value)


class ThreadStatisticListSerializer(serializers.ModelSerializer):
    """信息统计表序列化器"""

    class Meta:
        model = ThreadStatistic
        fields = '__all__'


class ThreadTagSerializer(serializers.ModelSerializer):
    """标签类型序列化器"""

    class Meta:
        model = ThreadTag
        exclude = ['thread']


class ThreadListSerializer(serializers.ModelSerializer):
    """信息表，即主表序列化"""

    create_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    update_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    # category_value = serializers.SerializerMethodField()
    # classify_value = serializers.SerializerMethodField()
    show_value = serializers.SerializerMethodField()
    # auth_value = serializers.SerializerMethodField()
    # classify_label = serializers.SerializerMethodField()
    # auth_label = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    statistic = serializers.SerializerMethodField()
    tag_list = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Thread
        fields = [
            'id',
            'create_time',
            'update_time',
            # 'category_value',
            # 'classify_value',
            # 'auth_value',
            # 'auth_label',
            'statistic',
            'full_name',
            'avatar',
            'is_deleted',
            'user_id',
            'title',
            # 'content',
            'summary',
            # 'ip',
            # 'has_enroll',
            'has_fee',
            # 'has_comment',
            'cover',
            # 'video',
            'photos',
            'files',
            'price',
            'author',
            # 'is_original',
            # 'more',
            'category_id',
            'classify_id',
            'show_id',
            'show_value',
            'auth_id',
            'tag_list',
        ]
        # exclude = ('logs',)
        # fields = '__all__'

    def get_avatar(self, instance):
        user_detail_obj = DetailInfo.objects.filter(user_id=instance.user_id).first()
        avatar = user_detail_obj.avatar if user_detail_obj else None
        return avatar

    def get_category_value(self, instance):
        category_value = instance.category_id.value if instance.category_id else None
        return category_value

    def get_classify_value(self, instance):
        classify_value = instance.classify_id.value if instance.classify_id else None
        return classify_value

    def get_show_value(self, instance):
        show_value = instance.show_id.value if instance.show_id else None
        return show_value

    def get_auth_value(self, instance):
        auth_value = instance.auth_id.value if instance.auth_id else None
        return auth_value

    def get_classify_label(self, instance):
        classify_value = tr(instance.classify_id.value) if instance.classify_id else None
        return classify_value

    def get_auth_label(self, instance):
        auth_value = tr(instance.auth_id.value) if instance.auth_id else None
        return auth_value

    def get_full_name(self, instance):
        user_obj = BaseInfo.objects.filter(id=instance.user_id).first()
        full_name = user_obj.full_name if user_obj else None
        return full_name

    def get_statistic(self, instance):
        obj = ThreadStatistic.objects.filter(thread_id=instance).first()
        data = ThreadStatisticListSerializer(obj)
        return data.data

    def get_tag_list(self, instance):
        tag_list = []
        tag_id_list = ThreadTagMapping.objects.filter(thread_id=instance).values_list('tag_id', flat=True)
        tag_obj = ThreadTag.objects.filter(id__in=tag_id_list)
        for t in tag_obj:
            tag_list.append({"id": t.id, "value": t.value})
        return tag_list


class ThreadDetailSerializer(serializers.ModelSerializer):
    """信息表，即主表详情序列化"""

    create_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    update_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    category_value = serializers.SerializerMethodField()
    classify_value = serializers.SerializerMethodField()
    show_value = serializers.SerializerMethodField()
    auth_value = serializers.SerializerMethodField()
    category_label = serializers.SerializerMethodField()
    classify_label = serializers.SerializerMethodField()
    show_label = serializers.SerializerMethodField()
    auth_label = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    nickname = serializers.SerializerMethodField()
    statistic = serializers.SerializerMethodField()
    tag_list = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Thread
        # exclude = ('logs',)
        fields = '__all__'

    def get_avatar(self, instance):
        user_detail_obj = DetailInfo.objects.filter(user_id=instance.user_id).first()
        avatar = user_detail_obj.avatar if user_detail_obj else None
        return avatar

    def get_category_value(self, instance):
        category_value = instance.category_id.value if instance.category_id else None
        return category_value

    def get_classify_value(self, instance):
        classify_value = instance.classify_id.value if instance.classify_id else None
        return classify_value

    def get_show_value(self, instance):
        show_value = instance.show_id.value if instance.show_id else None
        return show_value

    def get_auth_value(self, instance):
        auth_value = instance.auth_id.value if instance.auth_id else None
        return auth_value

    def get_category_label(self, instance):
        category_value = tr(instance.category_id.value) if instance.category_id else None
        return category_value

    def get_classify_label(self, instance):
        classify_value = tr(instance.classify_id.value) if instance.classify_id else None
        return classify_value

    def get_show_label(self, instance):
        show_value = tr(instance.show_id.value) if instance.show_id else None
        return show_value

    def get_auth_label(self, instance):
        auth_value = tr(instance.auth_id.value) if instance.auth_id else None
        return auth_value

    def get_full_name(self, instance):
        user_obj = BaseInfo.objects.filter(id=instance.user_id).first()
        full_name = user_obj.full_name if user_obj else None
        return full_name

    def get_user_name(self, instance):
        user_obj = BaseInfo.objects.filter(id=instance.user_id).first()
        user_name = user_obj.user_name if user_obj else None
        return user_name

    def get_nickname(self, instance):
        user_obj = BaseInfo.objects.filter(id=instance.user_id).first()
        nickname = user_obj.nickname if user_obj else None
        return nickname

    def get_statistic(self, instance):
        obj = ThreadStatistic.objects.filter(thread_id=instance).first()
        data = ThreadStatisticListSerializer(obj)
        return data.data

    def get_tag_list(self, instance):
        tag_list = []
        tag_id_list = ThreadTagMapping.objects.filter(thread_id=instance).values_list('tag_id', flat=True)
        tag_obj = ThreadTag.objects.filter(id__in=tag_id_list)
        for t in tag_obj:
            tag_list.append({"id": t.id, "value": t.value})
        return tag_list


class ThreadV2ListSerializer(serializers.ModelSerializer):
    """信息表，即主表序列化"""

    extend_child = serializers.SerializerMethodField()

    def get_extend_child(self, instance):
        try:
            return parse_model(ThreadExtendData.objects.filter(id=instance.extend.id))[0]
        except Exception as e:
            # 外键不存在的似乎后
            return []

    class Meta:
        model = Thread
        fields = [
            'id',
            'create_time',
            'title',
            'summary',
            'has_fee',
            'cover',
            'photos',
            'files',
            'price',
            'author',
            'category_id',
            'classify_id',
            'show_id',
            'extend',
            'extend_child'
        ]
