# -*- coding: utf-8 -*-
"""
:Author: CaiYouBin
:Date: 2020-05-26 15:26:32
@LastEditTime: 2022-02-24 14:58:22
@LastEditors: HuangJianYi
:description: 客户端活动处理
"""
from seven_cloudapp.handlers.seven_base import *

from seven_cloudapp.models.db_models.act.act_info_model import *
from seven_cloudapp.models.db_models.app.app_info_model import *


class ActInfoHandler(SevenBaseHandler):
    """
    :description: 获取活动信息
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 获取活动信息
        :param act_id：活动id
        :return: 字典
        :last_editors: HuangJingCan
        """
        act_id = int(self.get_param("act_id", 0))
        app_id = self.get_taobao_param().source_app_id

        app_info = AppInfoModel(context=self).get_entity("app_id=%s", params=app_id)
        if not app_info:
            return self.reponse_json_error("NoApp", "对不起，找不到该小程序")

        act_dict = ActInfoModel(context=self).get_dict_by_id(act_id)
        if not act_dict:
            return self.reponse_json_error("NoAct", "对不起，找不到该活动")

        act_dict["seller_id"] = app_info.seller_id
        act_dict["store_id"] = app_info.store_id
        act_dict["store_name"] = app_info.store_name
        act_dict["store_icon"] = app_info.store_icon
        act_dict["app_icon"] = app_info.app_icon
        act_dict["task_currency_type"] = self.json_loads(act_dict["task_currency_type"]) if act_dict["task_currency_type"] else {}

        return self.reponse_json_success(act_dict)