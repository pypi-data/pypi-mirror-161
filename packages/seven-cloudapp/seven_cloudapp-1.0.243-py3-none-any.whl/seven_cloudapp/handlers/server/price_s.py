# -*- coding: utf-8 -*-
"""
:Author: HuangJianYi
:Date: 2020-06-22 10:30:00
:LastEditTime: 2021-07-28 10:21:52
:LastEditors: HuangJingCan
:description: 价格档位
"""
from seven_cloudapp.handlers.seven_base import *

from seven_cloudapp.models.enum import OperationType
from seven_cloudapp.models.seven_model import PageInfo
from seven_cloudapp.models.db_models.price.price_gear_model import *
from seven_cloudapp.models.db_models.throw.throw_goods_model import *
from seven_cloudapp.models.db_models.act.act_info_model import *
# from seven_cloudapp.models.db_models.machine.machine_info_model import *


class PriceHandler(SevenBaseHandler):
    """
    :description: 保存价格档位
    """
    @filter_check_params("app_id,act_id,price")
    def get_async(self):
        """
        :description: 保存价格档位
        :param app_id：app_id
        :param price_gear_id：价格挡位id
        :param act_id：活动id
        :param price：价格
        :param goods_id：商品id
        :param sku_id：sku_id
        :param remarks：备注
        :return: reponse_json_success
        :last_editors: HuangJianYi
        """
        app_id = self.get_param("app_id")
        open_id = self.get_taobao_param().open_id
        price_gear_id = int(self.get_param("price_gear_id", 0))
        act_id = int(self.get_param("act_id", 0))
        relation_type = int(self.get_param("relation_type", 1))
        price = self.get_param("price")
        price_gear_name = self.get_param("price_gear_name")
        price_gear_pic = self.get_param("price_gear_pic")
        goods_id = self.get_param("goods_id")
        sku_id = self.get_param("sku_id")
        remarks = self.get_param("remarks")

        if act_id <= 0:
            return self.reponse_json_error_params()

        price_gear = None
        old_price_gear = None
        price_gear_model = PriceGearModel(context=self)
        if price_gear_id > 0:
            price_gear = price_gear_model.get_entity_by_id(price_gear_id)

        is_add = False
        if not price_gear:
            is_add = True
            price_gear = PriceGear()
        else:
            old_price_gear = deepcopy(price_gear)

        try:
            price = decimal.Decimal(price)
        except Exception as ex:
            # self.logging_link_error(str(ex) + "【保存价格档位】")
            return self.reponse_json_error("ParamError", "参数price类型错误")

        if goods_id != "":
            condition = "act_id!=%s and goods_id=%s"
            price_gear_goodsid = price_gear_model.get_entity(condition, params=[act_id, goods_id])
            if price_gear_goodsid:
                act_info = ActInfoModel(context=self).get_dict_by_id(price_gear_goodsid.act_id)
                actName = act_info["act_name"] if act_info else ""
                return self.reponse_json_error("Error", f"此商品ID已关联活动{actName},无法使用")

        price_gear.act_id = act_id
        price_gear.app_id = app_id
        price_gear.relation_type = relation_type
        price_gear.price = price
        price_gear.price_gear_name = price_gear_name
        price_gear.price_gear_pic = price_gear_pic
        price_gear.goods_id = goods_id
        price_gear.sku_id = sku_id
        price_gear.remarks = remarks
        price_gear.modify_date = self.get_now_datetime()

        if is_add:
            if sku_id != "":
                price_gear_goodsid_skuid = price_gear_model.get_entity("sku_id=%s", params=[sku_id])
                if price_gear_goodsid_skuid:
                    return self.reponse_json_error("Error", f"当前SKUID已绑定价格档位,请更换")
            price_gear.effective_date = self.get_now_datetime()
            price_gear.id = price_gear_model.add_entity(price_gear)
            # 记录日志
            self.create_operation_log(OperationType.add.value, price_gear.__str__(), "PriceHandler", None, self.json_dumps(price_gear))
        else:
            if sku_id != "":
                price_gear_goodsid_skuid = price_gear_model.get_entity("id!=%s and sku_id=%s", params=[price_gear.id, sku_id])
                if price_gear_goodsid_skuid:
                    return self.reponse_json_error("Error", f"当前SKUID已绑定价格档位,请更换")
            price_gear_model.update_entity(price_gear)
            # 记录日志
            self.create_operation_log(OperationType.update.value, price_gear.__str__(), "PriceHandler", self.json_dumps(old_price_gear), self.json_dumps(price_gear))

        self.throw_goods_add(price_gear_id, price_gear, old_price_gear)

        return self.reponse_json_success(price_gear.id)

    def throw_goods_add(self, price_gear_id, price_gear, old_price_gear):
        """
        :description: 投放商品处理
        :param price_gear_id：价格挡位id
        :param price_gear：价格挡位对象
        :param old_price_gear：旧价格挡位对象
        :return: 
        :last_editors: HuangJianYi
        """
        act_info = ActInfoModel(context=self).get_dict_by_id(price_gear.act_id)
        if act_info and act_info["is_throw"] == 1:
            throw_goods_model = ThrowGoodsModel(context=self)
            if price_gear_id > 0:
                # 商品ID与之前不同的话，改变原该投放商品的状态，并添加新商品ID
                if price_gear.goods_id != old_price_gear.goods_id:
                    prize_gear_model = PriceGearModel(context=self)
                    gear_throw_goods_exist = prize_gear_model.get_entity("act_id=%s and goods_id=%s", params=[price_gear.act_id, old_price_gear.goods_id])
                    if not gear_throw_goods_exist:
                        throw_goods_model.update_table("is_throw=0,throw_date=%s,is_sync=0", "act_id=%s and goods_id=%s", params=[self.get_now_datetime(), old_price_gear.act_id, old_price_gear.goods_id])

                    throw_goods = throw_goods_model.get_entity("act_id=%s and goods_id=%s", params=[price_gear.act_id, price_gear.goods_id])
                    if not throw_goods:
                        throw_goods = ThrowGoods()
                        throw_goods.app_id = price_gear.app_id
                        throw_goods.act_id = price_gear.act_id
                        throw_goods.goods_id = price_gear.goods_id
                        throw_goods.is_throw = 0
                        throw_goods.is_sync = 0
                        throw_goods_model.add_entity(throw_goods)
            else:
                throw_goods = throw_goods_model.get_entity("act_id=%s and goods_id=%s", params=[price_gear.act_id, price_gear.goods_id])
                if not throw_goods:
                    throw_goods = ThrowGoods()
                    throw_goods.app_id = price_gear.app_id
                    throw_goods.act_id = price_gear.act_id
                    throw_goods.goods_id = price_gear.goods_id
                    throw_goods.is_throw = 0
                    throw_goods.is_sync = 0
                    throw_goods_model.add_entity(throw_goods)


