# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-05-12 20:04:54
@LastEditTime: 2021-09-02 14:30:53
@LastEditors: HuangJianYi
:description: 用户相关
"""
from seven_cloudapp.handlers.seven_base import *
from seven_cloudapp.libs.customize.oss2help import *

from seven_cloudapp.models.enum import *
from seven_cloudapp.models.seven_model import *
from seven_cloudapp.models.db_models.app.app_info_model import *
from seven_cloudapp.models.db_models.login.login_log_model import *
from seven_cloudapp.models.db_models.user.user_info_model import *
from seven_cloudapp.models.db_models.machine.machine_value_model import *
from seven_cloudapp.models.db_models.user.user_blacklist_model import *
from seven_cloudapp.models.db_models.lottery.lottery_value_log_model import *
from seven_cloudapp.models.db_models.act.act_info_model import *
from seven_cloudapp.models.db_models.coin.coin_order_model import *
from seven_cloudapp.models.db_models.prop.prop_log_model import *
from seven_cloudapp.models.db_models.user.user_detail_model import *


class LoginHandler(SevenBaseHandler):
    """
    :description: 登录处理
    """
    @filter_check_params("open_id")
    def get_async(self):
        """
        :description: 登录日志入库
        :param open_id：用户唯一标识
        :param user_nick：用户昵称
        :return: 
        :last_editors: HuangJingCan
        """
        open_id = self.get_taobao_param().open_id
        user_nick = self.get_taobao_param().user_nick

        request_params = str(self.request_params)

        if user_nick == "":
            return self.reponse_json_success()

        login_log_model = LoginLogModel(context=self)
        login_log = login_log_model.get_entity("open_id=%s", params=open_id)

        is_add = False
        if not login_log:
            is_add = True
            login_log = LoginLog()

        login_log.open_id = open_id
        login_log.user_nick = user_nick
        if user_nick.__contains__(":"):
            login_log.store_user_nick = user_nick.split(":")[0]
            login_log.is_master = 0
        else:
            login_log.store_user_nick = user_nick
            login_log.is_master = 1
        login_log.request_params = request_params
        login_log.modify_date = self.get_now_datetime()

        try:
            if is_add:
                login_log.create_date = login_log.modify_date
                login_log.id = login_log_model.add_entity(login_log)
            else:
                login_log_model.update_entity(login_log)

            #更新登录时间到app_info
            app_id = self.get_app_id()
            if app_id:
                AppInfoModel(context=self).update_table("modify_date=%s", "app_id=%s", [login_log.modify_date, app_id])
        except:
            pass

        self.reponse_json_success()


class UserStatusHandler(SevenBaseHandler):
    """
    :description: 更新用户状态
    """
    @filter_check_params("userid,user_state")
    def get_async(self):
        """
        :description: 更新用户状态
        :param userid：用户id
        :param user_state：用户状态
        :return: 
        :last_editors: HuangJingCan
        """
        user_id = int(self.get_param("userid"))
        user_state = int(self.get_param("user_state"))
        modify_date = self.get_now_datetime()
        relieve_date = self.get_now_datetime()

        UserInfoModel(context=self).update_table("user_state=%s,modify_date=%s,relieve_date=%s", "id=%s", [user_state, modify_date, relieve_date, user_id])

        self.reponse_json_success()


class UserStatusByBlackHandler(SevenBaseHandler):
    """
    :description: 更新用户状态(拉黑)
    """
    @filter_check_params("userid")
    def get_async(self):
        """
        :description: 更新用户状态(拉黑)
        :param userid：用户id
        :return: 
        :last_editors: LaiKaiXiang
        """
        user_id = int(self.get_param("userid"), 0)
        modify_date = self.get_now_datetime()
        relieve_date = self.get_now_datetime()

        if user_id <= 0:
            return self.reponse_json_error("error", "找不到用户!")

        user_model = UserInfoModel(context=self)
        user_black_model = UserBlacklistModel(context=self)

        user_info = user_model.get_entity_by_id(user_id)
        if not user_info:
            return self.reponse_json_error("error", "找不到用户!")

        if user_info.user_state == 1:
            return self.reponse_json_error("error", "该用户已是黑名单!")

        user_model.update_table("user_state=1,modify_date=%s,relieve_date=%s", "id=%s", [modify_date, relieve_date, user_id])

        user_blacklist = user_black_model.get_entity("open_id=%s and act_id=%s", params=[user_info.open_id, user_info.act_id])

        if not user_blacklist:
            #添加到用户黑名单管理表
            user_blacklist = UserBlacklist()
            user_blacklist.app_id = user_info.app_id
            user_blacklist.act_id = user_info.act_id
            user_blacklist.open_id = user_info.open_id
            user_blacklist.user_nick = user_info.user_nick
            user_blacklist.black_type = 2
            user_blacklist.refund_order_data = []
            user_blacklist.create_date = self.get_now_datetime()
            user_black_model.add_entity(user_blacklist)
        else:
            user_blacklist.audit_status = 0
            user_blacklist.black_type = 2
            user_blacklist.create_date = self.get_now_datetime()
            user_black_model.update_entity(user_blacklist)

        self.reponse_json_success()


class UserListHandler(SevenBaseHandler):
    """
    :description: 用户列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 用户列表
        :param page_index:页索引
        :param page_size:页大小
        :param act_id:活动id
        :param user_nick:用户昵称
        :param open_id:open_id
        :param user_state:用户状态
        :param is_integral:是否需要用剩余积分计算剩余次数 0不需要 1需要
        :return PageInfo
        :last_editors: HuangJingCan
        """
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 20))
        act_id = int(self.get_param("act_id", 0))
        user_nick = self.get_param("nick_name")
        user_open_id = self.get_param("user_open_id")
        user_state = int(self.get_param("user_state", -1))
        is_integral = int(self.get_param("is_integral", 0))

        condition = "act_id=%s"
        params = [act_id]

        if user_nick:
            condition += " AND user_nick=%s"
            params.append(user_nick)
        if user_open_id:
            condition += " AND open_id=%s"
            params.append(user_open_id)
        if user_state >= 0:
            condition += " AND user_state=%s"
            params.append(user_state)

        page_list, total = UserInfoModel(context=self).get_dict_page_list("*", page_index, page_size, condition, order_by="id desc", params=params)

        if is_integral == 1:
            act_dict = ActInfoModel(context=self).get_dict_by_id(act_id)
            if act_dict:
                for user_info in page_list:
                    user_info['lottery_value'] = user_info['surplus_integral'] // act_dict['lottery_value']

        page_info = PageInfo(page_index, page_size, total, page_list)

        return self.reponse_json_success(page_info)


class UserListExportHandler(SevenBaseHandler):
    """
    :description: 用户列表导出
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 用户列表
        :param page_index：页索引
        :param page_size：页大小
        :param act_id：活动id
        :param user_nick：用户昵称
        :return PageInfo
        :last_editors: HuangJingCan
        """
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 20))
        act_id = int(self.get_param("act_id", 0))
        user_nick = self.get_param("nick_name")
        user_state = int(self.get_param("user_state", -1))

        condition = "act_id=%s"
        params = [act_id]

        if user_nick:
            condition += " AND user_nick=%s"
            params.append(user_nick)
        if user_state >= 0:
            condition += " AND user_state=%s"
            params.append(user_state)

        page_list, total = UserInfoModel(context=self).get_dict_page_list("*", page_index, page_size, condition, order_by="id desc", params=params)

        #订单奖品
        result_data = []
        for page in page_list:
            data_row = {}
            data_row["淘宝名"] = page["user_nick"]
            data_row["累计消费金额(排除退款)"] = str(page["store_pay_price"])
            data_row["剩余抽奖次数"] = str(page["lottery_sum"])
            data_row["剩余积分"] = str(page["surplus_integral"])
            data_row["创建时间"] = page["create_date"]
            if page["user_state"] == 0:
                data_row["状态"] = "正常"
            else:
                data_row["状态"] = "黑名单"

            result_data.append(data_row)

        resource_path = ""
        if result_data:
            path = "temp/" + UUIDHelper.get_uuid() + ".xlsx"
            ExcelHelper.export(result_data, path)

            resource_path = OSS2Helper().upload("", path, config.get_value("oss_folder"), False)

            os.remove(path)

        self.reponse_json_success(resource_path)


class UserBlackStatusHandler(SevenBaseHandler):
    """
    docstring 黑名单状态管理
    """
    @filter_check_params("black_id,audit_status")
    def get_async(self):
        """
        :description: 黑名单状态管理
        :param black_id：用户黑名单管理id
        :param audit_status：审核状态(0黑名单1申请中2同意3拒绝)
        :return: reponse_json_success
        :last_editors: LaiKaiXiang
        """
        black_id = int(self.get_param("black_id", 0))
        audit_status = int(self.get_param("audit_status", 0))
        audit_date = self.get_now_datetime()

        if black_id <= 0:
            return self.reponse_json_error("error", "找不到该条记录!")

        user_blacklist_model = UserBlacklistModel(context=self)
        black_info = user_blacklist_model.get_entity_by_id(black_id)
        if not black_info:
            return self.reponse_json_error("error", "找不到该条记录!")

        user_info_model = UserInfoModel(context=self)

        if audit_status == 2:
            user_blacklist_model.update_table("audit_status=%s,audit_date=%s", "id=%s", [audit_status, audit_date, black_id])
            userInfo = user_info_model.get_entity("act_id=%s and open_id=%s", params=[black_info.act_id, black_info.open_id])
            if not userInfo:
                return self.reponse_json_error("error", "找不到用户!")

            userInfo.user_state = 0
            userInfo.modify_date = audit_date
            userInfo.relieve_date = audit_date
            user_info_model.update_entity(userInfo)

        if audit_status == 0:
            user_blacklist_model.update_table("audit_status=%s,audit_date=%s,black_type=2", "id=%s", [audit_status, audit_date, black_id])
            userInfo = user_info_model.get_entity("act_id=%s and open_id=%s", params=[black_info.act_id, black_info.open_id])
            if not userInfo:
                return self.reponse_json_error("error", "找不到用户!")

            userInfo.user_state = 1
            userInfo.modify_date = audit_date
            user_info_model.update_entity(userInfo)

        if audit_status == 3:
            user_blacklist_model.update_table("audit_status=%s,audit_date=%s", "id=%s", [audit_status, audit_date, black_id])

        self.reponse_json_success()


class UserBlackListHandler(SevenBaseHandler):
    """
    获取黑名单管理列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 获取黑名单管理列表
        :param act_id：act_id
        :param audit_status：状态
        :param nick_name：用户昵称
        :param create_date_start：创建时间开始
        :param create_date_end：创建时间结束
        :return: list
        :last_editors: LaiKaiXiang
        """
        act_id = int(self.get_param("act_id", 0))
        audit_status = int(self.get_param("audit_status", -1))
        user_nick = self.get_param("nick_name")
        create_date_start = self.get_param("create_date_start")
        create_date_end = self.get_param("create_date_end")

        if act_id <= 0:
            return self.reponse_json_error_params()

        condition = "act_id=%s"
        params = [act_id]

        if audit_status >= 0:
            condition += " AND audit_status=%s"
            params.append(audit_status)
        if user_nick:
            condition += " AND user_nick=%s"
            params.append(user_nick)
        if create_date_start:
            condition += " AND create_date>=%s"
            params.append(create_date_start)
        if create_date_end:
            condition += " AND create_date<=%s"
            params.append(create_date_end)

        user_black_dict_list = UserBlacklistModel(context=self).get_dict_list(condition, order_by="create_date desc", params=params)

        for user_black in user_black_dict_list:
            user_black["refund_order_data"] = self.json_loads(user_black["refund_order_data"]) if user_black["refund_order_data"] else []

        self.reponse_json_success(user_black_dict_list)


class LotteryValueHandler(SevenBaseHandler):
    """
    :description: 设置抽奖次数或者积分
    """
    @filter_check_params("user_open_id,act_id")
    def post_async(self):
        """
        :description: 设置抽奖次数或者积分
        :param user_open_id：用户唯一标识
        :param current_value：修改的次数
        :return: reponse_json_success
        :last_editors: LaiKaiXiang
        """
        user_open_id = self.get_param("user_open_id")
        current_value = int(self.get_param("current_value", 0))
        act_id = int(self.get_param("act_id", 0))
        app_id = self.get_param("app_id")
        modify_date = self.get_now_datetime()

        if act_id <= 0:
            return self.reponse_json_error_params()
        act_dict = ActInfoModel(context=self).get_dict_by_id(act_id)
        if not act_dict:
            return self.reponse_json_error_params()

        user_info_model = UserInfoModel(context=self)
        user_info = user_info_model.get_entity("open_id=%s and act_id=%s", params=[user_open_id, act_id])
        if not user_info:
            return self.reponse_json_error_params()

        history_value = 0
        if act_dict['currency_type'] == 1:
            history_value = user_info.lottery_value
        elif act_dict['currency_type'] == 2:
            history_value = user_info.surplus_integral
        if history_value != current_value:
            update_sql = ""
            if act_dict['currency_type'] == 1:
                update_sql = "lottery_value=%s,modify_date=%s"
            if act_dict['currency_type'] == 2:
                update_sql = "surplus_integral=%s,modify_date=%s"
            if update_sql == "":
                return self.reponse_json_success()
            result = user_info_model.update_table(update_sql, "act_id=%s AND open_id=%s", [current_value, modify_date, act_id, user_open_id])
            if result:
                lottery_value_log = LotteryValueLog()
                lottery_value_log.app_id = app_id
                lottery_value_log.act_id = act_id
                lottery_value_log.open_id = user_open_id
                lottery_value_log.user_nick = user_info.user_nick
                lottery_value_log.log_title = "手动配置"
                lottery_value_log.source_type = SourceType.手动配置.value
                lottery_value_log.change_type = 301 if int(current_value - history_value) > 0 else 302
                lottery_value_log.operate_type = 0 if int(current_value - history_value) > 0 else 1
                lottery_value_log.current_value = current_value - history_value
                lottery_value_log.history_value = history_value
                lottery_value_log.log_info = {}
                lottery_value_log.create_date = self.get_now_datetime()
                LotteryValueLogModel(context=self).add_entity(lottery_value_log)

                #添加商家对帐记录
                coin_order_model = CoinOrderModel(context=self)
                if (current_value - history_value) > 0:
                    coin_order = CoinOrder()
                    coin_order.open_id = user_open_id
                    coin_order.app_id = app_id
                    coin_order.act_id = act_id
                    coin_order.reward_type = 0
                    coin_order.nick_name = user_info.user_nick
                    coin_order.buy_count = current_value - history_value
                    coin_order.surplus_count = current_value - history_value
                    coin_order.create_date = self.get_now_datetime()
                    coin_order.modify_date = self.get_now_datetime()
                    coin_order_model.add_entity(coin_order)
                else:
                    del_count = history_value - current_value
                    update_coin_order_list = []
                    coin_order_set_list = coin_order_model.get_list("act_id=%s and open_id=%s and surplus_count>0 and pay_order_id=0", "id asc", params=[act_id, user_open_id])

                    if len(coin_order_set_list) > 0:
                        for coin_order in coin_order_set_list:
                            if coin_order.surplus_count > del_count:
                                coin_order.surplus_count = coin_order.surplus_count - del_count
                                del_count = 0
                            else:
                                del_count = del_count - coin_order.surplus_count
                                coin_order.surplus_count = 0
                            update_coin_order_list.append(coin_order)
                            if del_count == 0:
                                break
                    if del_count > 0:
                        coin_order_pay_list = coin_order_model.get_list("act_id=%s and open_id=%s and surplus_count>0 and pay_order_id>0", "id asc", params=[act_id, user_open_id])
                        if len(coin_order_pay_list) > 0:
                            for coin_order in coin_order_pay_list:
                                if coin_order.surplus_count > del_count:
                                    coin_order.surplus_count = coin_order.surplus_count - del_count
                                    del_count = 0
                                else:
                                    del_count = del_count - coin_order.surplus_count
                                    coin_order.surplus_count = 0
                                update_coin_order_list.append(coin_order)
                                if del_count == 0:
                                    break
                    for coin_order in update_coin_order_list:
                        coin_order_model.update_entity(coin_order)

        self.reponse_json_success()


class LotteryValueLogHandler(SevenBaseHandler):
    """
    :description: 用户抽奖配置记录
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 用户抽奖配置记录
        :param page_index：页索引
        :param page_size：页大小
        :param act_id：活动id
        :param nick_name：淘宝名
        :param start_date：开始时间
        :param end_date：结束时间
        :param source_type：来源类型
        :param user_open_id：用户open_id
        :return list
        :last_editors: HuangJingCan
        """
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 20))
        act_id = int(self.get_param("act_id", 0))
        user_nick = self.get_param("nick_name")
        start_date = self.get_param("start_date")
        end_date = self.get_param("end_date")
        source_type = int(self.get_param("source_type", -1))
        user_open_id = self.get_param("user_open_id")

        condition = "act_id=%s"
        params = [act_id]

        if source_type >= 0:
            condition += " AND source_type=%s"
            params.append(source_type)
        if user_open_id:
            condition += " AND open_id=%s"
            params.append(user_open_id)
        if user_nick:
            condition += " AND user_nick=%s"
            params.append(user_nick)
        if start_date:
            condition += " AND create_date>=%s"
            params.append(start_date)
        if end_date:
            condition += " AND create_date<=%s"
            params.append(end_date)

        page_list, total = LotteryValueLogModel(context=self).get_dict_page_list("*", page_index, page_size, condition, order_by="id desc", params=params)

        page_info = PageInfo(page_index, page_size, total, page_list)

        self.reponse_json_success(page_info)


class LotteryValueLogExportHandler(SevenBaseHandler):
    """
    :description: 用户积分记录导出
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 用户积分记录导出
        :param page_index：页索引
        :param page_size：页大小
        :param act_id：活动id
        :param nick_name：淘宝名
        :param start_date：开始时间
        :param end_date：结束时间
        :return list
        :last_editors: HuangJingCan
        """
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 20))
        act_id = int(self.get_param("act_id", 0))
        user_nick = self.get_param("nick_name")
        start_date = self.get_param("start_date")
        end_date = self.get_param("end_date")

        condition = "act_id=%s"
        params = [act_id]

        if user_nick:
            condition += " AND user_nick=%s"
            params.append(user_nick)
        if start_date:
            condition += " AND create_date>=%s"
            params.append(start_date)
        if end_date:
            condition += " AND create_date<=%s"
            params.append(end_date)

        page_list, total = LotteryValueLogModel(context=self).get_dict_page_list("*", page_index, page_size, condition, order_by="id desc", params=params)

        result_data = []
        for page in page_list:
            data_row = {}
            data_row["淘宝名"] = page["user_nick"]
            data_row["变动原因"] = page["log_title"]
            data_row["变动时间"] = page["create_date"]
            data_row["变动值"] = str(page["current_value"])
            data_row["备注"] = page["log_desc"]

            result_data.append(data_row)

        resource_path = ""
        if result_data:
            path = "temp/" + UUIDHelper.get_uuid() + ".xlsx"
            ExcelHelper.export(result_data, path)

            resource_path = OSS2Helper().upload("", path, config.get_value("oss_folder"), False)

            os.remove(path)

        self.reponse_json_success(resource_path)


class UserDetailHandler(SevenBaseHandler):
    """
    :description:  用户详情(道具数量)   
    """
    @filter_check_params("user_open_id,act_id")
    def get_async(self):
        """
        :description: 用户详情
        :param user_open_id：用户唯一标识
        :return: reponse_json_success
        :last_editors: HuangJianYi
        """
        user_open_id = self.get_param("user_open_id")
        act_id = int(self.get_param("act_id", 0))

        condition = "act_id=%s and open_id=%s"
        params = [act_id, user_open_id]

        user_detail_model = UserDetailModel(context=self)
        user_detail = user_detail_model.get_entity(condition, params=params)

        if not user_detail:
            user_detail = UserDetail()
            user_detail.tips_card_count = 0
            user_detail.perspective_card_count = 0
            user_detail.redraw_card_count = 0

        return self.reponse_json_success(user_detail)


class PropLogHandler(SevenBaseHandler):
    """
    :description: 道具数量变动明细记录
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 道具数量变动明细记录
        :param page_index：页索引
        :param page_size：页大小
        :param act_id：活动id
        :param nick_name：淘宝名
        :param start_date：开始时间
        :param end_date：结束时间
        :param user_open_id：用户open_id
        :return list
        :last_editors: HuangJianYi
        """
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 20))
        act_id = int(self.get_param("act_id", 0))
        change_type = int(self.get_param("change_type", 0))
        user_nick = self.get_param("nick_name")
        start_date = self.get_param("start_date")
        end_date = self.get_param("end_date")
        user_open_id = self.get_param("user_open_id")

        condition = "act_id=%s"
        params = [act_id]
        field = "user_nick,change_type,operate_type,prop_type,machine_name,specs_type,operate_value,history_value,title,create_date"

        if user_open_id:
            condition += " AND open_id=%s"
            params.append(user_open_id)
        if user_nick:
            condition += " AND user_nick=%s"
            params.append(user_nick)
        if start_date:
            condition += " AND create_date>=%s"
            params.append(start_date)
        if end_date:
            condition += " AND create_date<=%s"
            params.append(end_date)
        if change_type > 0:
            condition += " AND change_type=%s"
            params.append(change_type)

        page_list, total = PropLogModel(context=self).get_dict_page_list(field, page_index, page_size, condition, order_by="id desc", params=params)
        for page in page_list:
            page["operate_value"] = str(page["operate_value"]) if int(page["operate_value"]) < 0 else "+" + str(page["operate_value"])
        page_info = PageInfo(page_index, page_size, total, page_list)

        self.reponse_json_success(page_info)