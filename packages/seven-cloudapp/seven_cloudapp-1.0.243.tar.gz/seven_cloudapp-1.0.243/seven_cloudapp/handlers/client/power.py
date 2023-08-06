# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2021-04-14 15:02:54
@LastEditTime: 2021-06-29 19:23:20
@LastEditors: WangQiang
:Description: 用户权限相关
"""
from seven_cloudapp.handlers.seven_base import *


class GetPowerMenuHandler(SevenBaseHandler):
    """
    :description: 获取权限菜单列表
    """
    def get_async(self):
        """
        :description: 获取权限菜单列表
        :return: dict
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id

        data = self.get_power_menu(app_id)

        return self.reponse_json_success(data)