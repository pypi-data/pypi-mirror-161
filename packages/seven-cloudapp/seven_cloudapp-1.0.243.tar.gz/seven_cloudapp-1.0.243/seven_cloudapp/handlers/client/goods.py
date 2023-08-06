# -*- coding: utf-8 -*-
"""
:Author: CaiYouBin
:Date: 2020-05-28 14:50:27
:LastEditTime: 2021-02-07 10:04:49
:LastEditors: HuangJingCan
:description: 商品相关
"""
from seven_cloudapp.handlers.top_base import *

from seven_cloudapp.models.db_models.prize.prize_roster_model import *
from seven_cloudapp.models.db_models.app.app_info_model import *
from seven_cloudapp.models.db_models.recommend.recommend_goods_model import *


class SubmitSkuHandler(SevenBaseHandler):
    """
    :description: 提交SKU
    """
    @filter_check_params("sku_id")
    def get_async(self):
        """
        :description: 提交SKU
        :param user_prize_id：用户中奖信息id
        :param properties_name：sku属性
        :param sku_id：sku_id
        :return 
        :last_editors: HuangJingCan
        """
        app_id = self.get_taobao_param().source_app_id
        open_id = self.get_taobao_param().open_id

        user_prize_id = int(self.get_param("user_prize_id"))
        properties_name = self.get_param("properties_name")
        sku_id = self.get_param("sku_id")

        prize_roster_model = PrizeRosterModel(context=self)
        prize_roster = prize_roster_model.get_entity("id=%s", params=user_prize_id)
        if not prize_roster:
            return self.reponse_json_error("NoUserPrize", "对不起，找不到该奖品")
        if prize_roster.is_sku > 0:
            goods_code_list = self.json_loads(prize_roster.goods_code_list)
            goods_codes = [i for i in goods_code_list if str(i["sku_id"]) == sku_id]

            prize_roster.sku_id = sku_id
            prize_roster.properties_name = properties_name
            if goods_codes and ("goods_code" in goods_codes[0].keys()):
                prize_roster.goods_code = goods_codes[0]["goods_code"]

        prize_roster_model.update_entity(prize_roster)

        return self.reponse_json_success()


class SkuInfoHandler(TopBaseHandler):
    """
    :description: 获取SKU信息
    """
    def get_async(self):
        """
        :description: 获取SKU信息
        :param num_iids：num_iids
        :return
        :last_editors: HuangJingCan
        """
        app_id = self.get_taobao_param().source_app_id
        num_iids = self.get_param("num_iids")

        access_token = ""
        app_info = AppInfoModel(context=self).get_entity("app_id=%s", params=app_id)
        if app_info:
            access_token = app_info.access_token

        return self.get_sku_info(num_iids, access_token)


class GoodsListHandler(TopBaseHandler):
    """
    :description: 获取商品列表
    """
    def get_async(self):
        """
        :description: 获取商品列表
        :param page_index：页索引
        :param page_size：页大小
        :return: 
        :last_editors: HuangJingCan
        """
        app_id = self.get_taobao_param().source_app_id
        page_index = int(self.get_param("page_index", 0))
        page_size = self.get_param("page_size", 200)

        access_token = ""
        app_info = AppInfoModel(context=self).get_entity("app_id=%s", params=app_id)
        if app_info:
            access_token = app_info.access_token

        return self.get_goods_list_client(page_index, page_size, access_token)


class RecommandGoodsHandler(SevenBaseHandler):
    """
    :description: 获取推荐商品列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 获取推荐商品列表
        :param act_id：活动id
        :return: list
        :last_editors: HuangJianYi
        """
        act_id = int(self.get_param("act_id", 0))

        if act_id <= 0:
            return self.reponse_json_error_params()

        recommend_goods = RecommendGoodsModel(context=self).get_entity("act_id=%s", params=act_id)

        if not recommend_goods:
            return self.reponse_json_success([])
        if recommend_goods.is_release == 0:
            return self.reponse_json_success([])

        return self.reponse_json_success(self.json_loads(recommend_goods.goods_list))