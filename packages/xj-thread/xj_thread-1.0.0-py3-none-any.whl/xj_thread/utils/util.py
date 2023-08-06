# -*- coding: utf-8 -*-
"""
Created on 2022-04-20
@author:刘飞
@description:
一些公共处理方法
此方法尽量不要引用其他文件的方法，容易出现混合引用问题
"""
import json
import os
import uuid
import logging
import hashlib
import datetime
import string
import secrets
from django.core.cache import cache, caches
from django.conf import settings

log = logging.getLogger()


def get_file_path(instance, filename):
    """文件保存路径"""
    folder = instance.__class__.__name__.lower() + datetime.datetime.now().strftime("/%Y/%m/%d")
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join(folder, filename)


def get_file_path_by_name(folder_name, filename):
    """
    传递名称返回文件相对路径
    """
    folder = folder_name.lower() + datetime.datetime.now().strftime("/%Y/%m/%d")  # 获取
    ext = filename.split('.')
    full_path = os.path.join(settings.MEDIA_ROOT, folder, "%s.%s" % (ext[0], ext[1]))  # 获取文件绝对路径
    flag = True
    while flag:  # 如果有相同名称文件处理[在服务器和内存中都查找]
        if os.path.isfile(full_path) or cache.get(f'{folder}/{filename}'):
            ext[0] = ext[0] + get_rand_str(6)
            filename = "%s.%s" % (ext[0], ext[1])
            full_path = os.path.join(settings.MEDIA_ROOT, folder, "%s.%s" % (ext[0], ext[1]))
        else:
            flag = False
    return "%s/%s" % (folder, filename)


def delete_file_path(file_path):
    """
    根据文件路径删除
    """
    file_path = str(file_path).lstrip('/media/')
    path = os.path.join(settings.MEDIA_ROOT, file_path)
    if os.path.isfile(path):
        os.remove(path)


def delete_file_diff(old_list, new_list):
    """
    根据列表不同删除
    旧的里面有，新的里面没有，即视为删除图片
    """
    [delete_file_path(p) for p in set(old_list).difference(set(new_list))]


def save_file(file_name):
    """
    文件保存，根据文件相对路径拼接后从内存中写入到服务器上
    不管是不是新上传都走进去,不在内存中会跳过
    前后端分离注意：这里传进来的file_name是没有/media/前缀的
    """
    # 这里再处理一下
    file_name = str(file_name).lstrip('/media/')
    file = cache.get(file_name)
    if file:
        filename = os.path.join(settings.MEDIA_ROOT, file_name)  # 资源绝对路径获取
        pos = filename.rfind("/")
        filepath = filename[:pos]
        if not os.path.exists(filepath):  # 资源目录
            os.makedirs(filepath)
        with open(filename, 'wb') as f:
            for chunk in file.chunks():  # 分块写入文件
                f.write(chunk)
        cache.delete(file_name)
    else:
        log.info(f'需要保存的文件在内存中不存在！{file_name}')


def md5(password, salt):
    """密码加密"""
    m = hashlib.md5(bytes(password, encoding='utf-8'))
    # m.update(bytes(salt, encoding='utf-8'))
    m = hashlib.md5(bytes(m.hexdigest() + salt, encoding='utf-8'))
    return m.hexdigest()


def get_rand_str(n):
    """
    生成随机长度的字母数字字符串
    """
    alphabet = string.ascii_letters + string.digits
    res = ''.join(secrets.choice(alphabet) for i in range(n))
    return res


def parse_json(self, json_data):
    """
    格式化json数据，避免json返回时出现字符串json情况
    :param self:
    :param json_data:
    :return:
    """
    for k, v in json_data.items():
        if not type(v) is dict:
            try:
                json_data[k] = json.loads(v)
            except Exception as e:
                json_data[k] = v
        else:
            json_data[k] = self.parse_json(v)
    return json_data
