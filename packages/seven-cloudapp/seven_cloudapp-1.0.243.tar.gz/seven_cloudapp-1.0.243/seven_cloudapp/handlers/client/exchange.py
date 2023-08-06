# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-03-11 14:45:09
@LastEditTime: 2022-03-04 10:25:51
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp.handlers.seven_base import *
from seven_cloudapp.handlers.top_base import *
from seven_cloudapp.models.db_models.act.act_info_model import *
from seven_cloudapp.models.db_models.user.user_info_model import *
from seven_cloudapp.models.db_models.lottery.lottery_value_log_model import *
from seven_cloudapp.models.db_models.exchange.exchange_info_model import *
from seven_cloudapp.models.db_models.user.user_detail_model import *
from seven_cloudapp.models.db_models.prop.prop_log_model import *


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
        condition = "act_id=%s and is_release=1"
        exchange_info_model = ExchangeInfoModel(context=self)
        result = {}
        result["tool_list"] = []
        exchange_info_list = exchange_info_model.get_dict_list(condition, order_by="id asc", params=[act_id])
        if len(exchange_info_list) > 0:
            for item in exchange_info_list:
                data = {}
                if int(item["goods_type"]) == 2:
                    data["goods_detail"] = "可额外获得一次显示机会"
                elif int(item["goods_type"]) == 3:
                    data["goods_detail"] = "可额外获得一次提示机会"
                else:
                    data["goods_detail"] = "可重新获得一次抽盒机会"
                data["exchange_id"] = item["id"]
                data["goods_type"] = item["goods_type"]
                data["goods_name"] = item["goods_name"]
                data["day_limit"] = item["day_limit"]
                data["need_value"] = item["need_value"]
                result["tool_list"].append(data)

        return self.reponse_json_success(result)


