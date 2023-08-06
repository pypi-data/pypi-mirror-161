# -*- coding: utf-8 -*-
"""
:Author: CaiYouBin
:Date: 2020-05-12 20:04:54
@LastEditTime: 2022-02-24 15:22:14
@LastEditors: HuangJianYi
:description: 基础接口
"""
from seven_framework.qr_code import *
from seven_cloudapp.handlers.seven_base import *

from seven_cloudapp.models.enum import *
from seven_cloudapp.models.seven_model import PageInfo
from seven_cloudapp.models.db_models.theme.theme_info_model import *
from seven_cloudapp.models.db_models.skin.skin_info_model import *
from seven_cloudapp.models.db_models.act.act_prize_model import *
from seven_cloudapp.models.db_models.act.act_info_model import *
from seven_cloudapp.models.db_models.act.act_type_model import *
from seven_cloudapp.models.db_models.app.app_info_model import *
from seven_cloudapp.models.db_models.base.base_info_model import *
from seven_cloudapp.models.db_models.marketing.marketing_program_model import *


class MarketingProgramHandler(SevenBaseHandler):
    """
    :description: 营销方案
    """
    def get_async(self):
        """
        :description: 营销方案获取
        :param {type} 
        :return: 列表
        :last_editors: HuangJingCan
        """
        marketing_program_list = MarketingProgramModel(context=self).get_dict_list()

        return self.reponse_json_success(marketing_program_list)


class ActTypeListHandler(SevenBaseHandler):
    """
    :description: 活动类型列表
    """
    def get_async(self):
        """
        :description: 活动类型获取
        :param marketing_id：营销方案id
        :param is_act：该活动类型是否创建过活动
        :return: 列表
        :last_editors: HuangJingCan
        """
        is_act = int(self.get_param("is_act", 0))
        app_id = self.get_param("app_id")

        marketing_id = int(self.get_param("marketing_id", 0))
        condition = ""
        if marketing_id > 0:
            condition = "marketing_id LIKE '%," + str(marketing_id) + ",%'"

        act_type_list = ActTypeModel(context=self).get_list(condition)

        new_list = []

        for info in act_type_list:
            info.play_process = self.json_loads(info.play_process) if info.play_process else {}
            info.applicable_behavior = self.json_loads(info.applicable_behavior) if info.applicable_behavior else {}
            info.market_function = self.json_loads(info.market_function) if info.market_function else {}
            info.skill_case = self.json_loads(info.skill_case) if info.skill_case else []
            info.type_desc = self.json_loads(info.type_desc) if info.type_desc else []
            info.share_desc = self.json_loads(info.share_desc) if info.share_desc else {}
            info.rule_desc = self.json_loads(info.rule_desc) if info.rule_desc else []
            info.integral_rule = self.json_loads(info.integral_rule) if info.integral_rule else []
            info.act_id = 0
            if is_act > 0 and app_id:
                act_dict = ActInfoModel(context=self).get_dict("app_id=%s and act_type=%s", params=[app_id, info.id])
                if act_dict:
                    info.act_id = act_dict['id']

            new_list.append(info.__dict__)

        return self.reponse_json_success(new_list)


