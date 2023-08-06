# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-05-19 11:33:16
@LastEditTime: 2022-02-17 14:14:38
@LastEditors: HuangJianYi
:description: 用户处理
"""
from seven_cloudapp.handlers.seven_base import *

from seven_cloudapp.models.seven_model import PageInfo
from seven_cloudapp.models.behavior_model import *
from seven_cloudapp.models.db_models.act.act_info_model import *
from seven_cloudapp.models.db_models.user.user_base_model import *
from seven_cloudapp.models.db_models.user.user_info_model import *
from seven_cloudapp.models.db_models.user.user_blacklist_model import *
from seven_cloudapp.models.db_models.machine.machine_info_model import *
from seven_cloudapp.models.db_models.machine.machine_value_model import *
from seven_cloudapp.models.db_models.gear.gear_value_model import *
from seven_cloudapp.models.db_models.lottery.lottery_value_log_model import *
from seven_cloudapp.models.db_models.user.user_detail_model import *


class LoginHandler(SevenBaseHandler):
    """
    :description: 登录处理
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 登录日志入库
        :param owner_open_id：应用拥有者唯一标识
        :param act_id:活动id
        :param owner_open_id:owner_open_id
        :param is_machine:是否机台
        :param is_gear:是否价格挡位
        :return: dict
        :last_editors: HuangJingCan
        """
        open_id = self.get_taobao_param().open_id
        user_nick = self.get_taobao_param().user_nick
        app_id = self.get_taobao_param().source_app_id
        owner_open_id = self.get_param("owner_open_id")
        act_id = int(self.get_param("act_id", 0))
        # 0-没关联机台或者价格挡位，1-关联机台，2-关联价格挡位
        is_machine_gear = config.get_value("is_machine_gear", 0)

        act_dict = ActInfoModel(context=self).get_dict_by_id(act_id)
        if not act_dict:
            return self.reponse_json_error("NoAct", "对不起，活动不存在")

        if is_machine_gear in (1, 2):
            machine_dict_list = MachineInfoModel(context=self).get_dict_list("act_id=%s", params=[act_id])
            if not machine_dict_list:
                return self.reponse_json_error("NoMachine", "对不起，盲盒不存在")

        # 用户基础表
        user_base = UserBaseModel(context=self).get_entity("open_id=%s", params=[open_id])

        user_info_model = UserInfoModel(context=self)
        user_info = user_info_model.get_entity("act_id=%s and open_id=%s", params=[act_id, open_id])

        try:
            if not user_info:
                user_info = UserInfo()
                user_info.open_id = open_id
                user_info.act_id = act_id
                user_info.app_id = app_id
                user_info.is_new = 1
                if user_base:
                    user_info.user_nick = user_base.user_nick
                    user_info.avatar = user_base.avatar
                if user_nick:
                    user_info.user_nick = user_nick
                user_info.create_date = self.get_now_datetime()
                user_info.modify_date = self.get_now_datetime()
                user_info.login_token = SevenHelper.get_random(16, 1)
                user_info.id = user_info_model.add_entity(user_info)
            else:
                if user_base:
                    user_info.user_nick = user_base.user_nick
                    user_info.avatar = user_base.avatar
                if user_nick:
                    user_info.user_nick = user_nick
                user_info.modify_date = self.get_now_datetime()
                user_info.login_token = SevenHelper.get_random(16, 1)
                user_info.is_new = 0
                user_info_model.update_entity(user_info, "modify_date,login_token,is_new,user_nick,avatar")
        except Exception as ex:
            self.logging_link_error(traceback.format_exc())

        user_info_dict = user_info.__dict__

        if is_machine_gear == 1:
            machine_value_list = MachineValueModel(context=self).get_dict_list("act_id=%s and open_id=%s", params=[act_id, open_id])
            user_info_dict["machine_value_list"] = machine_value_list
        elif is_machine_gear == 2:
            gear_value_list = GearValueModel(context=self).get_dict_list("act_id=%s and open_id=%s", params=[act_id, open_id])
            user_info_dict["gear_value_list"] = gear_value_list

        behavior_model = BehaviorModel(context=self)
        # 访问次数
        behavior_model.report_behavior_log(app_id, act_id, open_id, owner_open_id, 'VisitCountEveryDay', 1)
        # 访问人数
        behavior_model.report_behavior_log(app_id, act_id, open_id, owner_open_id, 'VisitManCountEveryDay', 1)
        if user_info.is_new == 1:
            # 新增用户数
            behavior_model.report_behavior_log(app_id, act_id, open_id, owner_open_id, 'VisitManCountEveryDayIncrease', 1)

        return self.reponse_json_success(user_info_dict)


class UserHandler(SevenBaseHandler):
    """
    :description: 更新用户信息
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 更新用户信息
        :param avatar：头像
        :param act_id：活动id
        :return: 
        :last_editors: HuangJingCan
        """
        try:
            open_id = self.get_taobao_param().open_id
            user_nick = self.get_taobao_param().user_nick
            act_id = int(self.get_param("act_id", 0))
            avatar = self.get_param("avatar")

            user_info_model = UserInfoModel(context=self)
            user_info = user_info_model.get_entity("act_id=%s and open_id=%s", params=[act_id, open_id])
            if not user_info:
                return self.reponse_json_error("NoUser", "对不起，用户不存在")

            if user_nick:
                user_info.user_nick = user_nick
            user_info.avatar = avatar
            user_info.is_auth = 1
            user_info.modify_date = self.get_now_datetime()
            user_info_model.update_entity(user_info)

            # 用户基础表
            user_base_model = UserBaseModel(context=self)
            user_base = user_base_model.get_entity("open_id=%s", params=[open_id])
            if user_base:
                if user_nick:
                    user_base.user_nick = user_nick
                if avatar:
                    user_base.avatar = avatar
                user_base.modify_date = self.get_now_datetime()
                user_base_model.update_entity(user_base, "modify_date,avatar,user_nick")
            else:
                user_base = UserBase()
                user_base.open_id = open_id
                if user_nick:
                    user_base.user_nick = user_nick
                if avatar:
                    user_base.avatar = avatar
                user_base.is_auth = 1
                user_base.user_state = 0
                user_base.create_date = self.get_now_datetime()
                user_base.modify_date = self.get_now_datetime()
                user_base_model.add_entity(user_base)

            return self.reponse_json_success("更新成功")
        except Exception as ex:
            return self.reponse_json_error("Error", "更新失败")


class SubmitUnbindHandler(SevenBaseHandler):
    """
    :description: 提交黑名单解封申请
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 提交黑名单解封申请
        :param {act_id:活动id}
        :param {reason:解封理由}
        :return {*}
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        open_id = self.get_taobao_param().open_id
        act_id = int(self.get_param("act_id", 0))
        reason = self.get_param("reason", "误封号,申请解封")

        user_info_model = UserInfoModel(context=self)
        user_info = user_info_model.get_entity("act_id=%s AND open_id=%s", params=[act_id, open_id])
        if not user_info:
            return self.reponse_json_error("Error", "用户信息不存在")
        if user_info.user_state == 0:
            return self.reponse_json_error("Error", "账号正常,无需申请解封")

        user_blacklist_model = UserBlacklistModel(context=self)
        user_blacklist = user_blacklist_model.get_entity("act_id=%s and open_id=%s", order_by="create_date desc", params=[act_id, open_id])

        if not user_blacklist:
            return self.reponse_json_error("Error", "账号正常,无需申请解封")
        if user_blacklist.audit_status == 1:
            return self.reponse_json_error("Error", "请耐心等待客服处理")

        user_blacklist.audit_status = 1
        user_blacklist_model.update_entity(user_blacklist, "audit_status")

        return self.reponse_json_success()


