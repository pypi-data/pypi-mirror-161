# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-05-26 14:45:44
:LastEditTime: 2021-03-17 11:04:57
:LastEditors: HuangJingCan
:description: 通用Handler
"""
from seven_cloudapp.handlers.seven_base import *


class IndexHandler(SevenBaseHandler):
    """
    :description: 默认页
    """
    def get_async(self):
        """
        :description: 默认页
        :param 
        :return 字符串
        :last_editors: HuangJingCan
        """
        self.write(UUIDHelper.get_uuid() + "_" + config.get_value("run_port") + "_api")