class ActCreateHandler(SevenBaseHandler):
    """
    :description: 创建活动
    """
    @filter_check_params("act_type,app_id")
    def get_async(self):
        """
        :description: 创建活动
        :param app_id：app_id
        :param act_type：活动类型
        :param act_name：活动名称
        :param theme_id：主题id
        :return act_id
        :last_editors: HuangJingCan
        """
        owner_open_id = self.get_taobao_param().open_id
        app_id = self.get_param("app_id")
        act_name = self.get_param("act_name")
        act_type = int(self.get_param("act_type", 1))
        theme_id = int(self.get_param("theme_id", 1))
        now_datetime = self.get_now_datetime()

        base_info = BaseInfoModel(context=self).get_entity()
        if not base_info:
            return self.reponse_json_error("BaseInfoError", "基础信息出错")
        theme_info = ThemeInfoModel(context=self).get_entity()
        if not theme_info:
            return self.reponse_json_error("NoTheme", "请管理员先上传主题信息")
        skin_info = SkinInfoModel(context=self).get_entity("theme_id=%s", params=theme_info.id)
        if not skin_info:
            return self.reponse_json_error("NoSkin", "请管理员先上传皮肤信息")
        act_type_info = ActTypeModel(context=self).get_entity("id=%s", params=act_type)
        if not act_type_info:
            return self.reponse_json_error("NoActType", "无活动类型信息")

        #增加默认活动
        act_info_model = ActInfoModel(context=self)
        act_count = act_info_model.get_total("app_id=%s", params=app_id)

        act_info = ActInfo()
        act_info.app_id = app_id
        act_info.owner_open_id = owner_open_id
        act_info.act_name = base_info.product_name + "_" + str(act_count + 1)
        act_info.act_type = act_type
        act_info.theme_id = theme_info.id
        act_info.close_word = "抱歉，程序维护中"
        act_info.share_desc = self.json_dumps(act_type_info.share_desc) if act_type_info.share_desc else {}
        act_info.rule_desc = self.json_dumps(act_type_info.rule_desc) if act_type_info.rule_desc else []
        act_info.integral_rule = self.json_dumps(act_type_info.integral_rule) if act_type_info.integral_rule else []
        act_info.start_date = now_datetime
        act_info.end_date = "2900-01-01 00:00:00"
        act_info.refund_count = 0
        act_info.is_black = 0
        act_info.sort_index = 0
        act_info.is_release = 1
        act_info.join_ways = 0
        act_info.is_fictitious = 0
        act_info.currency_type = act_type_info.currency_type
        act_info.task_currency_type = act_type_info.task_currency_type
        act_info.lottery_value = 0
        act_info.release_date = now_datetime
        act_info.create_date = now_datetime
        act_info.modify_date = now_datetime

        act_info.id = act_info_model.add_entity(act_info)

        self.create_operation_log(OperationType.add.value, act_info.__str__(), "ActCreateHandler", None, self.json_dumps(act_info))

        return self.reponse_json_success(act_info.id)


class ActHandler(SevenBaseHandler):
    """
    :description: 修改活动
    """
    @filter_check_params("act_id,act_name")
    def post_async(self):
        """
        :description: 修改活动
        :param act_id：活动id
        :param act_name：活动名称
        :param theme_id：主题ID
        :param store_url：店铺地址
        :param close_word：关闭小程序文案
        :param share_desc：分享内容
        :param rule_desc：规则内容
        :param integral_rule：积分规则
        :param start_date：开始时间
        :param end_date：结束时间
        :param refund_count：退款次数
        :param is_black：是否开启黑名单
        :param sort_index：排序号
        :param is_release：是否发布（1是0否）
        :param join_ways：活动参与条件（0所有1关注店铺2加入会员）
        :param is_fictitious：是否开启虚拟中奖
        :param currency_type 抽奖货币类型（0无1次数2积分3价格档位4抽奖码）
        :param lottery_value 单次抽奖消耗次数（积分）
        :return act_id
        :last_editors: HuangJingCan
        """
        act_id = int(self.get_param("act_id", 0))
        act_name = self.get_param("act_name")
        theme_id = int(self.get_param("theme_id", 1))
        store_url = self.get_param("store_url")
        close_word = self.get_param("close_word", "抱歉，程序维护中")
        share_desc = self.get_param("share_desc")
        rule_desc = self.get_param("rule_desc")
        integral_rule = self.get_param("integral_rule")
        start_date = self.get_param("start_date")
        end_date = self.get_param("end_date")
        refund_count = int(self.get_param("refund_count", 0))
        is_black = int(self.get_param("is_black", 0))
        sort_index = int(self.get_param("sort_index", 1))
        is_release = int(self.get_param("is_release", 0))
        join_ways = int(self.get_param("join_ways", 0))
        is_fictitious = int(self.get_param("is_fictitious", 0))
        lottery_value = int(self.get_param("lottery_value", 0))

        act_info_model = ActInfoModel(context=self)
        act_info = act_info_model.get_entity_by_id(act_id)

        if not act_info:
            return self.reponse_json_error("NoAct", "对不起，找不到该活动")

        old_act_info = deepcopy(act_info)

        act_info.act_name = act_name
        act_info.theme_id = theme_id
        act_info.store_url = store_url
        act_info.close_word = close_word
        act_info.share_desc = share_desc if share_desc != "" else {}
        act_info.rule_desc = rule_desc if rule_desc != "" else []
        act_info.integral_rule = integral_rule if integral_rule != "" else []
        act_info.start_date = start_date if start_date else self.get_now_datetime()
        act_info.end_date = end_date if end_date else "2900-01-01 00:00:00"
        act_info.refund_count = refund_count
        act_info.is_black = is_black
        act_info.sort_index = sort_index
        act_info.is_release = is_release
        act_info.join_ways = join_ways
        act_info.is_fictitious = is_fictitious
        act_info.lottery_value = lottery_value
        act_info.modify_date = self.get_now_datetime()

        act_info_model.update_entity(act_info)

        self.create_operation_log(OperationType.update.value, act_info.__str__(), "ActHandler", self.json_dumps(old_act_info), self.json_dumps(act_info))

        return self.reponse_json_success()