class ExchangeHandler(TopBaseHandler):
    """
    :description: 兑换
    """
    @filter_check_params("act_id,exchange_id,login_token")
    def get_async(self):
        """
        :param act_id：活动id
        :param user_id：用户id
        :param exchange_id:兑换id
        :param login_token:用户访问令牌
        :return: 
        :last_editors: HuangJianYi
        """
        open_id = self.get_taobao_param().open_id
        app_id = self.get_taobao_param().source_app_id
        exchange_id = int(self.get_param("exchange_id", 0))
        login_token = self.get_param("login_token")
        act_id = int(self.get_param("act_id", 0))

        db_transaction = DbTransaction(db_config_dict=config.get_value("db_cloudapp"))
        act_info_model = ActInfoModel(context=self)
        user_info_model = UserInfoModel(db_transaction=db_transaction, context=self)
        exchange_info_model = ExchangeInfoModel(db_transaction=db_transaction, context=self)
        prop_log_model = PropLogModel(db_transaction=db_transaction, context=self)
        user_detail_model = UserDetailModel(db_transaction=db_transaction, context=self)
        lottery_value_log_model = LotteryValueLogModel(db_transaction=db_transaction, context=self)

        #请求太频繁限制
        if self.check_post(f"ExchangeHandler_Get_{str(open_id)}") == False:
            return self.reponse_json_error("HintMessage", "对不起，请求太频繁")

        exchange_info = exchange_info_model.get_entity_by_id(exchange_id)
        if not exchange_info or exchange_info.is_release == 0:
            return self.reponse_json_error("Error", "对不起，当前兑换不存在")
        #获取当前用户
        user_info = user_info_model.get_entity("act_id=%s and open_id=%s", params=[act_id, open_id])
        if not user_info:
            return self.reponse_json_error("NoUser", "对不起，用户不存在")

        history_value = 0
        user_detail = user_detail_model.get_entity("act_id=%s and open_id=%s", params=[act_id, open_id])
        if user_detail:
            if exchange_info.goods_type == 2:
                history_value = user_detail.perspective_card_count
            elif exchange_info.goods_type == 3:
                history_value = user_detail.tips_card_count
            elif exchange_info.goods_type == 4:
                history_value = user_detail.redraw_card_count
        act_dict = act_info_model.get_dict("id=%s and is_release=1", params=act_id)
        if not act_dict:
            return self.reponse_json_error("NoAct", "对不起，活动不存在")
        if user_info.user_state == 1:
            return self.reponse_json_error("UserState", "账号异常，请联系客服处理")
        if user_info.login_token != login_token:
            return self.reponse_json_error("Error", "对不起，已在另一台设备登录")
        access_token = ""
        shop_member_integral = 0
        act_dict["task_currency_type"] = json.loads(act_dict["task_currency_type"]) if act_dict["task_currency_type"] else {"key": 2}
        if int(act_dict["task_currency_type"]["key"]) == 4:
            app_info = AppInfoModel(context=self).get_entity("app_id=%s", params=app_id)
            if app_info:
                access_token = app_info.access_token
            invoke_result_data = self.get_crm_point_available(user_info.user_nick, access_token)
            if invoke_result_data.success == False:
                return self.reponse_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
            shop_member_integral = invoke_result_data.data
            if shop_member_integral < int(exchange_info.need_value):
                return self.reponse_json_error("Error", "对不起，店铺会员积分不足")
        else:
            if user_info.surplus_integral < exchange_info.need_value:
                return self.reponse_json_error("Error", "对不起，积分不足")

        now_datetime = self.get_now_datetime()
        update_result = exchange_info_model.update_table("draw_num=draw_num+1", "id=%s", params=[exchange_info.id])
        if update_result:
            if int(act_dict["task_currency_type"]["key"]) == 4:
                result = self.check_is_member(access_token)
                if not result:
                    return self.reponse_json_error("No_Member", "不是会员，不能领取")
                invoke_result_data = self.change_crm_point(open_id, 1, 1, int(exchange_info.need_value), access_token, exchange_info.id, f"兑换{exchange_info.goods_name}", True)
                if invoke_result_data.success == False:
                    raise Exception("操作会员积分异常")
            try:
                db_transaction.begin_transaction()
                #创建道具记录
                prop_log = PropLog()
                prop_log.app_id = app_id
                prop_log.act_id = act_id
                prop_log.open_id = open_id
                prop_log.user_nick = user_info.user_nick
                prop_log.change_type = 2
                prop_log.operate_type = 0
                prop_log.prop_type = exchange_info.goods_type
                prop_log.operate_value = 1
                prop_log.history_value = history_value
                prop_log.title = f"兑换得到{exchange_info.goods_name}"
                prop_log.create_date_int = SevenHelper.get_now_day_int()
                prop_log.create_date = now_datetime
                prop_log_model.add_entity(prop_log)
                #创建积分记录
                lottery_value_log = LotteryValueLog()
                lottery_value_log.app_id = app_id
                lottery_value_log.act_id = act_id
                lottery_value_log.open_id = open_id
                lottery_value_log.user_nick = user_info.user_nick
                lottery_value_log.log_title = f"兑换{exchange_info.goods_name}"
                lottery_value_log.log_desc = f"兑换ID:{exchange_info.id}"
                lottery_value_log.log_info = {"record_id": invoke_result_data.data["record_id"]} if int(act_dict["task_currency_type"]["key"]) == 4 else {}
                lottery_value_log.currency_type = 4 if int(act_dict["task_currency_type"]["key"]) == 4 else 2
                lottery_value_log.source_type = 5
                lottery_value_log.change_type = 501
                lottery_value_log.operate_type = 1
                lottery_value_log.current_value = -exchange_info.need_value
                lottery_value_log.history_value = shop_member_integral if int(act_dict["task_currency_type"]["key"]) == 4 else user_info.surplus_integral
                lottery_value_log.create_date = self.get_now_datetime()
                lottery_value_log_model.add_entity(lottery_value_log)

                update_user_detail = ""
                if exchange_info.goods_type == 2:
                    update_user_detail = "perspective_card_count=perspective_card_count+1"
                elif exchange_info.goods_type == 3:
                    update_user_detail = "tips_card_count=tips_card_count+1"
                else:
                    update_user_detail = "redraw_card_count=redraw_card_count+1"
                if int(act_dict["task_currency_type"]["key"]) != 4:
                    user_info_model.update_table("surplus_integral=surplus_integral-%s,modify_date=%s", f"id={user_info.id} and surplus_integral={user_info.surplus_integral}", params=[exchange_info.need_value, now_datetime])
                user_detail_model.update_table(update_user_detail, "act_id=%s and open_id=%s", params=[act_id, open_id])
                db_transaction.commit_transaction()
            except Exception as ex:
                db_transaction.rollback_transaction()
                exchange_info_model.update_table("draw_num=draw_num-1", "id=%s", params=[exchange_info.id])
                self.logging_link_info("ExchangeHandler:" + str(ex))
        else:
            return self.reponse_json_error("Error", "当前人数过多,请稍后再试")

        return self.reponse_json_success()