class PriceListHandler(SevenBaseHandler):
    """
    :description: 获取价格档位列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 获取价格档位列表
        :param act_id：活动id
        :param page_index：页索引
        :param page_size：页大小
        :return: 列表
        :last_editors: HuangJianYi
        """
        act_id = int(self.get_param("act_id", 0))
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 10))

        if act_id <= 0:
            return self.reponse_json_error_params()

        page_list, total = PriceGearModel(context=self).get_dict_page_list("*", page_index, page_size, "act_id=%s and is_del=0", "", "id desc", act_id)

        page_info = PageInfo(page_index, page_size, total, page_list)

        return self.reponse_json_success(page_info)


class PriceListRecoverHandler(SevenBaseHandler):
    """
    :description: 价格档位回收站
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 价格档位回收站
        :param act_id：活动id
        :param page_index：页索引
        :param page_size：页大小
        :return: 列表
        :last_editors: HuangJianYi
        """
        act_id = int(self.get_param("act_id", 0))
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 10))

        if act_id <= 0:
            return self.reponse_json_error_params()

        page_list, total = PriceGearModel(context=self).get_dict_page_list("*", page_index, page_size, "act_id=%s and is_del=1", "", "id desc", act_id)

        page_info = PageInfo(page_index, page_size, total, page_list)

        return self.reponse_json_success(page_info)


class PriceStatusHandler(SevenBaseHandler):
    """
    :description: 价格档位删除和恢复
    """
    @filter_check_params("price_gear_id")
    def get_async(self):
        """
        :description: 删除价格档位
        :param app_id：app_id
        :param price_gear_id：价格档位id
        :param status：状态
        :return: 
        :last_editors: HuangJianYi
        """
        open_id = self.get_taobao_param().open_id
        app_id = self.get_param("app_id")
        price_gear_id = int(self.get_param("price_gear_id", 0))
        status = int(self.get_param("status", 0))
        if status > 0:
            status = 1
        if price_gear_id <= 0:
            return self.reponse_json_error_params()
        price_gear_model = PriceGearModel(context=self)
        # machine_info_model = MachineInfoModel(context=self)
        # machine_info = machine_info_model.get_entity("app_id=%s and price_gears_id=%s", params=[app_id,price_gear_id])
        # if machine_info:
        #     return self.reponse_json_error("Error", "当前档位已关联中盒,请取消关联再删除")
        price_gear = price_gear_model.get_entity_by_id(price_gear_id)
        price_gear_model.update_table("is_del=%s,goods_id='',sku_id=''", "id=%s", [status, price_gear_id])
        if status == 1:
            self.throw_goods_update(price_gear)
            # 记录日志
            self.create_operation_log(OperationType.delete.value, "price_gear_tb", "PriceStatusHandler", None, price_gear_id)

        return self.reponse_json_success()

    def throw_goods_update(self, price_gear):
        """
        :description: 投放商品处理
        :param price_gear：价格挡位
        :return: 
        :last_editors: HuangJianYi
        """
        act_info = ActInfoModel(context=self).get_dict_by_id(price_gear.act_id)
        if act_info and act_info["is_throw"] == 1:
            ThrowGoodsModel(context=self).update_table("is_throw=0,throw_date=%s,is_sync=0", "act_id=%s and goods_id=%s", params=[self.get_now_datetime(), price_gear.act_id, price_gear.goods_id])