class ActListHandler(SevenBaseHandler):
    """
    :description: 活动列表
    """
    def get_async(self):
        """
        :description: 获取活动列表
        :param act_name：活动名称
        :param page_index：页索引
        :param page_size：页大小
        :return: PageInfo
        :last_editors: HuangJingCan
        """
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 10))
        is_del = int(self.get_param("is_del", 0))
        act_name = self.get_param("act_name")
        app_id = self.get_app_id()

        if app_id:
            order_by = "id ASC"
            condition = "app_id=%s"
            if is_del == 0:
                condition += "AND is_del=0"
            else:
                condition += "AND is_del=1"

            page_list, total = ActInfoModel(context=self).get_dict_page_list("*", page_index, page_size, condition, "", order_by, app_id)

            for page in page_list:
                page["task_currency_type"] = self.json_loads(page["task_currency_type"]) if page["task_currency_type"] else {}
                page["share_desc"] = self.json_loads(page["share_desc"]) if page["share_desc"] else {}
                page["rule_desc"] = self.json_loads(page["rule_desc"]) if page["rule_desc"] else []
                page["menu_configed"] = self.json_loads(page["menu_configed"]) if page["menu_configed"] else []
                page["online_url"] = self.get_online_url(page['id'], app_id)
                page["live_url"] = self.get_live_url(app_id)
                page["finish_status"] = page["finish_progress"]

            page_info = PageInfo(page_index, page_size, total, page_list)

            return self.reponse_json_success(page_info)

        return self.reponse_json_success({"data": []})


class ActInfoHandler(SevenBaseHandler):
    """
    :description: 活动信息获取
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 活动信息获取
        :param act_id：活动id
        :return: 活动信息
        :last_editors: HuangJingCan
        """
        act_id = int(self.get_param("act_id", 0))

        act_info = ActInfoModel(context=self).get_dict_by_id(act_id)

        if act_info:
            act_info["task_currency_type"] = self.json_loads(act_info["task_currency_type"]) if act_info["task_currency_type"] else {}
            act_info['share_desc'] = self.json_loads(act_info['share_desc']) if act_info['share_desc'] != "" else {}
            act_info['rule_desc'] = self.json_loads(act_info['rule_desc']) if act_info['rule_desc'] != "" else []
            act_info['menu_configed'] = self.json_loads(act_info['menu_configed']) if act_info['menu_configed'] != "" else []
            act_info['online_url'] = self.get_online_url(act_info['id'], act_info['app_id'])
            act_info['live_url'] = self.get_live_url(act_info['app_id'])

            return self.reponse_json_success(act_info)

        return self.reponse_json_success()


class ActDelHandler(SevenBaseHandler):
    """
    :description: 删除或者还原活动
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 删除或者还原活动
        :param act_id：活动id
        :param is_del：0-还原，1-删除
        :return: 
        :last_editors: HuangJingCan
        """
        act_id = int(self.get_param("act_id", 0))
        is_del = int(self.get_param("is_del", 1))
        modify_date = self.get_now_datetime()

        if act_id <= 0:
            return self.reponse_json_error_params()

        is_release = 0 if is_del == 1 else 1

        ActInfoModel(context=self).update_table("is_del=%s,is_release=%s,modify_date=%s", "id=%s", [is_del, is_release, modify_date, act_id])

        return self.reponse_json_success()


