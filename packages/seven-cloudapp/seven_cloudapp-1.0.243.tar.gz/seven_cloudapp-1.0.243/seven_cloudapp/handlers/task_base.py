# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-05-19 11:33:16
@LastEditTime: 2022-03-02 15:51:14
@LastEditors: HuangJianYi
:description: 用户处理
"""
from seven_cloudapp.handlers.top_base import *
from seven_cloudapp.models.seven_model import *
from seven_cloudapp.models.behavior_model import *
from seven_cloudapp.models.db_models.user.user_info_model import *
from seven_cloudapp.models.db_models.act.act_info_model import *
from seven_cloudapp.models.db_models.task.task_info_model import *
from seven_cloudapp.models.db_models.task.task_count_model import *
from seven_cloudapp.models.db_models.lottery.lottery_value_log_model import *
from seven_cloudapp.models.db_models.user.user_blacklist_model import *


class TaskBaseHandler(TopBaseHandler):
    """
    :description: 任务基础类
    """
    def check_common(self, act_dict, user_info, task_info, act_id, open_id, login_token, check_task=True):
        """
        :description: 做任务前的资格校验
        :param act_dict:活动信息
        :param user_info:用户信息
        :param task_info:任务信息
        :param act_id:活动ID
        :param open_id:open_id
        :param login_token:访问令牌
        :param check_task:任务校验
        :return:
        :last_editors: HuangJianYi
        """
        invoke_result = {}
        invoke_result['code'] = "0"
        invoke_result['message'] = "成功"
        task_type = "0"
        if check_task:
            if act_dict.__contains__("is_task"):
                if act_dict["is_task"] == 0:
                    invoke_result['code'] = "CloseTask"
                    invoke_result['message'] = "对不起，任务不存在"
                    return invoke_result
            if not task_info:
                invoke_result['code'] = "NoTask"
                invoke_result['message'] = "对不起，任务不存在"
                return invoke_result
            if task_info.is_release == 0:
                invoke_result['code'] = "NoRelease"
                invoke_result['message'] = "对不起,未配置任务"
                return invoke_result
            task_type = str(task_info.task_type)

        #请求太频繁限制
        if self.check_post(f"Task_Post_{str(act_id)}_{str(task_type)}_{str(open_id)}") == False:
            invoke_result['code'] = "HintMessage"
            invoke_result['message'] = "对不起，请稍后再试"
            return invoke_result

        if not act_dict:
            invoke_result['code'] = "NoAct"
            invoke_result['message'] = "对不起，活动不存在"
            return invoke_result

        now_date = self.get_now_datetime()
        if act_dict['start_date'] != "":
            if TimeHelper.format_time_to_datetime(now_date) < act_dict['start_date']:
                invoke_result['code'] = "NoAct"
                invoke_result['message'] = "活动将在" + str(act_dict['start_date']) + "开启"
                return invoke_result
        if act_dict['end_date'] != "":
            if TimeHelper.format_time_to_datetime(now_date) > act_dict['end_date']:
                invoke_result['code'] = "NoAct"
                invoke_result['message'] = "活动已结束"
                return invoke_result
        if not user_info:
            invoke_result['code'] = "NoUser"
            invoke_result['message'] = "对不起，用户不存在"
            return invoke_result
        if user_info.user_nick == "":
            invoke_result['code'] = "NoUserNick"
            invoke_result['message'] = "对不起，请先授权"
            return invoke_result
        if user_info.user_state == 1:
            invoke_result['code'] = "UserState"
            invoke_result['message'] = "对不起，你是黑名单用户,无法操作"
            return invoke_result
        if login_token != "":
            if user_info.login_token != login_token:
                invoke_result['code'] = "ErrorToken"
                invoke_result['message'] = "对不起，已在另一台设备登录,无法操作"
                return invoke_result

        return invoke_result

    def check_black(self, user_info, act_dict, all_goods_order_list):
        """
        :description: 判断是否满足拉黑条件
        :param user_info:用户信息
        :param act_dict:活动信息
        :param all_goods_order_list:下单商品相关订单列表
        :return:
        :last_editors: HuangJianYi
        """
        user_info_model = UserInfoModel(context=self)
        result = False
        if user_info.user_state == 0 and act_dict['is_black'] == 1 and act_dict['refund_count'] > 0:
            #退款的订单  子订单存在退款 记录一次
            refund_order_data = [i for i in all_goods_order_list if i["refund_status"] not in self.refund_status()]
            #如果不是黑用户 并且存在退款时间 代表黑用户解禁
            if user_info.relieve_date != '1900-01-01 00:00:00':
                refund_order_data = [i for i in refund_order_data if TimeHelper.format_time_to_datetime(i['pay_time']) > TimeHelper.format_time_to_datetime(user_info.relieve_date)]
            #超过变成黑用户
            if len(refund_order_data) >= act_dict['refund_count']:
                result = True
                user_info_model.update_table("user_state=1", "id=%s", user_info.id)
                user_blacklist_model = UserBlacklistModel(context=self)
                user_blacklist = user_blacklist_model.get_entity("act_id=%s and open_id=%s", params=[user_info.act_id, user_info.open_id])
                if user_blacklist:
                    user_blacklist.black_type = 1
                    user_blacklist.reason = ""
                    user_blacklist.audit_status = 0
                    user_blacklist.audit_remark = ""
                    user_blacklist.refund_count += len(refund_order_data)
                    all_refund_order_data = self.json_loads(user_blacklist.refund_order_data)
                    if len(refund_order_data) > 0:
                        for item in refund_order_data:
                            all_refund_order_data.append(item)
                    user_blacklist.refund_order_data = self.json_dumps(all_refund_order_data)
                    user_blacklist_model.update_entity(user_blacklist)
                else:
                    user_blacklist = UserBlacklist()
                    user_blacklist.app_id = user_info.app_id
                    user_blacklist.act_id = user_info.act_id
                    user_blacklist.open_id = user_info.open_id
                    user_blacklist.user_nick = user_info.user_nick
                    user_blacklist.black_type = 1
                    user_blacklist.reason = ""
                    user_blacklist.audit_status = 0
                    user_blacklist.audit_remark = ""
                    user_blacklist.refund_count = len(refund_order_data)
                    user_blacklist.refund_order_data = self.json_dumps(refund_order_data)
                    user_blacklist.create_date = self.get_now_datetime()
                    user_blacklist_model.add_entity(user_blacklist)
        return result

    def send_lottery_value(self, log_title, user_info, update_sql, send_num, act_dict, source_type, change_type, currency_type, log_info="", log_desc="", main_pay_order_no=""):
        """
        :description: 任务完成发送奖励
        :param log_title:标题
        :param user_info:用户信息
        :param update_sql:用户更新语句
        :param send_num:奖励数量
        :param act_dict:活动信息
        :param source_type:来源类型：1-购买2-任务3-手动配置4抽奖
        :param change_type:变动类型
        :param currency_type:货币类型（0无1次数2积分3价格档位4会员积分）
        :param log_desc:备注
        :param log_info:日志
        :return:
        :last_editors: HuangJianYi
        """
        lottery_value_log = LotteryValueLog()
        lottery_value_log.app_id = user_info.app_id
        lottery_value_log.act_id = user_info.act_id
        lottery_value_log.open_id = user_info.open_id
        lottery_value_log.user_nick = user_info.user_nick
        lottery_value_log.log_title = log_title
        lottery_value_log.log_desc = log_desc
        lottery_value_log.log_info = log_info if log_info != "" else {}
        lottery_value_log.currency_type = currency_type
        lottery_value_log.source_type = source_type  #任务
        lottery_value_log.change_type = change_type
        lottery_value_log.operate_type = 0
        lottery_value_log.current_value = send_num
        if currency_type == 4:
            lottery_value_log.history_value = 0
        else:
            lottery_value_log.history_value = (user_info.lottery_value if currency_type == 1 else user_info.surplus_integral) - send_num
        lottery_value_log.create_date = self.get_now_datetime()
        lottery_value_log.main_pay_order_no = main_pay_order_no

        db_transaction = DbTransaction(db_config_dict=config.get_value("db_cloudapp"))
        lottery_value_log_model = LotteryValueLogModel(db_transaction=db_transaction, context=self)
        user_info_model = UserInfoModel(db_transaction=db_transaction, context=self)
        result = False

        try:
            db_transaction.begin_transaction()
            lottery_value_log_model.add_entity(lottery_value_log)
            if update_sql != "":
                user_info_model.update_table(update_sql, "id=%s", params=user_info.id)
            db_transaction.commit_transaction()
            result = True
        except Exception as ex:
            self.logging_link_error(traceback.format_exc())
            db_transaction.rollback_transaction()

        if result:
            behavior_model = BehaviorModel(context=self)
            behavior_model.report_behavior_log(user_info.app_id, user_info.act_id, user_info.open_id, "", 'JoinUserCount', 1, act_dict['act_type'])
            behavior_model.report_behavior_log(user_info.app_id, user_info.act_id, user_info.open_id, "", 'TotalRewardCount', send_num, act_dict['act_type'])
            behavior_model.report_behavior_log(user_info.app_id, user_info.act_id, user_info.open_id, "", 'AddJoinUserCount', 1, act_dict['act_type'])

        return result

    def get_task_currency_type(self, task_currency_type, task_type):
        """
        :description: 获取任务货币类型
        :param task_currency_type:任务货币类型配置  key:1次数2积分3抽奖码4会员积分100其他（混合搭配）
        :param task_type:任务类型（整形）
        :return 任务货币类型
        :last_editors: HuangJingCan
        """
        currency_type = 2
        if task_currency_type == "":
            return currency_type
        task_currency_type_dict = self.json_loads(task_currency_type)
        if not task_currency_type_dict:
            return currency_type
        if int(task_currency_type_dict["key"]) != 100:
            currency_type = int(task_currency_type_dict["key"])
            return currency_type
        value_dict = task_currency_type_dict["value"]
        if not value_dict:
            return currency_type
        if str(task_type) in value_dict.keys():
            currency_type = value_dict[str(task_type)]
        return currency_type