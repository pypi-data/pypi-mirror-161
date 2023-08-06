# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-11-05 10:13:31
:LastEditTime: 2021-07-08 16:37:00
:LastEditors: HuangJingCan
:description: 奖品相关
"""
from seven_cloudapp.handlers.top_base import *

from seven_cloudapp.models.seven_model import PageInfo
from seven_cloudapp.models.db_models.act.act_info_model import *
from seven_cloudapp.models.db_models.act.act_prize_model import *
from seven_cloudapp.models.db_models.pay.pay_order_model import *
from seven_cloudapp.models.db_models.prize.prize_roster_model import *
from seven_cloudapp.models.db_models.prize.prize_order_model import *


class PrizeListHandler(SevenBaseHandler):
    """
    :description: 奖品列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description:  获取奖品列表
        :param act_id：活动id
        :param machine_id：机台id
        :param page_index：页索引
        :param page_size：页大小
        :return: 分页列表信息
        :last_editors: HuangJingCan
        """
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 20))
        act_id = int(self.get_param("act_id", 0))
        machine_id = int(self.get_param("machine_id", 0))
        ascription_type = int(self.get_param("ascription_type", 0))

        condition = "is_release=1 AND act_id=%s AND ascription_type=%s"
        params = [act_id, ascription_type]

        if machine_id > 0:
            condition += " AND machine_id=%s"
            params.append(machine_id)

        act_prize_page_list, total = ActPrizeModel(context=self).get_dict_page_list("*", page_index, page_size, condition, order_by="sort_index desc", params=params)

        # for act_prize in act_prize_page_list:
        #     try:
        #         act_prize["prize_detail"] = self.json_loads(act_prize["prize_detail"]) if act_prize["prize_detail"] else []
        #     except Exception as ex:
        #         self.logging_link_error(traceback.format_exc())
        #         act_prize["prize_detail"] = []

        page_info = PageInfo(page_index, page_size, total, act_prize_page_list)

        return self.reponse_json_success(page_info)


class AllPrizeListHandler(SevenBaseHandler):
    """
    :description: 所有奖品列表
    """
    @filter_check_params("act_id,machine_id")
    def get_async(self):
        """
        :description:  所有奖品列表
        :param act_id:活动id
        :param machine_id:机台id
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        open_id = self.get_taobao_param().open_id
        act_id = int(self.get_param("act_id", 0))
        machine_id = int(self.get_param("machine_id", 0))

        condition = "is_release=1 AND act_id=%s AND machine_id=%s"

        act_prize_list = ActPrizeModel(context=self).get_dict_list(condition, params=[act_id, machine_id])

        for act_prize in act_prize_list:
            try:
                act_prize["prize_detail"] = self.json_loads(act_prize["prize_detail"]) if act_prize["prize_detail"] else []
            except Exception as ex:
                act_prize["prize_detail"] = []

        return self.reponse_json_success(act_prize_list)


class UserPrizeListHandler(SevenBaseHandler):
    """
    :description: 获取用户奖品列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 获取用户奖品列表
        :param act_id：活动id
        :return status：状态
        :param page_index：页索引
        :param page_size：页大小
        :return: 
        :last_editors: HuangJingCan
        """
        app_id = self.get_taobao_param().source_app_id
        open_id = self.get_taobao_param().open_id
        act_id = int(self.get_param("act_id", 0))
        status = int(self.get_param("status", 0))
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 20))

        condition = "open_id=%s and act_id=%s"
        params = [open_id, act_id]
        order_by = "id desc"

        if status == 0:
            condition += " and prize_order_id=0"
        else:
            condition += " and prize_order_id>0"

        page_list, total = PrizeRosterModel(context=self).get_dict_page_list("*", page_index, page_size, condition, "", order_by, params)

        page_info = PageInfo(page_index, page_size, total, page_list)

        return self.reponse_json_success(page_info)


