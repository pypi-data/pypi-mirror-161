# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-03-24 14:47:27
@LastEditTime: 2021-09-02 11:53:04
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp.handlers.seven_base import *

from seven_cloudapp.models.db_models.exchange.exchange_info_model import *


class ExchangeListHandler(SevenBaseHandler):
    """
    :description: 兑换列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 兑换列表
        :param act_id:活动id
        :return: 
        :last_editors: HuangJianYi
        """
        act_id = int(self.get_param("act_id", 0))

        condition = "act_id=%s"
        exchange_info_model = ExchangeInfoModel(context=self)
        exchange_info_list = exchange_info_model.get_dict_list(condition, order_by="id asc", field="id,goods_type,goods_name,day_limit,need_value,is_release", params=[act_id])

        return self.reponse_json_success(exchange_info_list)


class ExchangeSaveHandler(SevenBaseHandler):
    """
    :description: 保存兑换
    """
    @filter_check_params("act_id,exchange_list")
    def post_async(self):
        """
        :description: 保存兑换
        :param act_id:活动id
        :return: 
        :last_editors: HuangJianYi
        """
        act_id = int(self.get_param("act_id", 0))
        app_id = self.get_param("app_id")

        exchange_info_model = ExchangeInfoModel(context=self)
        exchange_list = self.get_param("exchange_list")
        exchange_list = self.json_loads(exchange_list)
        exchange_info = ExchangeInfo()
        if len(exchange_list) > 0:
            for item in exchange_list:
                if item.__contains__("id"):
                    exchange_info = exchange_info_model.get_entity_by_id(int(item["id"]))
                exchange_info.goods_type = item["goods_type"]
                exchange_info.goods_name = item["goods_name"]
                exchange_info.day_limit = item["day_limit"] if item.__contains__("day_limit") else 0
                exchange_info.need_value = item["need_value"]
                exchange_info.is_release = item["is_release"]
                if exchange_info.id > 0:
                    exchange_info.modify_date = self.get_now_datetime()
                    exchange_info_model.update_entity(exchange_info)
                else:
                    exchange_info.app_id = app_id
                    exchange_info.act_id = act_id
                    exchange_info.create_date = self.get_now_datetime()
                    exchange_info_model.add_entity(exchange_info)

        return self.reponse_json_success()
