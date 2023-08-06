import datetime

from django.db.models import F
from django.db.models import Q
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *


class ThreadListAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = '__all__'


class ThreadListAPIView(APIView):
    permission_classes = (AllowAny,)  # 允许所有用户
    params = None

    print(35 * "-", "api", 35 * "-")

    def get(self, request, format=None):
        self.params = request.query_params  # 返回QueryDict类型

        # 分页
        page = int(self.params['page']) - 1 if 'page' in self.params else 0
        size = int(self.params['size']) if 'size' in self.params else 10

        if 'category_id' not in self.params or self.params['category_id'] == '':
            return Response({'err': 1, 'msg': '缺少参数category_id', 'data': [], 'request': self.params, })

        threads = Thread.objects.all().filter(Q(category_id=self.params['category_id'])).order_by('id')

        if 'classify_id' in self.params:
            threads = Thread.objects.all().filter(
                Q(category_id=self.params['category_id']) &
                Q(classify_id=self.params['classify_id'])
            ).order_by('id')

        if 'title' in self.params:
            threads = Thread.objects.all().filter(
                Q(category_id=self.params['category_id']) &
                Q(title__contains=self.params['title'])
            ).order_by('id')

        if 'content' in self.params:
            threads = Thread.objects.all().filter(
                Q(category_id=self.params['category_id']) &
                Q(content__contains=self.params['content'])
            ).order_by('id')

        if 'classify_id' in self.params and 'title' in self.params:
            threads = Thread.objects.all().filter(
                Q(category_id=self.params['category_id']) &
                Q(classify_id=self.params['classify_id']) &
                Q(title__contains=self.params['title'])
            ).order_by('id')

        if 'classify_id' in self.params and 'content' in self.params:
            threads = Thread.objects.all().filter(
                Q(category_id=self.params['category_id']) &
                Q(classify_id=self.params['classify_id']) &
                Q(content__contains=self.params['content'])
            ).order_by('id')

        if 'title' in self.params and 'content' in self.params:
            threads = Thread.objects.all().filter(
                Q(category_id=self.params['category_id']) &
                Q(title__icontains=self.params['title']) &
                Q(content__icontains=self.params['content'])
            ).order_by('id')

        today = datetime.datetime.now()
        if 'start_time' in self.params:
            start_date = datetime.datetime.strptime(self.params['start_time'], '%Y-%m-%d')
            print(">>>start_date ", start_date)

            if start_date <= today:
                threads = Thread.objects.all().filter(
                    Q(category_id=self.params['category_id']),
                    create_time__range=[start_date, today]
                ).order_by('id')

        if 'end_time' in self.params:
            end_date = datetime.datetime.strptime(self.params['end_time'] + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
            print(">>>end_date ", end_date)

            if end_date >= today:
                threads = Thread.objects.all().filter(
                    Q(category_id=self.params['category_id']),
                    create_time__range=[today, end_date]
                ).order_by('id')

        if 'start_time' in self.params and 'end_time' in self.params:
            start_date = datetime.datetime.strptime(self.params['start_time'], '%Y-%m-%d')
            end_date = datetime.datetime.strptime(self.params['end_time'] + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
            print(">>>start_date ", start_date)
            print(">>>end_date ", end_date)

            if start_date <= today <= end_date:
                threads = Thread.objects.all().filter(
                    Q(category_id=self.params['category_id']),
                    create_time__range=[start_date, end_date]
                ).order_by('id')

        # if 'tags' in self.params:
        #     tags_arrr = self.params['tags'].split(",")
        #
        #     for index in range(len(tags_arrr)):
        #         # 查询是否存在该标签id
        #         threadTags = ThreadTag.objects.all().filter(Q(label=tags_arrr[index])).values('id')
        #         print(">>>", threadTags)



        #         mappings = ThreadTagMapping.objects.update_or_create(tag_id=threadTags,thread=111, id=1)
        #         print(">>>mappings ", mappings)

        #         如果不存在
        #         if not threadTags.exists():
        #             return Response({'err': 1, 'msg': '不存在该标签ID：'+tag_list_arrr[index], 'data': [], 'request': self.params, })
        #         如果存在，则获取eh_thread_tag表的ID，并记录到eh_thread_tag_mapping的tag_id和thread_id
        #         if threadTags.exists():
        #             tag_id = ThreadTag.objects.filter(Q(label))

        # print(">>>sql:")
        # print(threadTags.query)
        # print("\n")

        total = threads.count()
        now_pages = threads[page * size:page * size + size] if page >= 0 else threads
        data = now_pages.annotate(
            thread_category=F('category__label'),
            thread_classify=F('classify__classify'),
            show_type=F('show__label'),
            username=F('user__username'),
            thread_auth=F('auth__label'),
        ).values(
            'id',
            'thread_category',
            'thread_classify',
            'show_type',
            'username',
            'thread_auth',
            'title',
            'content',
            'has_enroll',
            'has_fee',
            'has_comment',
            'cover',
            'photos',
            'video',
            'create_time',
            'update_time',
            'weight',
            'views',
            'plays',
            'comments',
            'likes',
            'favorite',
            'shares',
        )
        return Response({
            'err': 0,
            'msg': 'OK',
            'data': {'total': total, 'list': data, },
            'request': self.params,
        })
