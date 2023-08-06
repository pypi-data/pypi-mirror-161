# -*- coding: utf-8 -*-
"""
:Author: CaiYouBin
:Date: 2020-06-12 11:04:12
:LastEditTime: 2021-04-16 14:24:12
:LastEditors: HuangJingCan
:description: 
"""
from seven_cloudapp.handlers.seven_base import *

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest


class SendSmsHandler(SevenBaseHandler):
    """
    :description: 发送短信
    """
    def get_async(self):
        """
        :description: 发送短信
        :param thelephone：电话号码
        :return 
        :last_editors: HuangJingCan
        """
        open_id = self.get_taobao_param().open_id
        thelephone = self.get_param("thelephone")
        client = AcsClient('LTAI4FwMYR1FBBui21t7cyh7', 'zyTM5zpYcL8lMXwtDgVoCfHgndoSKi', 'cn-hangzhou')

        result_code = str(random.randint(100000, 999999))
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('dysmsapi.aliyuncs.com')
        request.set_method('POST')
        request.set_protocol_type('https')  # https | http
        request.set_version('2017-05-25')
        request.set_action_name('SendSms')

        request.add_query_param('RegionId', "cn-hangzhou")
        request.add_query_param('PhoneNumbers', thelephone)
        request.add_query_param('SignName', "天志互联")
        request.add_query_param('TemplateCode', "SMS_193145309")
        request.add_query_param('TemplateParam', "{\"code\":" + result_code + "}")

        response = client.do_action(request)

        result = dict(json.loads(response))
        result["result_code"] = result_code
        #记录验证码
        self.redis_init().set("user_" + open_id + "_bind_phone_code", result_code, ex=300)

        return self.reponse_json_success()