# -*- coding: utf-8 -*-
"""
:Author: CaiYouBin
:Date: 2020-06-01 14:07:23
:LastEditTime: 2021-04-16 10:39:58
:LastEditors: HuangJingCan
:description: 商品相关
"""
from seven_cloudapp.handlers.top_base import *

from seven_cloudapp.models.db_models.machine.machine_info_model import *
from seven_cloudapp.models.db_models.price.price_gear_model import *
from seven_cloudapp.models.db_models.act.act_info_model import *
from seven_cloudapp.models.db_models.recommend.recommend_goods_model import *


class GoodsListHandler(TopBaseHandler):
    """
    :description: 导入商品列表（获取当前会话用户出售中的商品列表）
    """
    def get_async(self):
        """
        :description: 导入商品列表（获取当前会话用户出售中的商品列表）
        :param goods_name：商品名称
        :param order_tag：order_tag
        :param order_by：排序类型
        :param page_index：页索引
        :param page_size：页大小
        :return: 列表
        :last_editors: HuangJingCan
        """
        access_token = self.get_taobao_param().access_token
        goods_name = self.get_param("goods_name")
        order_tag = self.get_param("order_tag", "list_time")
        order_by = self.get_param("order_by", "desc")
        page_index = int(self.get_param("page_index", 0))
        page_size = self.get_param("page_size", 10)

        return self.get_goods_list(page_index, page_size, goods_name, order_tag, order_by, access_token)


class GoodsListByGoodsIDHandler(TopBaseHandler):
    """
    :description: 根据商品id获取商品列表
    """
    @filter_check_params("goods_ids")
    def get_async(self):
        """
        :description: 根据商品id获取商品列表
        :param goods_id：商品id
        :param is_check_exist：是否存在
        :return: list
        :last_editors: HuangJingCan
        """
        access_token = self.get_taobao_param().access_token
        goods_ids = self.get_param("goods_ids")

        resp = self.get_goods_list_for_goodsids(goods_ids, access_token)

        if "error_message" in resp.keys():
            return self.reponse_json_error("Error", resp["error_message"])

        return self.reponse_json_success(resp)


class GoodsInfoHandler(TopBaseHandler):
    """
    :description: 获取商品信息
    """
    @filter_check_params("goods_id")
    def get_async(self):
        """
        :description: 获取商品信息
        :param goods_id：商品id
        :param machine_id：机台id
        :param is_check_exist：是否存在
        :return: 商品信息
        :last_editors: HuangJingCan
        """
        access_token = self.get_taobao_param().access_token
        num_iid = self.get_param("goods_id")
        machine_id = int(self.get_param("machine_id", 0))
        is_check_machine_exist = int(self.get_param("is_check_exist", 0))

        if is_check_machine_exist > 0:
            exist_machineed = MachineInfoModel(context=self).get_dict("goods_id=%s and id<>%s", params=[num_iid, machine_id])
            if exist_machineed:
                return self.reponse_json_error("ExistGoodsID", "对不起，当前商品ID已应用到其他盒子中")

        return self.get_goods_info(num_iid, access_token)


class GoodsCheckHandler(TopBaseHandler):
    """
    :description: 校验商品
    """
    @filter_check_params("goods_id,act_id")
    def get_async(self):
        """
        :description: 校验商品
        :param goods_id：商品id
        :param act_id：活动id
        :return: 商品信息
        :last_editors: HuangJingCan
        """
        access_token = self.get_taobao_param().access_token
        num_iid = self.get_param("goods_id")
        act_id = int(self.get_param("act_id", 0))

        condition = "act_id!=%s and goods_id=%s"
        price_gear_dict = PriceGearModel(context=self).get_dict(condition, params=[act_id, num_iid])
        if price_gear_dict:
            act_dict = ActInfoModel(context=self).get_dict_by_id(price_gear_dict['act_id'])
            actName = act_dict['act_name'] if act_dict else ""
            return self.reponse_json_error("ParamError", f"此商品ID已关联活动{actName},无法使用！")
        else:
            return self.get_goods_info(num_iid, access_token)


class GetCouponDetails(TopBaseHandler):
    """
    :description: 获取优惠券详情信息
    """
    def get_async(self):
        """
        :description: 获取优惠券详情信息
        :param right_ename:奖池ID
        :return: dict
        :last_editors: LaiKaiXiang
        """
        right_ename = self.get_param("right_ename")

        return self.get_coupon_details(right_ename)


class RecommendGoodsHandler(SevenBaseHandler):
    """ 
    保存爆品推荐
    """
    @filter_check_params("act_id,app_id")
    def post_async(self):
        """
        :description: 保存爆品推荐
        :param app_id：app_id
        :param act_id：act_id
        :param goods_ids：推荐商品id(逗号,分隔)
        :param goods_list：推荐商品列表
        :param is_open：是否开启
        :return reponse_json_success
        :last_editors: LaiKaiXiang
        """
        act_id = int(self.get_param("act_id", 0))
        app_id = self.get_param("app_id")
        is_release = int(self.get_param("is_open", 0))
        goods_ids = self.get_param("goods_ids")
        goods_list = self.get_param("goods_list")
        goods_list = goods_list if goods_list != "" else []

        if act_id <= 0:
            return self.reponse_json_error_params()

        recommend_goods_model = RecommendGoodsModel(context=self)
        recommend_goods = recommend_goods_model.get_entity("act_id=%s", params=act_id)
        if recommend_goods:
            recommend_goods.is_release = is_release
            recommend_goods.goods_ids = goods_ids
            recommend_goods.goods_list = goods_list
            recommend_goods.modify_date = self.get_now_datetime()
            recommend_goods_model.update_entity(recommend_goods)
        else:
            recommend_goods = RecommendGoods()
            recommend_goods.act_id = act_id
            recommend_goods.app_id = app_id
            recommend_goods.is_release = is_release
            recommend_goods.goods_ids = goods_ids
            recommend_goods.goods_list = goods_list
            recommend_goods.create_date = self.get_now_datetime()
            recommend_goods_model.add_entity(recommend_goods)

        return self.reponse_json_success()


class RecommendGoodsInfoHandler(SevenBaseHandler):
    """
    获取爆品推荐列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 获取爆品推荐列表
        :param act_id：act_id
        :return list
        :last_editors: LaiKaiXiang
        """
        act_id = int(self.get_param("act_id", 0))

        if act_id <= 0:
            return self.reponse_json_error_params()

        recommend_goods = RecommendGoodsModel(context=self).get_entity("act_id=%s", params=act_id)

        if recommend_goods:
            recommend_goods.goods_list = self.json_loads(recommend_goods.goods_list) if recommend_goods.goods_list else []

        return self.reponse_json_success(recommend_goods)