class GetUnbindApplyHandler(SevenBaseHandler):
    """
    :description: 获取黑名单解封申请记录
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 获取黑名单解封申请记录
        :param act_id:活动id
        :return 
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        open_id = self.get_taobao_param().open_id
        act_id = int(self.get_param("act_id", 0))

        user_info_model = UserInfoModel(context=self)
        user_info = user_info_model.get_entity("act_id=%s AND open_id=%s", params=[act_id, open_id])
        if not user_info:
            return self.reponse_json_error("Error", "用户信息不存在")

        user_blacklist_model = UserBlacklistModel(context=self)
        user_blacklist = user_blacklist_model.get_entity("act_id=%s AND open_id=%s", order_by="create_date desc", params=[act_id, open_id])

        return self.reponse_json_success(user_blacklist)


class GetIntegralListHandler(SevenBaseHandler):
    """
    :description: 获取心愿值记录列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 获取心愿值记录列表
        :param act_id:活动id
        :param currency_type:货币类型（0无1次数2积分3价格档位4会员积分）
        :param page_index：页索引
        :param page_size：页大小
        :return list
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        open_id = self.get_taobao_param().open_id
        act_id = int(self.get_param("act_id", 0))
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 20))
        currency_type = int(self.get_param("currency_type", 2))
        lottery_value_log_model = LotteryValueLogModel(context=self)
        condition = "act_id=%s and open_id=%s and currency_type=%s"
        params = [act_id, open_id, currency_type]
        field = "log_title,source_type,current_value,operate_type,create_date"

        lottery_value_log_page_list, total = lottery_value_log_model.get_dict_page_list(field, page_index, page_size, condition, order_by="id desc", params=params)
        if len(lottery_value_log_page_list) > 0:
            for item in lottery_value_log_page_list:
                item["create_date"] = item["create_date"].strftime('%Y-%m-%d')
                # item["create_date"] = item["create_date"].strftime('%Y-%m-%d %H:%M:%S')

        page_info = PageInfo(page_index, page_size, total, lottery_value_log_page_list)

        return self.reponse_json_success(page_info)


class GetUserDetailHandler(SevenBaseHandler):
    """
    :description: 获取用户详情（包含道具卡数量）
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 获取用户详情（包含道具卡数量）
        :param act_id:活动id
        :return
        :last_editors: HuangJianYi
        """
        open_id = self.get_taobao_param().open_id
        app_id = self.get_taobao_param().source_app_id
        act_id = int(self.get_param("act_id", 0))

        act_dict = ActInfoModel(context=self).get_dict_by_id(act_id)
        if not act_dict:
            return self.reponse_json_error("NoAct", "对不起，活动不存在")

        user_detail_model = UserDetailModel(context=self)
        user_detail = user_detail_model.get_entity("act_id=%s and open_id=%s", params=[act_id, open_id])
        if not user_detail:
            user_detail = UserDetail()
            user_detail.app_id = app_id
            user_detail.act_id = act_id
            user_detail.open_id = open_id
            user_detail.tips_card_count = 0
            user_detail.perspective_card_count = 0
            user_detail.redraw_card_count = 0
            user_detail.create_date = self.get_now_datetime()
            user_detail_model.add_entity(user_detail)

        return self.reponse_json_success(user_detail)