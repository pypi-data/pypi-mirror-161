# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-11-03 16:25:11
:LastEditTime: 2021-03-17 11:13:56
:LastEditors: HuangJingCan
:description: 
"""

from seven_cloudapp.models.db_models.machine.machine_info_model import *
from seven_cloudapp.models.db_models.throw.throw_goods_model import *
from seven_cloudapp.models.db_models.act.act_info_model import *
from seven_cloudapp.models.db_models.act.act_prize_model import *


class ThrowModel():
    """
    :description: 投放相关
    """
    def __init__(self, context=None):
        self.context = context

    def throw_goods_add(self, object_id, app_id, act_id, goods_id, old_act_id, old_goods_id, now_datetime):
        """
        :description: 投放商品处理
        :param object_id：对象id（机台id或者奖品id）
        :param app_id：app_id
        :param act_id：活动id
        :param goods_id：投放id
        :param old_act_id：旧活动id
        :param old_goods_id：旧投放id
        :param now_datetime：当前时间
        :return
        :last_editors: HuangJingCan
        """
        act_info = ActInfoModel(context=self.context).get_dict_by_id(act_id)
        if act_info and act_info["is_throw"] == 1:
            throw_goods_model = ThrowGoodsModel(context=self.context)
            if object_id > 0:
                # 商品ID与之前不同的话，改变原该投放商品的状态，并添加新商品ID
                if goods_id != old_goods_id:
                    machine_info_model = MachineInfoModel(context=self.context)
                    prize_throw_goods_exist = ActPrizeModel(context=self.context).get_dict("act_id=%s and goods_id=%s", params=[act_id, old_goods_id])
                    machine_throw_goods_exist = machine_info_model.get_dict("act_id=%s and goods_id=%s", params=[act_id, old_goods_id])
                    if not prize_throw_goods_exist and not machine_throw_goods_exist:
                        throw_goods_model.update_table("is_throw=0,throw_date=%s,is_sync=0", "act_id=%s and goods_id=%s", params=[now_datetime, old_act_id, old_goods_id])

                    throw_goods = throw_goods_model.get_entity("act_id=%s and goods_id=%s", params=[act_id, goods_id])
                    if not throw_goods:
                        throw_goods = ThrowGoods()
                        throw_goods.app_id = app_id
                        throw_goods.act_id = act_id
                        throw_goods.goods_id = goods_id
                        throw_goods.is_throw = 0
                        throw_goods.is_sync = 0
                        throw_goods_model.add_entity(throw_goods)
            else:
                throw_goods = throw_goods_model.get_entity("act_id=%s and goods_id=%s", params=[act_id, goods_id])
                if not throw_goods:
                    throw_goods = ThrowGoods()
                    throw_goods.app_id = app_id
                    throw_goods.act_id = act_id
                    throw_goods.goods_id = goods_id
                    throw_goods.is_throw = 0
                    throw_goods.is_sync = 0
                    throw_goods_model.add_entity(throw_goods)

    def throw_goods_update(self, act_id, goods_id, now_datetime):
        """
        :description: 投放商品处理
        :param act_id：活动id
        :param goods_id：投放id
        :param now_datetime：当前时间
        :return
        :last_editors: HuangJingCan
        """
        act_info = ActInfoModel(context=self.context).get_dict_by_id(act_id)
        if act_info and act_info["is_throw"] == 1:
            throw_goods_model = ThrowGoodsModel(context=self.context)
            machine_info_model = MachineInfoModel(context=self.context)
            prize_throw_goods_exist = ActPrizeModel(context=self.context).get_dict("act_id=%s and goods_id=%s", params=[act_id, goods_id])
            machine_throw_goods_exist = machine_info_model.get_dict("act_id=%s and goods_id=%s", params=[act_id, goods_id])
            if not prize_throw_goods_exist and not machine_throw_goods_exist:
                throw_goods_model.update_table("is_throw=0,throw_date=%s,is_sync=0", "act_id=%s and goods_id=%s", params=[now_datetime, act_id, goods_id])

    def init_throw_goods_list(self, act_id, app_id, act_name, online_url, goods_id_list, now_datetime):
        """
        :description: 初始化活动投放
        :param act_id:活动id
        :param app_id:app_id
        :param act_name:活动名称
        :param online_url:online_url
        :param goods_id_list:商品id列表
        :return dict
        :last_editors: HuangJingCan
        """
        throw_goods_model = ThrowGoodsModel(context=self.context)

        goods_ids = ",".join([str(i) for i in goods_id_list])

        throw_goods_exist_list = throw_goods_model.get_dict_list("act_id<>%s and goods_id in (" + goods_ids + ")", field="goods_id", params=act_id)
        throw_goods_id_exist_list = [i for i in throw_goods_exist_list]

        throw_goods_list = []

        for goods_id in goods_id_list:
            throw_goods = ThrowGoods()
            throw_goods.app_id = app_id
            throw_goods.act_id = act_id
            throw_goods.goods_id = goods_id
            if goods_id in throw_goods_id_exist_list:
                throw_goods.is_throw = 0
                throw_goods.is_sync = 0
            else:
                throw_goods.is_throw = 1
                throw_goods.is_sync = 1
            throw_goods.create_date = now_datetime
            throw_goods.throw_date = now_datetime
            throw_goods.sync_date = now_datetime
            throw_goods_list.append(throw_goods)

        throw_goods_model.add_list(throw_goods_list)

        result_data = {"url": online_url, "act_name": act_name, "goods_list": goods_id_list}

        return result_data