class SubmitPrizeOrderHandler(SevenBaseHandler):
    """
    :description: 奖品订单提交
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 奖品订单提交
        :param act_id：活动id
        :param login_token：登录令牌
        :param real_name：用户名
        :param telephone：联系电话
        :param province：所在省
        :param city：所在市
        :param county：所在区
        :param street：所在街道
        :param address：收货地址
        :return 
        :last_editors: HuangJingCan
        """
        app_id = self.get_taobao_param().source_app_id
        open_id = self.get_taobao_param().open_id

        act_id = int(self.get_param("act_id", 0))
        login_token = self.get_param("login_token")
        real_name = self.get_param("real_name")
        telephone = self.get_param("telephone")
        province = self.get_param("province")
        city = self.get_param("city")
        county = self.get_param("county")
        street = self.get_param("street")
        address = self.get_param("address")

        user_info = UserInfoModel(context=self).get_entity("act_id=%s and open_id=%s", params=[act_id, open_id])
        if not user_info:
            return self.reponse_json_error("NoUser", "对不起，用户不存在")
        if user_info.user_state == 1:
            return self.reponse_json_error("UserBlock", "对不起，你是黑名单用户,无法提交订单")
        if user_info.login_token != login_token:
            return self.reponse_json_error("ErrorLoginToken", "对不起，帐号已在另一台设备登录,当前无法提交订单")

        act_info_model = ActInfoModel(context=self)
        act_info = act_info_model.get_entity("id=%s and is_del=0 and is_release=1", params=act_id)
        if not act_info:
            return self.reponse_json_error("NoAct", "对不起，活动不存在")

        prize_roster_model = PrizeRosterModel(context=self)
        prize_roster_count = prize_roster_model.get_total("act_id=%s and open_id=%s and prize_order_id=0", params=[act_id, open_id])
        if prize_roster_count == 0:
            return self.reponse_json_error("NoNeedSubmitPrize", "当前没有未提交订单的奖品")

        prize_order_model = PrizeOrderModel(context=self)
        prize_order = PrizeOrder()
        prize_order.app_id = app_id
        prize_order.open_id = open_id
        prize_order.act_id = act_id
        prize_order.user_nick = user_info.user_nick
        prize_order.real_name = real_name
        prize_order.telephone = telephone
        prize_order.province = province
        prize_order.city = city
        prize_order.county = county
        prize_order.street = street
        prize_order.adress = address
        prize_order.create_date = self.get_now_datetime()
        prize_order.modify_date = self.get_now_datetime()
        prize_order.order_no = self.create_order_id()

        prize_order.id = prize_order_model.add_entity(prize_order)

        update_sql = "prize_order_id=%s,prize_order_no=%s"
        where = "act_id=%s and open_id=%s and prize_order_id=0"
        params = [prize_order.id, prize_order.order_no, act_id, open_id]
        prize_roster_model.update_table(update_sql, where, params)

        return self.reponse_json_success()


class PrizeOrderHandler(SevenBaseHandler):
    """
    :description: 用户订单列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 用户订单列表
        :param act_id：活动id
        :param page_index：页索引
        :param page_size：页大小
        :return: PageInfo
        :last_editors: HuangJingCan
        """
        app_id = self.get_taobao_param().source_app_id
        open_id = self.get_taobao_param().open_id
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 20))
        act_id = int(self.get_param("act_id", 0))
        prize_order_id = int(self.get_param("prize_order_id", 0))

        condition = "open_id=%s and act_id=%s"
        params = [open_id, act_id]

        if prize_order_id > 0:
            condition += " and id=%s"
            params.append(prize_order_id)

        prize_order_model = PrizeOrderModel(context=self)
        prize_roster_model = PrizeRosterModel(context=self)
        prize_order_list_dict, total = prize_order_model.get_dict_page_list("*", page_index, page_size, condition, "", "create_date desc", params)
        if prize_order_list_dict:
            prize_order_id_list = [str(i['id']) for i in prize_order_list_dict]
            prize_order_ids = ",".join(prize_order_id_list)
            prize_roster_list_dict = prize_roster_model.get_dict_list("prize_order_id in (" + prize_order_ids + ")")
            for i in range(len(prize_order_list_dict)):
                prize_list = [prize_roster for prize_roster in prize_roster_list_dict if prize_order_list_dict[i]["id"] == prize_roster["prize_order_id"]]
                prize_order_list_dict[i]["prize_list"] = prize_list

        page_info = PageInfo(page_index, page_size, total, prize_order_list_dict)

        return self.reponse_json_success(page_info)


