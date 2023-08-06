# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-05-26 11:34:07
:LastEditTime: 2020-12-07 16:26:12
:LastEditors: HuangJingCan
:description: 阿里云存储
"""
import oss2
import os

from seven_framework.uuid import *


class OSS2Helper:
    """
    :description: 阿里云存储帮助类
    :param {type} 
    :return: 
    :last_editors: HuangJingCan
    """
    AK_ID = "LTAI4GAV8q6wxi2gqispR4my"
    AK_SECRET = "LWBuIALo4X4pnBDCwiuRjZur1Yhm5h"
    BUCKET_NAME = "mang-he"
    END_POINT = "oss-cn-zhangjiakou.aliyuncs.com"
    DOMAIN = "https://mang-he.oss-cn-zhangjiakou.aliyuncs.com/"

    @classmethod
    def upload(self, file_name, local_file='', folder='', is_auto_name=True, data=None):
        """
        :description: 上传文件
        :param file_name：文件名称
        :param local_file：本地文件地址
        :param is_auto_name：是否生成随机文件名
        :param data：需要上传的数据
        :return: 
        :last_editors: HuangJingCan
        """
        # 文件名
        file_name = os.path.basename(local_file) if local_file != "" else file_name

        if is_auto_name:
            file_extension = os.path.splitext(file_name)[1]
            file_name = UUIDHelper.get_uuid().replace("-", "") + file_extension

        auth = oss2.Auth(self.AK_ID, self.AK_SECRET)
        bucket = oss2.Bucket(auth, self.END_POINT, self.BUCKET_NAME)

        folder = folder.strip('/')
        folder = folder + "/" if folder != "" else folder
        file_name = folder + file_name

        # 上传文件
        # 如果需要上传文件时设置文件存储类型与访问权限，请在put_object中设置相关headers, 参考如下。
        # headers = dict()
        # headers["x-oss-storage-class"] = "Standard"
        # headers["x-oss-object-acl"] = oss2.OBJECT_ACL_PRIVATE
        # result = bucket.put_object('<yourObjectName>', 'content of object', headers=headers)
        if local_file:
            result = bucket.put_object_from_file(file_name, local_file)
        else:
            result = bucket.put_object(file_name, data)

        resource_path = ''
        if result.status == 200:
            resource_path = self.DOMAIN + file_name
            # # HTTP返回码。
            # print('http status: {0}'.format(result.status))
            # # 请求ID。请求ID是请求的唯一标识，强烈建议在程序日志中添加此参数。
            # print('request_id: {0}'.format(result.request_id))
            # # ETag是put_object方法返回值特有的属性。
            # print('ETag: {0}'.format(result.etag))
            # # HTTP响应头部。
            # print('date: {0}'.format(result.headers['date']))

        return resource_path