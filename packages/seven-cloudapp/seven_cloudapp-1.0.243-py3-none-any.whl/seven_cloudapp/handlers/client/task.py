# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-05-19 11:33:16
@LastEditTime: 2022-03-04 10:27:45
@LastEditors: HuangJianYi
:description: 任务处理
"""
from seven_cloudapp.handlers.task_base import *

from seven_cloudapp.models.seven_model import *
from seven_cloudapp.models.behavior_model import *
from seven_cloudapp.models.db_models.coin.coin_order_model import *
from seven_cloudapp.models.db_models.pay.pay_order_model import *
from seven_cloudapp.models.db_models.user.user_info_model import *
from seven_cloudapp.models.db_models.act.act_info_model import *
from seven_cloudapp.models.db_models.task.task_info_model import *
from seven_cloudapp.models.db_models.task.task_count_model import *
from seven_cloudapp.models.db_models.lottery.lottery_value_log_model import *
from seven_cloudapp.models.db_models.invite.invite_log_model import *
from seven_cloudapp.models.db_models.collect.collect_log_model import *
from seven_cloudapp.models.db_models.browse.browse_log_model import *
from seven_cloudapp.models.db_models.prize.prize_roster_model import *


class TaskListHandler(TaskBaseHandler):
    """
    :description: 任务列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 任务列表
        :param act_id:活动id
        :param task_types:任务类型字符串,分隔
        :return: 
        :last_editors: HuangJianYi
        """
        open_id = self.get_taobao_param().open_id
        app_id = self.get_taobao_param().source_app_id
        act_id = int(self.get_param("act_id", 0))
        task_types = self.get_param("task_types")

        task_info_model = TaskInfoModel(context=self)
        task_count_model = TaskCountModel(context=self)
        act_info_model = ActInfoModel(context=self)
        user_info_model = UserInfoModel(context=self)
        invite_log_model = InviteLogModel(context=self)
        act_prize_model = ActPrizeModel(context=self)
        prize_roster_model = PrizeRosterModel(context=self)

        task_list = []
        act_dict = act_info_model.get_dict("id=%s and is_release=1", params=act_id)
        user_info = user_info_model.get_entity("act_id=%s and open_id=%s", params=[act_id, open_id])
        if not act_dict:
            return self.reponse_json_error("NoAct", "对不起，活动不存在")
        if not user_info:
            return self.reponse_json_error("NoUser", "对不起，用户不存在")
        task_info_list = task_info_model.get_list("act_id=%s and is_release=1", order_by="sort_index desc", params=[act_id])
        if len(task_info_list) <= 0:
            return self.reponse_json_success(task_list)
        now_day = SevenHelper.get_now_day_int()
        app_info = AppInfoModel(context=self).get_entity("app_id=%s", params=app_id)
        if not app_info:
            return self.reponse_json_error("NoApp", "对不起，App不存在")

        for task_info in task_info_list:
            if task_types:
                if "," + str(task_info.task_type) + "," not in "," + task_types + ",":
                    continue
            task_config = self.json_loads(task_info.task_config)
            reward_value = int(task_config["reward_value"]) if task_config.__contains__("reward_value") else 0
            last_content = self.get_currency_type_name(self.get_task_currency_type(act_dict['task_currency_type'], task_info.task_type))
            if task_info.task_type == 1:  #新人有礼
                is_get = 0
                task_count = task_count_model.get_entity("act_id=%s and open_id=%s and task_type=%s", params=[act_id, open_id, task_info.task_type])
                if task_count:
                    is_get = 1
                result = {}
                result["title"] = "新人有礼"
                result["status"] = is_get
                result["content"] = f"赠送+{reward_value}{last_content}"
                result["reward"] = reward_value
                result["type"] = "free"
                task_list.append(result)
            elif task_info.task_type == 2:  #每日签到
                is_sign = 0
                task_count = task_count_model.get_entity("act_id=%s and open_id=%s and task_type=%s", params=[act_id, open_id, task_info.task_type])
                if task_count and task_count.last_day == now_day:
                    is_sign = 1
                result = {}
                result["title"] = "每日签到"
                result["status"] = is_sign
                result["content"] = f"赠送+{reward_value}{last_content}"
                result["reward"] = reward_value
                result["type"] = "sign"
                result["text"] = ["签到", "已签到"]
                task_list.append(result)
            elif task_info.task_type == 3:  #邀请
                user_limit = int(task_config["user_limit"]) if task_config.__contains__("user_limit") else 0
                today_invite = invite_log_model.get_dict_list("act_id=%s and open_id=%s and create_day=%s", params=[act_id, open_id, now_day])
                result = {}
                result["title"] = "成功邀请1名新用户"
                result["status"] = 1 if len(today_invite) >= user_limit else 0
                result["user_limit"] = user_limit
                result["invite_user_list"] = today_invite
                result["completed_quantity"] = len(today_invite)
                result["content"] = f"赠送+{reward_value}{last_content}"
                result["reward"] = reward_value
                result["type"] = "invite"
                result["text"] = ["去邀请", "已完成"]
                task_list.append(result)
            elif task_info.task_type == 4:  #关注店铺
                result = {}
                result["title"] = "关注店铺"
                result["status"] = user_info.is_favor
                result["content"] = f"赠送+{reward_value}{last_content}"
                result["store_name"] = app_info.store_name
                result["reward"] = reward_value
                result["type"] = "favor"
                result["text"] = ["去关注", "已关注"]
                task_list.append(result)
            elif task_info.task_type == 5:  #加入会员
                finish_status = 0  #2入会已领取0未入会1入会未领取
                join_member_url = ""
                if user_info.is_member != 1:
                    access_token = ""
                    if app_info:
                        access_token = app_info.access_token
                    is_member = self.check_is_member(access_token)
                    if is_member == True:
                        finish_status = 1
                    else:
                        finish_status = 0
                        join_member_url = self.get_join_member_url(access_token)
                else:
                    finish_status = 2
                result = {}
                result["title"] = "加入会员"
                result["join_member_url"] = join_member_url
                result["status"] = finish_status
                result["content"] = f"赠送+{reward_value}{last_content}"
                result["reward"] = reward_value
                result["type"] = "member"
                result["text"] = ["立即入会", "立即领取", "已领取"]
                task_list.append(result)
            elif task_info.task_type == 6:  #下单
                result = {}
                effective_date_start = task_config["effective_date_start"] if task_config.__contains__("effective_date_start") else ""
                effective_date_end = task_config["effective_date_end"] if task_config.__contains__("effective_date_end") else ""
                result["date"] = [effective_date_start, effective_date_end]
                result["title"] = "下单任意1个商品" if reward_value > 0 else f"购买单品享多倍{last_content}"
                # result["title"] = "下单任意1个商品"
                result["goods_list"] = task_config["goods_list"] if task_config.__contains__("goods_list") else []
                result["num_limit"] = int(task_config["num_limit"]) if task_config.__contains__("num_limit") else 0
                result["content"] = f"赠送+{reward_value}{last_content}"
                result["reward"] = reward_value
                result["type"] = "buy"
                result["text"] = ["去购买", "已购买"]
                task_list.append(result)
            elif task_info.task_type == 7:  #收藏
                collect_log_model = CollectLogModel(context=self)
                user_goods_list = collect_log_model.get_list("act_id=%s and open_id=%s", params=[act_id, open_id])
                completed_quantity = collect_log_model.get_total("act_id=%s and open_id=%s and create_day=%s", params=[act_id, open_id, now_day])
                result = {}
                result["title"] = "收藏任意1个商品"
                result["goods_list"] = task_config["goods_list"] if task_config.__contains__("goods_list") else []
                result["user_goods_list"] = [str(i.goods_id) for i in user_goods_list] if len(user_goods_list) > 0 else []
                result["num_limit"] = int(task_config["num_limit"]) if task_config.__contains__("num_limit") else 0
                result["completed_quantity"] = completed_quantity
                result["content"] = f"赠送+{reward_value}{last_content}"
                result["reward"] = reward_value
                result["type"] = "collect"
                result["text"] = ["去收藏", "已收藏"]
                task_list.append(result)
            elif task_info.task_type == 8:  #浏览
                browse_log_model = BrowseLogModel(context=self)
                user_goods_list = browse_log_model.get_list("act_id=%s and open_id=%s", params=[act_id, open_id])
                completed_quantity = browse_log_model.get_total("act_id=%s and open_id=%s and create_day=%s", params=[act_id, open_id, now_day])
                result = {}
                result["title"] = "浏览任意1个商品"
                result["goods_list"] = task_config["goods_list"] if len(task_config["goods_list"]) > 0 else []
                result["user_goods_list"] = [str(i.goods_id) for i in user_goods_list] if len(user_goods_list) > 0 else []
                result["num_limit"] = int(task_config["num_limit"]) if task_config.__contains__("num_limit") else 0
                result["completed_quantity"] = completed_quantity
                result["content"] = f"赠送+{reward_value}{last_content}"
                result["reward"] = reward_value
                result["type"] = "browse"
                result["text"] = ["去浏览", "已浏览"]
                task_list.append(result)
            elif task_info.task_type == 9:  #加入群聊
                finish_status = 0  #2入群已领取0未入群1入群未领取
                task_count = task_count_model.get_entity("act_id=%s and open_id=%s and task_type=%s", params=[act_id, open_id, task_info.task_type])
                if task_count:
                    finish_status = 2
                else:
                    access_token = ""
                    if app_info:
                        access_token = app_info.access_token
                    is_join_group = self.check_join_group(access_token)
                    if is_join_group == True:
                        finish_status = 1
                    else:
                        finish_status = 0

                chatting_group_url = ""
                if task_config.__contains__("join_type") and task_config["join_type"] == 1:
                    chatting_group_url = task_config["join_url"] if task_config.__contains__("join_url") else ""
                else:
                    chatting_group_url = "https://market.m.taobao.com/app/tb-chatting/join-group-landing/index/index.html?groupId=" + str(task_config["chatting_list"][0]["chatting_id"]) if task_config["chatting_list"][0] else ""

                result = {}
                result["title"] = "入群"
                result["status"] = finish_status
                result["chatting_group_url"] = chatting_group_url
                result["content"] = f"赠送+{reward_value}{last_content}"
                result["reward"] = reward_value
                result["type"] = "join_chatting"
                result["text"] = ["立即加群", "立即领取", "已领取"]
                task_list.append(result)
            elif task_info.task_type == 12:  #每周签到
                signin = self.json_loads(user_info.signin) if user_info.signin else {"signin_date": "1900-01-01 00:00:00", "signin_value": 0}
                is_sign = 0
                task_count = task_count_model.get_entity("act_id=%s and open_id=%s and task_type=%s", params=[act_id, open_id, task_info.task_type])
                if task_count and task_count.last_day == now_day:
                    is_sign = 1
                reward_value = int(task_config[str(signin["signin_value"])]) if task_config.__contains__(str(signin["signin_value"])) else 0
                result = {}
                result["title"] = "每周签到"
                result["status"] = is_sign
                result["content"] = f"赠送+{reward_value}{last_content}"
                result["reward"] = reward_value
                result["type"] = "weekly_sign"
                result["count"] = signin["signin_value"] if TimeHelper.is_this_week(signin["signin_date"]) else 0
                result["text"] = ["签到", "已签到"]
                result["task_config"] = task_config
                task_list.append(result)
            elif task_info.task_type == 13:  #下单任意消费
                result = {}
                effective_date_start = task_config["effective_date_start"] if task_config["effective_date_start"] else ""
                effective_date_end = task_config["effective_date_end"] if task_config["effective_date_end"] else ""
                reward_value = reward_value if int(reward_value) != 0 else 1
                result["title"] = f"店内任意消费送{last_content}"
                result["date"] = [effective_date_start, effective_date_end]
                result["content"] = f"在店内消费成功后，积分奖励为实付1元={reward_value}{last_content}，取整数金额奖励{last_content}"
                result["reward"] = reward_value
                result["type"] = "arbitrarily_consumption"
                result["text"] = ["立即下单"]
                task_list.append(result)
            elif task_info.task_type == 14:  #累计消费
                result = {}
                effective_date_start = task_config["effective_date_start"] if task_config["effective_date_start"] else ""
                effective_date_end = task_config["effective_date_end"] if task_config["effective_date_end"] else ""
                reward_list = task_config["reward_list"] if task_config["reward_list"] else []
                count = 0
                for i in range(len(reward_list)):
                    if float(user_info.store_pay_price) >= float(reward_list[i]["money"]):
                        count += 1
                result["title"] = f"累计消费送{last_content}"
                result["date"] = [effective_date_start, effective_date_end]
                result["content"] = ["累计", r"满{}元"]
                result["unit"] = r"+{}" + last_content
                result["reward_list"] = reward_list
                result["type"] = "totle_consumption"
                result["count"] = count
                task_list.append(result)
            elif task_info.task_type == 15:  #单笔订单消费
                result = {}
                effective_date_start = task_config["effective_date_start"] if task_config["effective_date_start"] else ""
                effective_date_end = task_config["effective_date_end"] if task_config["effective_date_end"] else ""
                reward_list = task_config["reward_list"] if task_config["reward_list"] else []
                result["title"] = f"单笔消费送{last_content}"
                result["date"] = [effective_date_start, effective_date_end]
                result["content"] = r"单笔订单消费满{}元"
                result["reward_list"] = reward_list
                result["unit"] = r"+{}" + f"{last_content}奖励"
                result["type"] = "one_consumption"
                result["text"] = ["立即下单"]
                task_list.append(result)
            elif task_info.task_type == 16:  #店长好礼
                act_prize_list = act_prize_model.get_dict_list("act_id=%s and is_release=1 and ascription_type=1", "", "sort_index desc", "", "id,prize_name,surplus,lottery_sum", [act_id])
                if act_prize_list:
                    lottery_sum = int(user_info.lottery_sum) if user_info.lottery_sum else 0
                    for act_prize in act_prize_list:
                        prize_roster_have = prize_roster_model.get_total("open_id=%s and act_id=%s and prize_id=%s", params=[open_id, act_id, act_prize['id']])
                        if prize_roster_have > 0:
                            act_prize["code"] = 2
                            act_prize["text"] = "已领取"
                        elif act_prize["surplus"] <= 0:
                            act_prize["code"] = 3
                            act_prize["text"] = "已领完"
                        elif act_prize["lottery_sum"] > lottery_sum:
                            act_prize["code"] = 1
                            act_prize["text"] = f"还差{act_prize['lottery_sum']-lottery_sum}次可领取"
                        elif act_prize["lottery_sum"] <= lottery_sum:
                            act_prize["code"] = 0
                            act_prize["text"] = "立即领取"
                        result = {}
                        result["title"] = f"店长好礼"
                        result["content"] = r"领取条件：累计参与{}次转盘抽奖"
                        result["act_prize_list"] = act_prize_list
                        result["unit"] = "剩余{}件"
                        result["type"] = "shopowner_gift"
                        result["lottery_sum"] = lottery_sum
                        task_list.append(result)
            elif task_info.task_type == 17:  #抽奖送积分
                result = {}
                result["title"] = f"抽盒获得"
                result["content"] = f"每消耗一次抽盒次数+{reward_value}{last_content}"
                result["text"] = ["去抽盒"]
                result["type"] = "lottery_points"
                task_list.append(result)

        self.reponse_json_success(task_list)


class NewCourtesyHandler(TaskBaseHandler):
    """
    :description: 新人有礼任务
    """
    @filter_check_params("act_id,login_token")
    def get_async(self):
        """
        :description: 新人有礼任务
        :param act_id:活动id
        :param login_token:用户访问令牌
        :return: 
        :last_editors: HuangJianYi
        """
        open_id = self.get_taobao_param().open_id
        app_id = self.get_taobao_param().source_app_id
        login_token = self.get_param("login_token")
        act_id = int(self.get_param("act_id", 0))

        task_info_model = TaskInfoModel(context=self)
        task_count_model = TaskCountModel(context=self)
        act_info_model = ActInfoModel(context=self)
        user_info_model = UserInfoModel(context=self)
        task_type = 1  #任务类型

        act_dict = act_info_model.get_dict("id=%s and is_release=1", params=act_id)
        user_info = user_info_model.get_entity("act_id=%s and open_id=%s", params=[act_id, open_id])
        task_info = task_info_model.get_entity("act_id=%s and task_type=%s", params=[act_id, task_type])
        invoke_result = self.check_common(act_dict, user_info, task_info, act_id, open_id, login_token)
        if invoke_result["code"] != "0":
            return self.reponse_json_error(invoke_result["code"], invoke_result["message"])
        if user_info.is_new == 0:
            return self.reponse_json_error("Error", "对不起，新用户才能领取")
        now_day = SevenHelper.get_now_day_int()

        task_count = task_count_model.get_entity("act_id=%s and open_id=%s and task_type=%s", params=[act_id, open_id, task_type])
        if task_count:
            return self.reponse_json_error("Error", "对不起，已经领取过")
        task_count = TaskCount()
        task_count.app_id = app_id
        task_count.act_id = act_id
        task_count.open_id = open_id
        task_count.task_type = task_type
        task_count.count_value = 1
        task_count.last_day = now_day
        task_count.last_date = self.get_now_datetime()
        if task_count.id > 0:
            task_count_model.update_entity(task_count)
        else:
            task_count_model.add_entity(task_count)

        send_num = 0
        task_config = self.json_loads(task_info.task_config)
        if task_config:
            send_num = int(task_config["reward_value"]) if task_config.__contains__("reward_value") else 0
        if send_num > 0:
            currency_type = self.get_task_currency_type(act_dict['task_currency_type'], task_type)
            last_content = self.get_currency_type_name(currency_type)
            log_title = f"新人有礼+{send_num}{last_content}"
            if currency_type == 1:
                user_info.lottery_value = user_info.lottery_value + send_num
                update_sql = f"lottery_value=lottery_value+{send_num}"
                send_result = self.send_lottery_value(log_title, user_info, update_sql, send_num, act_dict, 2, 201, currency_type)
            elif currency_type == 2:
                user_info.surplus_integral = user_info.surplus_integral + send_num
                update_sql = f"surplus_integral=surplus_integral+{send_num}"
                send_result = self.send_lottery_value(log_title, user_info, update_sql, send_num, act_dict, 2, 201, currency_type)
            elif currency_type == 4:
                access_token = ""
                app_info = AppInfoModel(context=self).get_entity("app_id=%s", params=app_id)
                if app_info:
                    access_token = app_info.access_token
                result = self.check_is_member(access_token)
                if not result:
                    return self.reponse_json_error("No_Member", "不是会员，不能领取")
                invoke_result_data = self.change_crm_point(open_id, 1, 0, send_num, access_token, task_type, "新人有礼任务", True)
                if invoke_result_data.success == False:
                    return self.reponse_json_error("Error", "无法操作会员积分")
                send_result = self.send_lottery_value(log_title, user_info, "", send_num, act_dict, 2, 201, currency_type)
            if send_result == False:
                return self.reponse_json_error("Error", "对不起，请稍后再试")

            behavior_model = BehaviorModel(context=self)
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'FreeUserCount', 1, act_dict['act_type'])
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'FreeCount', 1, act_dict['act_type'])
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'FreeRewardCount', send_num, act_dict['act_type'])

        return self.reponse_json_success(send_num)


class EverySignHandler(TaskBaseHandler):
    """
    :description: 每日签到任务
    """
    @filter_check_params("act_id,login_token")
    def get_async(self):
        """
        :description: 每日签到任务
        :param act_id:活动id
        :param login_token:用户访问令牌
        :return: 
        :last_editors: HuangJianYi
        """
        open_id = self.get_taobao_param().open_id
        app_id = self.get_taobao_param().source_app_id
        login_token = self.get_param("login_token")
        act_id = int(self.get_param("act_id", 0))

        task_info_model = TaskInfoModel(context=self)
        task_count_model = TaskCountModel(context=self)
        act_info_model = ActInfoModel(context=self)
        user_info_model = UserInfoModel(context=self)
        task_type = 2  #任务类型

        act_dict = act_info_model.get_dict("id=%s and is_release=1", params=act_id)
        user_info = user_info_model.get_entity("act_id=%s and open_id=%s", params=[act_id, open_id])
        task_info = task_info_model.get_entity("act_id=%s and task_type=%s", params=[act_id, task_type])
        invoke_result = self.check_common(act_dict, user_info, task_info, act_id, open_id, login_token)
        if invoke_result["code"] != "0":
            return self.reponse_json_error(invoke_result["code"], invoke_result["message"])
        now_day = SevenHelper.get_now_day_int()

        task_count = task_count_model.get_entity("act_id=%s and open_id=%s and task_type=%s", params=[act_id, open_id, task_type])
        if task_count:
            if task_count.last_day == now_day:
                return self.reponse_json_error("Error", "今日已签到")
            task_count.last_day = now_day
            task_count.last_date = self.get_now_datetime()
        else:
            task_count = TaskCount()
            task_count.app_id = app_id
            task_count.act_id = act_id
            task_count.open_id = open_id
            task_count.task_type = task_type
            task_count.count_value = 1
            task_count.last_day = now_day
            task_count.last_date = self.get_now_datetime()
            if task_count.id > 0:
                task_count_model.update_entity(task_count)
            else:
                task_count_model.add_entity(task_count)

        send_num = 0
        task_config = self.json_loads(task_info.task_config)
        if task_config:
            send_num = int(task_config["reward_value"]) if task_config.__contains__("reward_value") else 0
        if send_num > 0:
            currency_type = self.get_task_currency_type(act_dict['task_currency_type'], task_type)
            last_content = self.get_currency_type_name(currency_type)
            log_title = f"签到+{send_num}{last_content}"
            # user_info.lottery_value = user_info.lottery_value + send_num
            # update_sql = f"lottery_value=lottery_value+{send_num}"
            #判断活动的抽奖货币类型来选择更新字段
            if currency_type == 1:
                user_info.lottery_value = user_info.lottery_value + send_num
                update_sql = f"lottery_value=lottery_value+{send_num}"
                send_result = self.send_lottery_value(log_title, user_info, update_sql, send_num, act_dict, 2, 202, currency_type)
            elif currency_type == 2:
                user_info.surplus_integral = user_info.surplus_integral + send_num
                update_sql = f"surplus_integral=surplus_integral+{send_num}"
                send_result = self.send_lottery_value(log_title, user_info, update_sql, send_num, act_dict, 2, 202, currency_type)
            elif currency_type == 4:
                access_token = ""
                app_info = AppInfoModel(context=self).get_entity("app_id=%s", params=app_id)
                if app_info:
                    access_token = app_info.access_token
                result = self.check_is_member(access_token)
                if not result:
                    return self.reponse_json_error("No_Member", "不是会员，不能领取")
                invoke_result_data = self.change_crm_point(open_id, 1, 0, send_num, access_token, task_type, "每日签到任务", True)
                if invoke_result_data.success == False:
                    return self.reponse_json_error("Error", "无法操作会员积分")
                send_result = self.send_lottery_value(log_title, user_info, "", send_num, act_dict, 2, 202, currency_type)
            if send_result == False:
                return self.reponse_json_error("Error", "对不起，请稍后再试")

            behavior_model = BehaviorModel(context=self)
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'SignUserCount', 1, act_dict['act_type'])
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'SignCount', 1, act_dict['act_type'])
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'SignRewardCount', send_num, act_dict['act_type'])

        return self.reponse_json_success(send_num)


class ShareHandler(TaskBaseHandler):
    """
    :description: 用户分享
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 用户分享
        :param act_id:活动id
        :return 
        :last_editors: HuangJingCan
        """
        open_id = self.get_taobao_param().open_id
        app_id = self.get_taobao_param().source_app_id
        act_id = int(self.get_param("act_id", 0))

        act_dict = ActInfoModel(context=self).get_dict("id=%s and is_release=1", params=act_id)

        if not act_dict:
            return self.reponse_json_error_params()

        behavior_model = BehaviorModel(context=self)
        behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'ShareUserCount', 1)
        behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'ShareCount', 1)

        return self.reponse_json_success()


class ActiveNewUserHandler(TaskBaseHandler):
    """
    :description: 邀请新用户上报（分享链接进入）
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 用户分享
        :param act_id:活动id
        :return 
        :last_editors: HuangJingCan
        """
        open_id = self.get_taobao_param().open_id
        app_id = self.get_taobao_param().source_app_id
        act_id = int(self.get_param("act_id", 0))

        act_dict = ActInfoModel(context=self).get_dict("id=%s and is_release=1", params=act_id)

        if not act_dict:
            return self.reponse_json_error_params()

        behavior_model = BehaviorModel(context=self)
        behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'ActiveNewUserCount', 1)

        return self.reponse_json_success()


class InviteHandler(TaskBaseHandler):
    """
    :description: 邀请任务（被邀请人进入调用）
    """
    @filter_check_params("act_id,invite_open_id")
    def get_async(self):
        """
        :description: 邀请任务（被邀请人进入调用）
        :param act_id:活动id
        :param invite_open_id:邀请人
        :param is_task:是否任务
        :return: 
        :last_editors: HuangJianYi
        """
        open_id = self.get_taobao_param().open_id
        app_id = self.get_taobao_param().source_app_id
        act_id = int(self.get_param("act_id", 0))
        invite_open_id = self.get_param("invite_open_id")
        is_task = int(self.get_param("is_task", 1))
        # self.logging_link_info(str(invite_open_id) + "【InviteHandler】"+str(open_id))

        task_info_model = TaskInfoModel(context=self)
        task_count_model = TaskCountModel(context=self)
        act_info_model = ActInfoModel(context=self)
        user_info_model = UserInfoModel(context=self)
        task_type = 3  #任务类型

        act_dict = act_info_model.get_dict("id=%s and is_release=1", params=act_id)
        user_info = user_info_model.get_entity("act_id=%s and open_id=%s", params=[act_id, open_id])
        task_info = task_info_model.get_entity("act_id=%s and task_type=%s", params=[act_id, task_type])
        invoke_result = self.check_common(act_dict, user_info, task_info, act_id, open_id, "", False)
        if invoke_result["code"] != "0":
            return self.reponse_json_error(invoke_result["code"], invoke_result["message"])
        if open_id == invite_open_id:
            return self.reponse_json_error("Error", "无效邀请")

        now_day = SevenHelper.get_now_day_int()
        invite_log_model = InviteLogModel(context=self)
        behavior_model = BehaviorModel(context=self)
        behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'ActiveUserCount', 1)
        behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'ActiveCount', 1)
        if is_task == 1:
            if user_info.is_new == 0:
                return self.reponse_json_error("Error", "此用户不是新用户")
            invite_count = invite_log_model.get_total("act_id=%s and invite_open_id=%s", params=[act_id, open_id])
            if invite_count > 0:
                return self.reponse_json_error("Error", "此用户已经被邀请过")
            task_config = self.json_loads(task_info.task_config)
            if not task_config:
                return self.reponse_json_error("Error", "未开启邀请任务")
            user_limit = int(task_config["user_limit"]) if task_config.__contains__("user_limit") else 0
            today_invite_count = invite_log_model.get_total("act_id=%s and open_id=%s and create_day=%s", params=[act_id, invite_open_id, now_day])
            if today_invite_count >= user_limit:
                return self.reponse_json_error("Error", "达到每日邀请好友上限")

            invite_log = InviteLog()
            invite_log.app_id = app_id
            invite_log.act_id = act_id
            invite_log.open_id = invite_open_id
            invite_log.invite_user_nick = user_info.user_nick
            invite_log.invite_open_id = open_id
            invite_log.invite_avatar = user_info.avatar
            invite_log.is_handle = 0
            invite_log.create_date = self.get_now_datetime()
            invite_log.create_day = now_day
            result = invite_log_model.add_entity(invite_log)
            if result <= 0:
                return self.reponse_json_error("Error", "邀请失败")

        return self.reponse_json_success()


class InviteRewardHandler(TaskBaseHandler):
    """
    :description: 邀请奖励（邀请人进入调用）
    """
    @filter_check_params("act_id,login_token")
    def get_async(self):
        """
        :description: 邀请奖励（邀请人进入调用）
        :param act_id:活动id
        :param login_token:login_token
        :return: 
        :last_editors: HuangJianYi
        """
        open_id = self.get_taobao_param().open_id
        app_id = self.get_taobao_param().source_app_id
        login_token = self.get_param("login_token")
        act_id = int(self.get_param("act_id", 0))

        task_info_model = TaskInfoModel(context=self)
        act_info_model = ActInfoModel(context=self)
        user_info_model = UserInfoModel(context=self)
        task_type = 3

        act_dict = act_info_model.get_dict("id=%s and is_release=1", params=act_id)
        user_info = user_info_model.get_entity("act_id=%s and open_id=%s", params=[act_id, open_id])
        task_info = task_info_model.get_entity("act_id=%s and task_type=%s", params=[act_id, task_type])
        invoke_result = self.check_common(act_dict, user_info, task_info, act_id, open_id, login_token)
        if invoke_result["code"] != "0":
            return self.reponse_json_error(invoke_result["code"], invoke_result["message"])
        now_day = SevenHelper.get_now_day_int()
        task_config = self.json_loads(task_info.task_config)
        if not task_config:
            return self.reponse_json_error("Error", "未开启邀请任务")
        invite_log_model = InviteLogModel(context=self)
        condition = "act_id=%s and open_id=%s and create_day=%s and is_handle=0"
        prams = [act_id, open_id, now_day]
        today_invite_list = invite_log_model.get_dict_list(condition, params=prams)
        today_invite_count = len(today_invite_list)
        reward_count = int(today_invite_count * int(task_config["reward_value"]))
        if reward_count <= 0:
            return self.reponse_json_error("Error", "未达到邀请奖励条件")
        if reward_count > 0:
            currency_type = self.get_task_currency_type(act_dict['task_currency_type'], task_type)
            user_info.lottery_value = user_info.lottery_value + reward_count
            last_content = self.get_currency_type_name(currency_type)
            log_info = {}
            log_info["title"] = f"邀请{today_invite_count}人"
            log_info["invite_list"] = today_invite_list if today_invite_count > 0 else []
            log_title = f"邀请+{reward_count}{last_content}"
            invite_user_nick_list = [i['invite_user_nick'] for i in today_invite_list]
            log_desc = "被邀请用户：" + ",".join(invite_user_nick_list)
            #判断活动的抽奖货币类型来选择更新字段
            if currency_type == 1:
                user_info.lottery_value = user_info.lottery_value + reward_count
                update_sql = f"lottery_value=lottery_value+{reward_count}"
                send_result = self.send_lottery_value(log_title, user_info, update_sql, reward_count, act_dict, 2, 203, currency_type, log_info, log_desc)
            elif currency_type == 2:
                user_info.surplus_integral = user_info.surplus_integral + reward_count
                update_sql = f"surplus_integral=surplus_integral+{reward_count}"
                send_result = self.send_lottery_value(log_title, user_info, update_sql, reward_count, act_dict, 2, 203, currency_type, log_info, log_desc)
            elif currency_type == 4:
                access_token = ""
                app_info = AppInfoModel(context=self).get_entity("app_id=%s", params=app_id)
                if app_info:
                    access_token = app_info.access_token
                result = self.check_is_member(access_token)
                if not result:
                    return self.reponse_json_error("No_Member", "不是会员，不能领取")
                invoke_result_data = self.change_crm_point(open_id, 1, 0, reward_count, access_token, task_type, "每日签到任务", True)
                if invoke_result_data.success == False:
                    return self.reponse_json_error("Error", "无法操作会员积分")
                send_result = self.send_lottery_value(log_title, user_info, "", reward_count, act_dict, 2, 203, currency_type, log_info, log_desc)
            if send_result == False:
                return self.reponse_json_error("Error", "邀请成功,系统异常未给奖励")
            invite_log_model.update_table("is_handle=1", SevenHelper.get_condition_by_id_list("id", [i['id'] for i in today_invite_list]))

            behavior_model = BehaviorModel(context=self)
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'InviteUserCount', 1, act_dict['act_type'])
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'InviteCount', 1, act_dict['act_type'])
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'InviteRewardCount', reward_count, act_dict['act_type'])

        return self.reponse_json_success(reward_count)


class InitialStateHandler(TaskBaseHandler):
    """
    :description: 记录用户最初状态
    """
    @filter_check_params("act_id,is_favor_before,is_member_before")
    def get_async(self):
        """
        :description: 记录用户最初状态
        :param act_id:活动id
        :return 
        :last_editors: ChenCheng
        """
        open_id = self.get_taobao_param().open_id
        act_id = int(self.get_param("act_id", 0))
        is_favor_before = int(self.get_param("is_favor_before", 0))  #初始关注状态
        is_member_before = int(self.get_param("is_member_before", 0))  #初始会员状态

        user_info_model = UserInfoModel(context=self)

        user_info_model.update_table("is_favor_before=%s,is_member_before=%s", "act_id=%s and open_id=%s", params=[is_favor_before, is_member_before, act_id, open_id])

        return self.reponse_json_success()


class FollowHandler(TaskBaseHandler):
    """
    :description: 关注任务
    """
    @filter_check_params("act_id,login_token")
    def get_async(self):
        """
        :description: 关注任务
        :param act_id:活动id
        :param login_token:用户访问令牌
        :return 
        :last_editors: HuangJianYi
        """
        open_id = self.get_taobao_param().open_id
        app_id = self.get_taobao_param().source_app_id
        login_token = self.get_param("login_token")
        act_id = int(self.get_param("act_id", 0))

        task_info_model = TaskInfoModel(context=self)
        act_info_model = ActInfoModel(context=self)
        user_info_model = UserInfoModel(context=self)
        behavior_model = BehaviorModel(context=self)

        task_type = 4  #任务类型

        act_dict = act_info_model.get_dict("id=%s and is_release=1", params=act_id)
        user_info = user_info_model.get_entity("act_id=%s and open_id=%s", params=[act_id, open_id])
        task_info = task_info_model.get_entity("act_id=%s and task_type=%s", params=[act_id, task_type])
        if user_info.is_favor_before == 0:
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'IncreaseFollowUserCount', 1, act_dict['act_type'])
        invoke_result = self.check_common(act_dict, user_info, task_info, act_id, open_id, login_token, False)
        if invoke_result["code"] != "0":
            return self.reponse_json_error(invoke_result["code"], invoke_result["message"])
        if user_info.is_favor == 1:
            return self.reponse_json_error("Error", "已经关注过店铺了")
        if not task_info or task_info.is_release == 0:
            user_info_model.update_table("is_favor=1", "id=%s", params=user_info.id)
            return self.reponse_json_success()

        task_config = self.json_loads(task_info.task_config)
        send_num = 0
        if not task_config:
            return self.reponse_json_error("Error", "未开启加入店铺任务")
        send_num = int(task_config["reward_value"]) if task_config.__contains__("reward_value") else 0
        if send_num > 0:
            user_info.is_favor = 1
            currency_type = self.get_task_currency_type(act_dict['task_currency_type'], task_type)
            last_content = self.get_currency_type_name(currency_type)
            log_title = f"关注店铺+{send_num}{last_content}"
            #判断活动的抽奖货币类型来选择更新字段
            if currency_type == 1:
                user_info.lottery_value = user_info.lottery_value + send_num
                update_sql = f"lottery_value=lottery_value+{send_num},is_favor=1"
                send_result = self.send_lottery_value(log_title, user_info, update_sql, send_num, act_dict, 2, 204, currency_type)
            elif currency_type == 2:
                user_info.surplus_integral = user_info.surplus_integral + send_num
                update_sql = f"surplus_integral=surplus_integral+{send_num},is_favor=1"
                send_result = self.send_lottery_value(log_title, user_info, update_sql, send_num, act_dict, 2, 204, currency_type)
            elif currency_type == 4:
                access_token = ""
                app_info = AppInfoModel(context=self).get_entity("app_id=%s", params=app_id)
                if app_info:
                    access_token = app_info.access_token
                result = self.check_is_member(access_token)
                if not result:
                    return self.reponse_json_error("No_Member", "不是会员，不能领取")
                invoke_result_data = self.change_crm_point(open_id, 1, 0, send_num, access_token, task_type, "关注任务", True)
                if invoke_result_data.success == False:
                    return self.reponse_json_error("Error", "无法操作会员积分")
                send_result = self.send_lottery_value(log_title, user_info, "is_favor=1", send_num, act_dict, 2, 204, currency_type)
            if send_result == False:
                return self.reponse_json_error("Error", "关注店铺成功,系统异常未给奖励")

            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'FollowUserCount', 1, act_dict['act_type'])
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'FollowCount', 1, act_dict['act_type'])
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'FollowRewardCount', send_num, act_dict['act_type'])

        return self.reponse_json_success(send_num)


class JoinMemberRewardHandler(TaskBaseHandler):
    """
    :description: 加入会员任务
    """
    @filter_check_params("act_id,login_token")
    def get_async(self):
        """
        :description: 加入会员任务
        :param act_id:活动id
        :param login_token:用户访问令牌
        :return 
        :last_editors: HuangJianYi
        """
        open_id = self.get_taobao_param().open_id
        app_id = self.get_taobao_param().source_app_id
        login_token = self.get_param("login_token")
        act_id = int(self.get_param("act_id", 0))

        task_info_model = TaskInfoModel(context=self)
        act_info_model = ActInfoModel(context=self)
        user_info_model = UserInfoModel(context=self)
        behavior_model = BehaviorModel(context=self)

        task_type = 5  #任务类型

        act_dict = act_info_model.get_dict("id=%s and is_release=1", params=act_id)
        user_info = user_info_model.get_entity("act_id=%s and open_id=%s", params=[act_id, open_id])
        task_info = task_info_model.get_entity("act_id=%s and task_type=%s", params=[act_id, task_type])
        if user_info.is_member_before == 0:
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'IncreaseMemberUserCount', 1, act_dict['act_type'])
        invoke_result = self.check_common(act_dict, user_info, task_info, act_id, open_id, login_token, False)
        if invoke_result["code"] != "0":
            return self.reponse_json_error(invoke_result["code"], invoke_result["message"])
        if user_info.is_member == 1:
            return self.reponse_json_error("Error", "已经加入会员了")
        access_token = ""
        app_info = AppInfoModel(context=self).get_entity("app_id=%s", params=app_id)
        if app_info:
            access_token = app_info.access_token
        is_member = self.check_is_member(access_token)
        if is_member == False:
            return self.reponse_json_error("Error", "对不起，您未加入会员")
        if not task_info or task_info.is_release == 0:
            user_info_model.update_table("is_member=1", "id=%s", params=user_info.id)
            return self.reponse_json_success()

        task_config = self.json_loads(task_info.task_config)
        if not task_config:
            return self.reponse_json_error("Error", "未开启加入会员任务")
        send_num = int(task_config["reward_value"]) if task_config.__contains__("reward_value") else 0
        if send_num > 0:
            user_info.is_member = 1
            currency_type = self.get_task_currency_type(act_dict['task_currency_type'], task_type)
            last_content = self.get_currency_type_name(currency_type)
            log_title = f"加入会员+{send_num}{last_content}"
            #判断活动的抽奖货币类型来选择更新字段
            if currency_type == 1:
                user_info.lottery_value = user_info.lottery_value + send_num
                update_sql = f"lottery_value=lottery_value+{send_num},is_member=1"
                send_result = self.send_lottery_value(log_title, user_info, update_sql, send_num, act_dict, 2, 205, currency_type)
            elif currency_type == 2:
                user_info.surplus_integral = user_info.surplus_integral + send_num
                update_sql = f"surplus_integral=surplus_integral+{send_num},is_member=1"
                send_result = self.send_lottery_value(log_title, user_info, update_sql, send_num, act_dict, 2, 205, currency_type)
            elif currency_type == 4:
                result = self.check_is_member(access_token)
                if not result:
                    return self.reponse_json_error("No_Member", "不是会员，不能领取")
                invoke_result_data = self.change_crm_point(open_id, 1, 0, send_num, access_token, task_type, "加入会员任务", True)
                if invoke_result_data.success == False:
                    return self.reponse_json_error("Error", "无法操作会员积分")
                send_result = self.send_lottery_value(log_title, user_info, "is_member=1", send_num, act_dict, 2, 205, currency_type)
            if send_result == False:
                return self.reponse_json_error("Error", "加入会员成功,系统异常未给奖励")

            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'MemberUserCount', 1, act_dict['act_type'])
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'MemberCount', 1, act_dict['act_type'])
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'MemberRewardCount', send_num, act_dict['act_type'])

        return self.reponse_json_success(send_num)


class GetMemberUrlHandler(TaskBaseHandler):
    """
    :description: 获取入会地址
    """
    def get_async(self):
        """
        :description: 获取入会地址
        :return: str
        :last_editors: LaiKaiXiang
        """
        app_id = self.get_taobao_param().source_app_id

        app_info = AppInfoModel(context=self).get_entity("app_id=%s", params=app_id)
        if not app_info:
            return self.reponse_json_error("NoApp", "对不起，App不存在")

        access_token = app_info.access_token
        join_member_url = self.get_join_member_url(access_token)

        return self.reponse_json_success(join_member_url)


class CollectGoodsHandler(TaskBaseHandler):
    """
    :description: 收藏商品任务
    """
    @filter_check_params("act_id,goods_id,login_token")
    def get_async(self):
        """
        :description: 收藏商品任务
        :param act_id:活动id
        :param login_token:用户访问令牌
        :return 
        :last_editors: HuangJianYi
        """
        open_id = self.get_taobao_param().open_id
        app_id = self.get_taobao_param().source_app_id
        login_token = self.get_param("login_token")
        act_id = int(self.get_param("act_id", 0))
        goods_id = int(self.get_param("goods_id"))
        goods_name = self.get_param("goods_name")

        task_info_model = TaskInfoModel(context=self)
        task_count_model = TaskCountModel(context=self)
        act_info_model = ActInfoModel(context=self)
        user_info_model = UserInfoModel(context=self)
        task_type = 7  #任务类型

        act_dict = act_info_model.get_dict("id=%s and is_release=1", params=act_id)
        user_info = user_info_model.get_entity("act_id=%s and open_id=%s", params=[act_id, open_id])
        task_info = task_info_model.get_entity("act_id=%s and task_type=%s", params=[act_id, task_type])
        invoke_result = self.check_common(act_dict, user_info, task_info, act_id, open_id, login_token)
        if invoke_result["code"] != "0":
            return self.reponse_json_error(invoke_result["code"], invoke_result["message"])
        task_config = self.json_loads(task_info.task_config)
        if not task_config:
            return self.reponse_json_error("Error", "未开启收藏商品任务")
        if task_config["goods_ids"] == "":
            return self.reponse_json_error("Error", "没有配置收藏商品")
        task_config["goods_ids"] = "," + task_config["goods_ids"] + ","
        if "," + str(goods_id) + "," not in task_config["goods_ids"]:
            return self.reponse_json_error("Error", "当前商品不在收藏任务里")
        collect_log_model = CollectLogModel(context=self)
        collect_count = collect_log_model.get_total("act_id=%s and open_id=%s and goods_id=%s", params=[act_id, open_id, goods_id])
        if collect_count > 0:
            return self.reponse_json_error("Error", "当前商品已经收藏")
        now_day = SevenHelper.get_now_day_int()

        task_count = task_count_model.get_entity("act_id=%s and open_id=%s and task_type=%s", params=[act_id, open_id, task_type])
        if task_count:
            if task_count.last_day == now_day:
                task_count.count_value += 1
            else:
                task_count.count_value = 1
                task_count.last_day = now_day
                task_count.last_date = self.get_now_datetime()
        else:
            task_count = TaskCount()
            task_count.app_id = app_id
            task_count.act_id = act_id
            task_count.open_id = open_id
            task_count.task_type = task_type
            task_count.count_value = 1
            task_count.last_day = now_day
            task_count.last_date = self.get_now_datetime()

        num_limit = int(task_config["num_limit"]) if task_config.__contains__("num_limit") else 0
        if task_count.count_value > num_limit:
            return self.reponse_json_error("Error", "达到每日奖励上限")

        if task_count.id > 0:
            task_count_model.update_entity(task_count)
        else:
            task_count_model.add_entity(task_count)

        send_num = int(task_config["reward_value"]) if task_config.__contains__("reward_value") else 0
        if send_num > 0:
            currency_type = self.get_task_currency_type(act_dict['task_currency_type'], task_type)
            last_content = self.get_currency_type_name(currency_type)
            log_info = {}
            log_info["title"] = f"商品ID：{str(goods_id)}"
            log_info["goods_id"] = goods_id
            log_info["goods_name"] = goods_name
            log_title = f"收藏商品+{send_num}{last_content}"
            log_desc = log_info["title"]
            #判断活动的抽奖货币类型来选择更新字段
            if currency_type == 1:
                user_info.lottery_value = user_info.lottery_value + send_num
                update_sql = f"lottery_value=lottery_value+{send_num}"
                send_result = self.send_lottery_value(log_title, user_info, update_sql, send_num, act_dict, 2, 207, currency_type, log_info, log_desc)
            elif currency_type == 2:
                user_info.surplus_integral = user_info.surplus_integral + send_num
                update_sql = f"surplus_integral=surplus_integral+{send_num}"
                send_result = self.send_lottery_value(log_title, user_info, update_sql, send_num, act_dict, 2, 207, currency_type, log_info, log_desc)
            elif currency_type == 4:
                access_token = ""
                app_info = AppInfoModel(context=self).get_entity("app_id=%s", params=app_id)
                if app_info:
                    access_token = app_info.access_token
                result = self.check_is_member(access_token)
                if not result:
                    return self.reponse_json_error("No_Member", "不是会员，不能领取")
                invoke_result_data = self.change_crm_point(open_id, 1, 0, send_num, access_token, task_type, "收藏商品任务", True)
                if invoke_result_data.success == False:
                    return self.reponse_json_error("Error", "无法操作会员积分")
                send_result = self.send_lottery_value(log_title, user_info, "", send_num, act_dict, 2, 207, currency_type, log_info, log_desc)
            if send_result == False:
                return self.reponse_json_error("Error", "对不起，请稍后再试")
            behavior_model = BehaviorModel(context=self)
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'CollectUserCount', 1, act_dict['act_type'])
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'CollectCount', 1, act_dict['act_type'])
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'CollectRewardCount', send_num, act_dict['act_type'])

        collect_log = CollectLog()
        collect_log.app_id = app_id
        collect_log.act_id = act_id
        collect_log.open_id = open_id
        collect_log.goods_id = goods_id
        collect_log.is_handle = 1
        collect_log.create_date = self.get_now_datetime()
        collect_log.create_day = now_day
        collect_log_model.add_entity(collect_log)

        return self.reponse_json_success(send_num)


class BrowseGoodsHandler(TaskBaseHandler):
    """
    :description: 浏览商品任务
    """
    @filter_check_params("act_id,goods_id,login_token")
    def get_async(self):
        """
        :description: 浏览商品任务
        :param act_id:活动id
        :param login_token:用户访问令牌
        :return 
        :last_editors: HuangJianYi
        """
        open_id = self.get_taobao_param().open_id
        app_id = self.get_taobao_param().source_app_id
        login_token = self.get_param("login_token")
        act_id = int(self.get_param("act_id", 0))
        goods_id = int(self.get_param("goods_id"))
        goods_name = self.get_param("goods_name")

        task_info_model = TaskInfoModel(context=self)
        task_count_model = TaskCountModel(context=self)
        act_info_model = ActInfoModel(context=self)
        user_info_model = UserInfoModel(context=self)
        task_type = 8  #任务类型

        act_dict = act_info_model.get_dict("id=%s and is_release=1", params=act_id)
        user_info = user_info_model.get_entity("act_id=%s and open_id=%s", params=[act_id, open_id])
        task_info = task_info_model.get_entity("act_id=%s and task_type=%s", params=[act_id, task_type])
        invoke_result = self.check_common(act_dict, user_info, task_info, act_id, open_id, login_token)
        if invoke_result["code"] != "0":
            return self.reponse_json_error(invoke_result["code"], invoke_result["message"])
        task_config = self.json_loads(task_info.task_config)
        if not task_config:
            return self.reponse_json_error("Error", "未开启浏览商品任务")
        if task_config["goods_ids"] == "":
            return self.reponse_json_error("Error", "没有配置浏览商品")
        task_config["goods_ids"] = "," + task_config["goods_ids"] + ","
        if "," + str(goods_id) + "," not in task_config["goods_ids"]:
            return self.reponse_json_error("Error", "当前商品不在浏览任务里")

        browse_log_model = BrowseLogModel(context=self)
        browse_count = browse_log_model.get_total("act_id=%s and open_id=%s and goods_id=%s", params=[act_id, open_id, goods_id])
        if browse_count > 0:
            return self.reponse_json_error("Error", "当前商品已经浏览过")
        now_day = SevenHelper.get_now_day_int()
        task_count = task_count_model.get_entity("act_id=%s and open_id=%s and task_type=%s", params=[act_id, open_id, task_type])
        if task_count:
            if task_count.last_day == now_day:
                task_count.count_value += 1
            else:
                task_count.count_value = 1
                task_count.last_day = now_day
                task_count.last_date = self.get_now_datetime()
        else:
            task_count = TaskCount()
            task_count.app_id = app_id
            task_count.act_id = act_id
            task_count.open_id = open_id
            task_count.task_type = task_type
            task_count.count_value = 1
            task_count.last_day = now_day
            task_count.last_date = self.get_now_datetime()

        num_limit = int(task_config["num_limit"]) if task_config.__contains__("num_limit") else 0
        if task_count.count_value > num_limit:
            return self.reponse_json_error("Error", "达到每日奖励上限")

        if task_count.id > 0:
            task_count_model.update_entity(task_count)
        else:
            task_count_model.add_entity(task_count)

        send_num = int(task_config["reward_value"]) if task_config.__contains__("reward_value") else 0
        if send_num > 0:
            currency_type = self.get_task_currency_type(act_dict['task_currency_type'], task_type)
            last_content = self.get_currency_type_name(currency_type)
            log_info = {}
            log_info["title"] = f"商品ID：{str(goods_id)}"
            log_info["goods_id"] = goods_id
            log_info["goods_name"] = goods_name
            log_title = f"浏览商品+{send_num}{last_content}"
            log_desc = log_info["title"]
            #判断活动的抽奖货币类型来选择更新字段
            if currency_type == 1:
                user_info.lottery_value = user_info.lottery_value + send_num
                update_sql = f"lottery_value=lottery_value+{send_num}"
                send_result = self.send_lottery_value(log_title, user_info, update_sql, send_num, act_dict, 2, 208, currency_type, log_info, log_desc)
            elif currency_type == 2:
                user_info.surplus_integral = user_info.surplus_integral + send_num
                update_sql = f"surplus_integral=surplus_integral+{send_num}"
                send_result = self.send_lottery_value(log_title, user_info, update_sql, send_num, act_dict, 2, 208, currency_type, log_info, log_desc)
            elif currency_type == 4:
                access_token = ""
                app_info = AppInfoModel(context=self).get_entity("app_id=%s", params=app_id)
                if app_info:
                    access_token = app_info.access_token
                result = self.check_is_member(access_token)
                if not result:
                    return self.reponse_json_error("No_Member", "不是会员，不能领取")
                invoke_result_data = self.change_crm_point(open_id, 1, 0, send_num, access_token, task_type, "浏览商品任务", True)
                if invoke_result_data.success == False:
                    return self.reponse_json_error("Error", "无法操作会员积分")
                send_result = self.send_lottery_value(log_title, user_info, "", send_num, act_dict, 2, 208, currency_type, log_info, log_desc)
            if send_result == False:
                return self.reponse_json_error("Error", "对不起，请稍后再试")
            behavior_model = BehaviorModel(context=self)
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'BrowseUserCount', 1, act_dict['act_type'])
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'BrowseCount', 1, act_dict['act_type'])
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'BrowseRewardCount', send_num, act_dict['act_type'])

        browse_log = BrowseLog()
        browse_log.app_id = app_id
        browse_log.act_id = act_id
        browse_log.open_id = open_id
        browse_log.goods_id = goods_id
        browse_log.is_handle = 1
        browse_log.create_date = self.get_now_datetime()
        browse_log.create_day = now_day
        browse_log_model.add_entity(browse_log)

        return self.reponse_json_success(send_num)


class BuyGoodsHandler(TaskBaseHandler):
    """
    :description: 指定商品下单任务
    """
    @filter_check_params("act_id,login_token")
    def get_async(self):
        """
        :description: 指定商品下单任务
        :param act_id:活动id
        :param login_token:用户访问令牌
        :return:
        :last_editors: HuangJianYi
        """
        open_id = self.get_taobao_param().open_id
        app_id = self.get_taobao_param().source_app_id
        login_token = self.get_param("login_token")
        act_id = int(self.get_param("act_id", 0))

        act_info_model = ActInfoModel(context=self)
        task_count_model = TaskCountModel(context=self)
        task_info_model = TaskInfoModel(context=self)
        user_info_model = UserInfoModel(context=self)
        task_type = 6  #任务类型

        act_dict = act_info_model.get_dict("id=%s and is_release=1", params=act_id)
        user_info = user_info_model.get_entity("act_id=%s and open_id=%s", params=[act_id, open_id])
        task_info = task_info_model.get_entity("act_id=%s and task_type=%s", params=[act_id, task_type])
        invoke_result = self.check_common(act_dict, user_info, task_info, act_id, open_id, login_token)
        if invoke_result["code"] != "0":
            return self.reponse_json_error(invoke_result["code"], invoke_result["message"])
        task_config = self.json_loads(task_info.task_config)
        if not task_config:
            return self.reponse_json_error("Error", "未开启下单商品任务")
        if task_config.__contains__("goods_ids") == False or task_config["goods_ids"] == "":
            return self.reponse_json_error("Error", "没有配置下单商品")

        now_day = SevenHelper.get_now_day_int()
        task_count = task_count_model.get_entity("act_id=%s and open_id=%s and task_type=%s", params=[act_id, open_id, task_type])
        # if task_count:
        #     if task_count.last_day == now_day:
        #         task_count.count_value += 1
        #     else:
        #         task_count.count_value = 1
        #         task_count.last_day = now_day
        #         task_count.last_date = self.get_now_datetime()
        # else:
        #     task_count = TaskCount()
        #     task_count.app_id = app_id
        #     task_count.act_id = act_id
        #     task_count.open_id = open_id
        #     task_count.task_type = task_type
        #     task_count.count_value = 1
        #     task_count.last_day = now_day
        #     task_count.last_date = self.get_now_datetime()

        num_limit = int(task_config["num_limit"]) if task_config.__contains__("num_limit") else 0
        # if task_count.count_value > num_limit:
        #     return self.reponse_json_error("Error", "达到每日奖励上限")

        access_token = ""
        app_info = AppInfoModel(context=self).get_entity("app_id=%s", params=self.get_taobao_param().source_app_id)
        if app_info:
            access_token = app_info.access_token
        # 获取订单
        order_data = []
        if task_config.__contains__("effective_date_start") == True and task_config.__contains__("effective_date_end") == True and task_config["effective_date_start"] != "" and task_config["effective_date_end"] != "":
            order_data = self.get_taobao_order(open_id, access_token, task_config.effective_date_start, task_config.effective_date_end)
        if act_dict['start_date'] != "":
            order_data = self.get_taobao_order(open_id, access_token, act_dict['start_date'])
        else:
            order_data = self.get_taobao_order(open_id, access_token)

        # self.logging_link_info(str(order_data) + "【订单列表】")

        pay_order_model = PayOrderModel(context=self)
        pay_order_list = pay_order_model.get_list("app_id=%s and open_id=%s and act_id=%s", params=[app_id, open_id, act_id])

        pay_order_id_list = []
        for item in pay_order_list:
            pay_order_id_list.append(item.order_no)

        buy_goods_id_list = []
        for item in task_config["goods_ids"].split(","):
            buy_goods_id_list.append(item)

        #所有订单(排除交易结束订单)
        all_sub_order_list = []
        #所有相关商品订单
        all_goods_order_list = []

        #过滤掉不奖励的数据和跟活动无关的订单
        if order_data:
            for item in order_data:
                for order in item["orders"]["order"]:
                    if str(order["num_iid"]) in buy_goods_id_list:
                        if order["status"] in self.rewards_status():
                            order["pay_time"] = item["pay_time"]
                            order["tid"] = item["tid"]
                            all_sub_order_list.append(order)
                        if "pay_time" in item:
                            order["tid"] = item["tid"]
                            order["pay_time"] = item["pay_time"]
                            all_goods_order_list.append(order)

        # self.logging_link_info(str(all_goods_order_list) + "【all_goods_order_list】")

        total_pay_num = 0  #总支付笔数
        total_reward_num = 0  #总奖励值
        total_pay_prize = 0  #总支付金额
        total_pay_order_num = 0  #总订单数
        try:
            for order in all_sub_order_list:
                #判断是否已经加过奖励
                if order["oid"] not in pay_order_id_list:

                    if task_count:
                        if task_count.last_day == now_day:
                            task_count.count_value += 1
                        else:
                            task_count.count_value = 1
                            task_count.last_day = now_day
                            task_count.last_date = self.get_now_datetime()
                    else:
                        task_count = TaskCount()
                        task_count.app_id = app_id
                        task_count.act_id = act_id
                        task_count.open_id = open_id
                        task_count.task_type = task_type
                        task_count.count_value = 1
                        task_count.last_day = now_day
                        task_count.last_date = self.get_now_datetime()

                    if task_count.id > 0:
                        task_count_model.update_entity(task_count)
                    else:
                        task_count_model.add_entity(task_count)

                    pay_order = PayOrder()
                    pay_order.app_id = app_id
                    pay_order.act_id = act_id
                    pay_order.open_id = open_id
                    pay_order.owner_open_id = act_dict['owner_open_id']
                    pay_order.user_nick = user_info.user_nick
                    pay_order.main_order_no = order['tid']
                    pay_order.order_no = order['oid']
                    pay_order.goods_code = order['num_iid']
                    pay_order.goods_name = order['title']
                    if "sku_id" in order.keys():
                        pay_order.sku_id = order['sku_id']
                    pay_order.buy_num = order['num']
                    pay_order.pay_price = order['payment']
                    pay_order.order_status = order['status']
                    pay_order.create_date = self.get_now_datetime()
                    pay_order.pay_date = order['pay_time']

                    send_num = int(task_config["reward_value"]) if task_config.__contains__("reward_value") else 0

                    #获得次数
                    prize_count = int(order["num"])
                    pay_price = decimal.Decimal(order["payment"])
                    user_info.lottery_value += send_num
                    user_info.pay_num += prize_count
                    user_info.pay_price = str(decimal.Decimal(user_info.pay_price) + pay_price)
                    currency_type = self.get_task_currency_type(act_dict['task_currency_type'], task_type)
                    last_content = self.get_currency_type_name(act_dict['currency_type'])
                    log_info = {}
                    log_info["title"] = f"商品ID：{str(order['num_iid'])}"
                    log_info["goods_id"] = order['num_iid']
                    log_info["goods_name"] = order['title']
                    log_info["order"] = order

                    if send_num <= 0:
                        if task_config.__contains__("goods_list"):
                            for goods in task_config["goods_list"]:
                                if str(goods["num_iid"]) == str(order['num_iid']):
                                    send_num = int(goods["reward_value"]) if goods.__contains__("reward_value") else 0
                    log_title = f"购买商品+{send_num}{last_content}"
                    update_sql = f"pay_num=pay_num+{prize_count},pay_price=pay_price+{pay_price},lottery_value=lottery_value+{send_num}"
                    if currency_type == 4:
                        update_sql = f"pay_num=pay_num+{prize_count},pay_price=pay_price+{pay_price}"
                    log_desc = f"淘宝订单号：{pay_order.main_order_no}；" + log_info["title"]
                    send_result = False
                    if task_count.count_value > num_limit:
                        send_result = True
                    else:
                        # return self.reponse_json_error("Error", "达到每日奖励上限")
                        if currency_type == 4:
                            result = self.check_is_member(access_token)
                            if not result:
                                return self.reponse_json_error("No_Member", "不是会员，不能领取")
                            invoke_result_data = self.change_crm_point(open_id, 1, 0, send_num, access_token, task_type, "指定商品下单任务", True)
                            if invoke_result_data.success == False:
                                return self.reponse_json_error("Error", "无法操作会员积分")
                            send_result = self.send_lottery_value(log_title, user_info, "", send_num, act_dict, 2, 206, currency_type, log_info, log_desc)
                        else:
                            send_result = self.send_lottery_value(log_title, user_info, update_sql, send_num, act_dict, 2, 206, currency_type, log_info, log_desc)
                    if send_result == False:
                        continue
                    send_num = 0 if task_count.count_value > num_limit else send_num
                    total_reward_num += send_num
                    total_pay_num += 1
                    total_pay_prize = str(decimal.Decimal(total_pay_prize) + decimal.Decimal(order["payment"]))
                    total_pay_order_num += int(order["num"])
                    user_info_dict = user_info.__dict__
                    if "sku_id" in order.keys():
                        pay_order.sku_name = self.get_sku_name(int(order['num_iid']), int(order['sku_id']), access_token)
                    pay_order_id = pay_order_model.add_entity(pay_order)
                    #添加记录
                    coin_order_model = CoinOrderModel(context=self)
                    coin_order = CoinOrder()
                    coin_order.open_id = open_id
                    coin_order.app_id = app_id
                    coin_order.act_id = act_id
                    coin_order.reward_type = 0
                    coin_order.goods_name = pay_order.goods_name
                    coin_order.goods_price = pay_order.pay_price
                    coin_order.sku = pay_order.sku_id
                    coin_order.nick_name = pay_order.user_nick
                    coin_order.main_pay_order_no = pay_order.main_order_no
                    coin_order.pay_order_no = pay_order.order_no
                    coin_order.pay_order_id = pay_order_id
                    coin_order.buy_count = prize_count
                    coin_order.surplus_count = 0 if task_count.count_value > num_limit else prize_count
                    coin_order.pay_date = pay_order.pay_date
                    coin_order.create_date = self.get_now_datetime()
                    coin_order.modify_date = self.get_now_datetime()
                    coin_order_model.add_entity(coin_order)

        except Exception as ex:
            # self.logging_link_info(str(all_sub_order_list) + "【任务订单列表】" + str(ex))
            return self.reponse_json_error('Error', '任务获取订单失败', str(ex))

        is_black = self.check_black(user_info, act_dict, all_goods_order_list)
        if total_reward_num > 0:
            behavior_model = BehaviorModel(context=self)
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'BuyUserCount', 1, act_dict['act_type'])
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'BuyCount', total_pay_num, act_dict['act_type'])
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'BuyRewardCount', total_reward_num, act_dict['act_type'])

            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'PayMoneyCount', decimal.Decimal(total_pay_prize), act_dict['act_type'])

        result = {}
        result["is_black"] = is_black
        result["reward_num"] = total_reward_num

        return self.reponse_json_success(result)


class JoinChattingRewardHandler(TaskBaseHandler):
    """
    :description: 加入群聊奖励接口
    """
    @filter_check_params("act_id,login_token")
    def get_async(self):
        """
        :description: 加入群聊奖励接口
        :param act_id:活动id
        :param login_token:login_token
        :return:
        :last_editors: HuangJianYi
        """
        open_id = self.get_taobao_param().open_id
        app_id = self.get_taobao_param().source_app_id
        login_token = self.get_param("login_token")
        act_id = int(self.get_param("act_id", 0))

        task_info_model = TaskInfoModel(context=self)
        act_info_model = ActInfoModel(context=self)
        user_info_model = UserInfoModel(context=self)
        task_count_model = TaskCountModel(context=self)
        task_type = 9

        app_info = AppInfoModel(context=self).get_entity("app_id=%s", params=app_id)
        if not app_info:
            return self.reponse_json_error("Error", "对不起,应用不存在")
        act_dict = act_info_model.get_dict("id=%s and is_release=1", params=act_id)
        user_info = user_info_model.get_entity("act_id=%s and open_id=%s", params=[act_id, open_id])
        task_info = task_info_model.get_entity("act_id=%s and task_type=%s", params=[act_id, task_type])
        invoke_result = self.check_common(act_dict, user_info, task_info, act_id, open_id, login_token)
        if invoke_result["code"] != "0":
            return self.reponse_json_error(invoke_result["code"], invoke_result["message"])
        now_day = SevenHelper.get_now_day_int()

        task_config = self.json_loads(task_info.task_config)
        send_num = 0
        if not task_config:
            return self.reponse_json_error("Error", "未开启入群任务")
        send_num = int(task_config["reward_value"]) if task_config.__contains__("reward_value") else 0
        reward_task_count = task_count_model.get_entity("act_id=%s and open_id=%s and task_type=%s", params=[act_id, open_id, task_info.task_type])
        if reward_task_count:
            return self.reponse_json_error("Error", "对不起，请勿重复领取")
        is_join_group = self.check_join_group(app_info.access_token)
        if is_join_group == False:
            return self.reponse_json_error("Error", "对不起，您还未加入群聊")
        reward_count = int(task_config["reward_value"])
        if reward_count <= 0:
            return self.reponse_json_error("Error", "未达到入群奖励条件")

        if send_num > 0:
            user_info.surplus_integral = user_info.surplus_integral + send_num
            currency_type = self.get_task_currency_type(act_dict['task_currency_type'], task_type)
            last_content = self.get_currency_type_name(currency_type)
            chatting_id = str(task_config["chatting_list"][0]["chatting_id"]) if task_config["chatting_list"][0] else ""
            chatting_name = str(task_config["chatting_list"][0]["chatting_name"]) if task_config["chatting_list"][0] else ""
            log_info = {}
            log_info["title"] = f"群聊ID：{chatting_id}" if chatting_id else ""
            log_info["chatting_id"] = chatting_id
            log_info["chatting_name"] = chatting_name
            log_title = f"入群+{send_num}{last_content}"
            #判断活动的抽奖货币类型来选择更新字段
            if currency_type == 1:
                user_info.lottery_value = user_info.lottery_value + send_num
                update_sql = f"lottery_value=lottery_value+{send_num}"
            elif currency_type == 2:
                user_info.surplus_integral = user_info.surplus_integral + send_num
                update_sql = f"surplus_integral=surplus_integral+{send_num}"
            log_desc = log_info["title"]
            send_result = self.send_lottery_value(log_title, user_info, update_sql, send_num, act_dict, 2, 209, currency_type, log_info, log_desc)
            if send_result == False:
                return self.reponse_json_error("Error", "入群成功,系统异常未给奖励")

            behavior_model = BehaviorModel(context=self)
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'JoinGroupUserCount', 1, act_dict['act_type'])
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'JoinGroupCount', 1, act_dict['act_type'])
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'JoinGroupRewardCount', send_num, act_dict['act_type'])

            task_count = TaskCount()
            task_count.app_id = app_id
            task_count.act_id = act_id
            task_count.open_id = open_id
            task_count.task_type = task_type
            task_count.task_sub_type = ""
            task_count.count_value = 1
            task_count.last_day = now_day
            task_count.last_date = self.get_now_datetime()
            task_count_model.add_entity(task_count)

        return self.reponse_json_success(send_num)


class WeeklySignHandler(TaskBaseHandler):
    """
    :description: 每周签到任务
    """
    @filter_check_params("act_id,login_token")
    def get_async(self):
        """
        :description: 每周签到任务
        :param act_id:活动id
        :param login_token:用户访问令牌
        :return: 
        :last_editors: ChenCheng
        """
        open_id = self.get_taobao_param().open_id
        app_id = self.get_taobao_param().source_app_id
        login_token = self.get_param("login_token")
        act_id = int(self.get_param("act_id", 0))

        task_info_model = TaskInfoModel(context=self)
        task_count_model = TaskCountModel(context=self)
        act_info_model = ActInfoModel(context=self)
        user_info_model = UserInfoModel(context=self)
        task_type = 12  #任务类型

        act_dict = act_info_model.get_dict("id=%s and is_release=1", params=act_id)
        user_info = user_info_model.get_entity("app_id=%s and act_id=%s and open_id=%s", params=[app_id, act_id, open_id])
        task_info = task_info_model.get_entity("act_id=%s and task_type=%s", params=[act_id, task_type])
        invoke_result = self.check_common(act_dict, user_info, task_info, act_id, open_id, login_token)
        if invoke_result["code"] != "0":
            return self.reponse_json_error(invoke_result["code"], invoke_result["message"])
        now_day = SevenHelper.get_now_day_int()

        task_count = task_count_model.get_entity("act_id=%s and open_id=%s and task_type=%s", params=[act_id, open_id, task_type])
        if task_count:
            if task_count.last_day == now_day:
                return self.reponse_json_error("Error", "今日已签到")
            task_count.count_value += 1
            task_count.last_day = now_day
            task_count.last_date = self.get_now_datetime()
        else:
            task_count = TaskCount()
            task_count.app_id = app_id
            task_count.act_id = act_id
            task_count.open_id = open_id
            task_count.task_type = task_type
            task_count.count_value = 1
            task_count.last_day = now_day
            task_count.last_date = self.get_now_datetime()

        send_num = 0
        task_config = self.json_loads(task_info.task_config)
        signin = self.json_loads(user_info.signin) if user_info.signin else {"signin_date": "1900-01-01 00:00:00", "signin_value": 0}
        # updata_signin = UpdataSignModel(context=self)
        updata_signin = {}
        updata_signin['signin_value'] = signin["signin_value"]
        updata_signin['signin_date'] = TimeHelper.get_now_format_time()
        # updata_signin["signin_date"] = TimeHelper.get_now_format_time()
        if task_config:
            if TimeHelper.is_this_week(signin["signin_date"]):
                updata_signin['signin_value'] = signin["signin_value"] + 1
            else:
                updata_signin['signin_value'] = 1
            send_num = int(task_config[str(updata_signin['signin_value'])]) if task_config.__contains__(str(updata_signin['signin_value'])) else 0
        if send_num > 0:
            user_info.surplus_integral = user_info.surplus_integral + send_num
            currency_type = self.get_task_currency_type(act_dict['task_currency_type'], task_type)
            last_content = self.get_currency_type_name(currency_type)
            log_title = f"周累计签到{updata_signin['signin_value']}天"
            log_desc = log_title
            update_sql = f"surplus_integral=surplus_integral+{send_num},signin='{self.json_dumps(updata_signin)}'"
            # print(update_sql)
            if currency_type == 4:
                access_token = ""
                app_info = AppInfoModel(context=self).get_entity("app_id=%s", params=app_id)
                if app_info:
                    access_token = app_info.access_token
                result = self.check_is_member(access_token)
                if not result:
                    return self.reponse_json_error("No_Member", "不是会员，不能领取")
                invoke_result_data = self.change_crm_point(open_id, 1, 0, send_num, access_token, task_type, "每周签到任务", True)
                if invoke_result_data.success == False:
                    return self.reponse_json_error("Error", "无法操作会员积分")
                update_sql = f"signin='{self.json_dumps(updata_signin)}'"
                send_result = self.send_lottery_value(log_title, user_info, update_sql, send_num, act_dict, 2, 2012, currency_type, log_desc)
            else:
                send_result = self.send_lottery_value(log_title, user_info, update_sql, send_num, act_dict, 2, 2012, currency_type, log_desc)
            if send_result == False:
                return self.reponse_json_error("Error", "对不起，请稍后再试")

            behavior_model = BehaviorModel(context=self)
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'SignUserCount', 1, act_dict['act_type'])
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'SignCount', 1, act_dict['act_type'])
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'SignRewardCount', send_num, act_dict['act_type'])

        if task_count.id > 0:
            task_count_model.update_entity(task_count)
        else:
            task_count_model.add_entity(task_count)

        return self.reponse_json_success(send_num)


class ShopownerGiftHandler(TaskBaseHandler):
    """
    :description: 店长好礼任务（注意：添加或者删除奖品的时候需要新增或者删除orm_key）
    """
    @filter_check_params("act_id,login_token")
    def get_async(self):
        """
        :description: 店长好礼任务（注意：添加或者删除奖品的时候需要新增或者删除orm_key）
        :param act_id:活动id
        :param login_token:用户访问令牌
        :return: 
        :last_editors: ChenCheng 
        """
        open_id = self.get_taobao_param().open_id
        app_id = self.get_taobao_param().source_app_id
        login_token = self.get_param("login_token")
        act_id = int(self.get_param("act_id", 0))
        prize_id = int(self.get_param("prize_id", 0))
        log_info = {}

        db_transaction = DbTransaction(db_config_dict=config.get_value("db_cloudapp"))
        task_info_model = TaskInfoModel(context=self)
        task_count_model = TaskCountModel(db_transaction=db_transaction, context=self)
        act_info_model = ActInfoModel(context=self)
        user_info_model = UserInfoModel(context=self)
        act_prize_model = ActPrizeModel(db_transaction=db_transaction, context=self)
        prize_roster_model = PrizeRosterModel(db_transaction=db_transaction, context=self)
        task_type = 16  #任务类型

        act_dict = act_info_model.get_dict("id=%s and is_release=1", params=act_id)
        user_info = user_info_model.get_entity("app_id=%s and act_id=%s and open_id=%s", params=[app_id, act_id, open_id])
        task_info = task_info_model.get_entity("act_id=%s and task_type=%s", params=[act_id, task_type])
        invoke_result = self.check_common(act_dict, user_info, task_info, act_id, open_id, login_token)
        if invoke_result["code"] != "0":
            return self.reponse_json_error(invoke_result["code"], invoke_result["message"])

        prize_roster_have = prize_roster_model.get_entity("open_id=%s and act_id=%s and prize_id=%s", params=[open_id, act_id, prize_id])
        if prize_roster_have:
            return self.reponse_json_error("Error", "对不起，已经领取过")

        act_prize = act_prize_model.get_entity("act_id=%s and is_release=1 and id=%s", params=[act_id, prize_id])
        if act_prize:
            if act_prize.lottery_sum > user_info.lottery_sum:
                return self.reponse_json_error("Error", "对不起，未达到领取要求")
        else:
            return self.reponse_json_error("Error", "对不起，奖品不存在")

        #添加记录，同步奖品库存
        try:
            #任务完成记录
            now_day = SevenHelper.get_now_day_int()
            task_count = task_count_model.get_entity("act_id=%s and open_id=%s and task_type=%s", params=[act_id, open_id, task_type])
            if task_count:
                task_count.count_value += 1
                task_count.last_day = now_day
                task_count.last_date = self.get_now_datetime()
            else:
                task_count = TaskCount()
                task_count.app_id = app_id
                task_count.act_id = act_id
                task_count.open_id = open_id
                task_count.task_type = task_type
                task_count.count_value = 1
                task_count.last_day = now_day
                task_count.last_date = self.get_now_datetime()

            #录入中奖记录
            prize_roster = PrizeRoster()
            prize_roster.app_id = app_id
            prize_roster.act_id = act_id
            prize_roster.open_id = open_id
            prize_roster.prize_id = act_prize.id
            prize_roster.prize_name = act_prize.prize_name
            prize_roster.prize_price = act_prize.prize_price
            prize_roster.prize_pic = act_prize.prize_pic
            prize_roster.prize_detail = act_prize.prize_detail
            prize_roster.prize_type = act_prize.prize_type
            prize_roster.award_name = act_prize.tag_name if act_prize.tag_name else ""
            prize_roster.user_nick = user_info.user_nick
            prize_roster.goods_id = act_prize.goods_id
            prize_roster.is_sku = act_prize.is_sku
            prize_roster.goods_code = act_prize.goods_code
            prize_roster.goods_code_list = act_prize.goods_code_list
            prize_roster.sku_detail = act_prize.sku_detail
            prize_roster.avatar = user_info.avatar
            prize_roster.create_date = self.get_now_datetime()

            db_transaction.commit_transaction()

            #过滤并发情况，奖品剩余件数已不足
            result = act_prize_model.update_table("surplus=surplus-1,hand_out=hand_out+1", "id=%s and surplus>0", act_prize.id)
            if not result:
                return self.reponse_json_error("Error", "对不起，领取失败，请刷新")

            prize_roster_id = prize_roster_model.add_entity(prize_roster)
            prize_roster.id = prize_roster_id
            if task_count.id > 0:
                task_count_model.update_entity(task_count)
            else:
                task_count_model.add_entity(task_count)

            log_info["code"] = "Success"
            log_info["message"] = prize_roster.__dict__
        except Exception as ex:
            # self.logging_link_error(str(ex) + "【店长好礼任务】")
            db_transaction.rollback_transaction()
            log_info["code"] = "Exception"
            log_info["message"] = ex
            # print(log_info)
            return self.reponse_json_error("Error", "对不起，领取失败", ex)

        if log_info["code"] == "Success":
            behavior_model = BehaviorModel(context=self)
            # 完成次数：保底_累计抽xx次
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_dict['owner_open_id'], 'ShopownerGiftCount_' + str(prize_id), 1, act_dict['act_type'])

        return self.reponse_json_success(prize_roster)