class RosterNoticeHandler(SevenBaseHandler):
    """
    :description: 中奖通告
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 中奖通告
        :param act_id：活动id
        :return 列表
        :last_editors: HuangJingCan
        """
        act_id = int(self.get_param("act_id", 0))

        prize_roster_list_dict = PrizeRosterModel(context=self).get_dict_list("act_id=%s", order_by="id desc", limit="20", params=act_id)

        return self.reponse_json_success(prize_roster_list_dict)


class GetCouponPrizeHandler(TopBaseHandler):
    """
    :description: 领取优惠券（发奖接口）
    """
    @filter_check_params("user_prize_id")
    def get_async(self):
        """
        :description: 领取优惠券（发奖接口）
        :param user_prize_id:用户奖品标识
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        open_id = self.get_taobao_param().open_id
        user_prize_id = int(self.get_param("user_prize_id", 0))
        # self.logging_link_error("Error【优惠券传参user_prize_id】"+ str(user_prize_id))
        app_info = AppInfoModel(context=self).get_entity("app_id=%s", params=app_id)
        if not app_info:
            return self.reponse_json_error("NoApp", "对不起，小程序不存在")
        access_token = app_info.access_token
        if access_token == "":
            return self.reponse_json_error("Error", "未授权，请联系客服授权")

        prize_roster_model = PrizeRosterModel(context=self)
        prize_roster = prize_roster_model.get_dict_by_id(user_prize_id)
        if not prize_roster or prize_roster['open_id'] != open_id:
            return self.reponse_json_error("Error", "对不起,奖品不存在")

        act_prize_model = ActPrizeModel(context=self)
        act_prize = act_prize_model.get_dict_by_id(prize_roster['prize_id'])
        if not act_prize or act_prize['right_ename'] == "" or prize_roster['right_ename'] == "":
            return self.reponse_json_error("Error", "对不起,奖品不是优惠券,无需领取")

        resp = self.benefit_send(act_prize['right_ename'], open_id, access_token)
        # self.logging_link_error("Error【优惠券】"+ str(resp))
        if not resp:
            return self.reponse_json_error("Error", "领取失败")

        if resp["alibaba_benefit_send_response"]:
            if resp["alibaba_benefit_send_response"]["result_success"] == True:
                prize_roster_model.update_table("order_status=1", "id=%s", params=[user_prize_id])
                result = {}
                result["prize_name"] = resp["alibaba_benefit_send_response"]["prize_name"]
                return self.reponse_json_success(result)
            if resp["alibaba_benefit_send_response"]["result_code"] == "COUPON_INVALID_OR_DELETED":
                prize_roster_model.update_table("order_status=2", "id=%s", params=[user_prize_id])
                return self.reponse_json_error("Error", "领取失败：优惠券无效或已删除")
            if resp["alibaba_benefit_send_response"]["result_code"] == "APPLY_SINGLE_COUPON_COUNT_EXCEED_LIMIT":
                return self.reponse_json_error("Error", "领取失败：优惠券超过限额")
            if resp["alibaba_benefit_send_response"]["result_code"] == "USER_PERMISSION_EXCEED_MAX_RIGHT_COUNT_IN_DAY":
                return self.reponse_json_error("Error", "领取失败：同一张优惠券每天限领取一次")
            if resp["alibaba_benefit_send_response"]["result_code"] == "APPLY_ONE_SELLER_COUNT_EXCEED_LIMIT":
                return self.reponse_json_error("Error", "领取失败：用户优惠券超出10张限制")
        else:
            result = resp["sub_msg"] if resp["sub_msg"] else ""
            if result == "" and resp["result_msg"]:
                result = resp["result_msg"]
            return self.reponse_json_error("Error", f"领取失败:{result}")