class ActReleaseHandler(SevenBaseHandler):
    """
    :description: 上架下架活动
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 上架下架活动
        :param act_id：活动id
        :return 
        :last_editors: LaiKaiXiang
        """
        act_id = self.get_param("act_id")
        is_release = int(self.get_param("is_release", 0))
        modify_date = self.get_now_datetime()

        ActInfoModel(context=self).update_table("modify_date=%s,is_release=%s", "id=%s", [modify_date, is_release, act_id])

        return self.reponse_json_success()


class ActQrCodeHandler(SevenBaseHandler):
    """
    :description: 活动二维码获取
    """
    @filter_check_params("url")
    def get_async(self):
        """
        :description: 活动二维码获取
        :param act_id：活动id
        :return: 活动二维码图片
        :last_editors: HuangJingCan
        """
        url = self.get_param("url")

        img, img_bytes = QRCodeHelper.create_qr_code(url, fill_color="black")
        img_base64 = base64.b64encode(img_bytes).decode()

        return self.reponse_json_success(f"data:image/jpeg;base64,{img_base64}")


class ActReviewHandler(SevenBaseHandler):
    """
    :description: 还原活动
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 还原活动
        :param act_id：活动id
        :return 
        :last_editors: HuangJingCan
        """
        act_id = self.get_param("act_id")
        modify_date = self.get_now_datetime()

        app_id = self.get_app_id()

        if not app_id:
            return self.reponse_json_error("NoAppId", "对不起，app_id不存在")

        act_info_model = ActInfoModel(context=self)
        act_info_total = act_info_model.get_total("app_id=%s and is_del=0", params=app_id)
        if act_info_total > 9:
            return self.reponse_json_error("OverAct", "对不起，活动不可超过10个")

        act_info_model.update_table("is_del=0,modify_date=%s,is_release=1", "id=%s", [modify_date, act_id])

        return self.reponse_json_success()


class NextProgressHandler(SevenBaseHandler):
    """
    :description: 下一步
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 下一步
        :param act_id：活动id
        :param finish_key：finish_key
        :return 
        :last_editors: HuangJingCan
        """
        act_id = int(self.get_param("act_id", 0))
        finish_key = self.get_param("finish_key")

        base_info = BaseInfoModel(context=self).get_entity()
        if not base_info:
            return self.reponse_json_error("Error", "对不起，请与管理员联系")

        act_info_model = ActInfoModel(context=self)
        act_info = act_info_model.get_dict_by_id(act_id)
        if not act_info:
            return self.reponse_json_error("NoAct", "对不起，找不到当前活动")

        menu_config = self.json_loads(base_info.menu_config)
        menu = [menu for menu in menu_config if menu["key"] == finish_key]
        if len(menu) == 0:
            return self.reponse_json_error("Error", "对不起，无此菜单")

        if act_info["menu_configed"] != "" and finish_key in act_info["menu_configed"]:
            return self.reponse_json_success()

        if act_info["menu_configed"] == "":
            act_info["menu_configed"] = "[]"

        menu_configed = self.json_loads(act_info["menu_configed"])
        menu_configed.append(finish_key)

        result_menu_configed = []
        for item in menu_configed:
            is_exist = [item2 for item2 in menu_config if item2["key"] == item]
            if len(is_exist) > 0:
                result_menu_configed.append(item)

        finish_progress = 0
        if finish_key == "finish_config" and act_info["finish_progress"] == 0:
            finish_progress = 1

        result_menu_configed = self.json_dumps(result_menu_configed)

        act_info_model.update_table("menu_configed=%s,finish_progress=%s", "id=%s", [result_menu_configed, finish_progress, act_id])

        if finish_progress == 1:
            app_id = self.get_app_id()
            if app_id:
                AppInfoModel(context=self).update_table("is_setting=1", "app_id=%s", app_id)

        return self.reponse_json_success()