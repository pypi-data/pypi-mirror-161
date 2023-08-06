# -*- coding: utf-8 -*-
"""
:Author: LaiKaiXiang
:Date: 2020-11-16 13:44:20
:LastEditTime: 2021-09-03 11:37:05
:LastEditors: HuangJingCan
:description: 
"""
from seven_cloudapp.handlers.seven_base import *

from seven_cloudapp.models.db_models.behavior.behavior_log_model import *
from seven_cloudapp.models.db_models.behavior.behavior_orm_model import *
from seven_cloudapp.models.db_models.behavior.behavior_report_model import *
from seven_cloudapp.models.db_models.act.act_info_model import *


class ReportTotalHandler(SevenBaseHandler):
    """
    :description: 各类总数统计
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 各类总数统计
        :param act_id：活动id
        :return dict
        :last_editors: LaiKaiXiang
        """
        act_id = int(self.get_param("act_id", 0))

        behavior_report_model = BehaviorReportModel(context=self)

        sum_visit = behavior_report_model.get_dict("act_id=%s and key_name=%s", field="sum(key_value) as key_value", params=[act_id, "VisitManCountEveryDayIncrease"])
        sum_lottery = behavior_report_model.get_dict("act_id=%s and key_name=%s", field="sum(key_value) as key_value", params=[act_id, "LotteryAddUserCount"])
        # sum_win = behavior_report_model.get_dict("act_id=%s and key_name=%s", field="sum(key_value) as key_value", params=[act_id, "WinLotteryAddUserCount"])
        sum_reward = behavior_report_model.get_dict("act_id=%s and key_name=%s", field="sum(key_value) as key_value", params=[act_id, "TotalRewardCount"])

        data_list = []
        data = {}
        data["title"] = "总访问人数"
        data["value"] = int(sum_visit["key_value"]) if sum_visit["key_value"] else 0
        data_list.append(data)
        data = {}
        data["title"] = "总抽奖人数"
        data["value"] = int(sum_lottery["key_value"]) if sum_lottery["key_value"] else 0
        data_list.append(data)
        data = {}
        data["title"] = "奖励发放总量"
        data["value"] = int(sum_reward["key_value"]) if sum_reward["key_value"] else 0
        data_list.append(data)

        return self.reponse_json_success(data_list)


class ReportInfoHandler(SevenBaseHandler):
    """
    :description: 关键数据获取(表格)
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 关键数据获取(表格)
        :param act_id：活动id
        :return list
        :last_editors: LaiKaiXiang
        """
        act_id = int(self.get_param("act_id", 0))
        start_date = self.get_param("start_date")
        end_date = self.get_param("end_date")

        act_dict = ActInfoModel(context=self).get_dict_by_id(act_id)
        if not act_dict:
            return self.reponse_json_success([])

        act_type = act_dict['act_type']

        condition = "act_id=%s"
        params = [act_id]

        if start_date != "":
            condition += " and create_date>=%s"
            params.append(start_date)
        if end_date != "":
            condition += " and create_date<%s"
            params.append(TimeHelper.add_days_by_format_time(end_date, 1))

        behavior_orm_model = BehaviorOrmModel(context=self)
        behavior_report_model = BehaviorReportModel(context=self)

        # behavior_orm_list = behavior_orm_model.get_list("(is_common=1 and act_type=%s) or act_id=%s", order_by="sort_index asc", params=[act_type, act_id])
        behavior_orm_list = behavior_orm_model.get_list("((is_common=1 and act_type=%s) or act_id=%s) and is_release=1", order_by="sort_index asc", params=[act_type, act_id])
        behavior_report_list = behavior_report_model.get_dict_list(condition, group_by="key_name", field="key_name,SUM(key_value) AS key_value", params=params)

        #公共映射组（未去重）
        common_groups_1 = [orm.group_name for orm in behavior_orm_list if orm.is_common == 1]
        #公共映射组(去重)
        common_groups = list(set(common_groups_1))
        common_groups.sort(key=common_groups_1.index)

        common_group_data_list = []

        for common_group in common_groups:
            group_data = {}
            group_data["group_name"] = common_group
            data_list = []

            # 无子节点
            orm_list = [orm for orm in behavior_orm_list if orm.group_name == common_group and orm.group_sub_name == '']
            for orm in orm_list:
                data = {}
                data["title"] = orm.key_value
                data["value"] = 0
                for behavior_report in behavior_report_list:
                    if behavior_report["key_name"] == orm.key_name:
                        if orm.value_type == 2:
                            data["value"] = behavior_report["key_value"]
                        else:
                            data["value"] = int(behavior_report["key_value"])
                data_list.append(data)
            if len(data_list) > 0:
                group_data["data_list"] = data_list

            # 有子节点
            orm_list_sub = [orm for orm in behavior_orm_list if orm.group_name == common_group and orm.group_sub_name != '']
            if orm_list_sub:
                groups_sub_name = [orm.group_sub_name for orm in orm_list_sub]
                #公共映射组(去重)
                sub_names = list(set(groups_sub_name))
                sub_names.sort(key=groups_sub_name.index)
                sub_group_data_list = []
                for sub_name in sub_names:
                    sub_group_data = {}
                    sub_group_data["group_name"] = sub_name
                    sub_data_list = []

                    # 无子节点
                    orm_list_1 = [orm for orm in behavior_orm_list if orm.group_sub_name == sub_name]
                    for orm in orm_list_1:
                        data = {}
                        data["title"] = orm.key_value
                        data["value"] = 0
                        for behavior_report in behavior_report_list:
                            if behavior_report["key_name"] == orm.key_name:
                                if orm.value_type == 2:
                                    data["value"] = behavior_report["key_value"]
                                else:
                                    data["value"] = int(behavior_report["key_value"])
                        sub_data_list.append(data)
                    sub_group_data["data_list"] = sub_data_list
                    sub_group_data_list.append(sub_group_data)
                group_data["sub_data_list"] = sub_group_data_list

            common_group_data_list.append(group_data)

        return self.reponse_json_success(common_group_data_list)


class ReportInfoListHandler(SevenBaseHandler):
    """
    :description: 关键数据获取(趋势图)
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 关键数据获取(趋势图)
        :param act_id:活动id
        :param start_date:开始时间
        :param end_date:结束时间
        :return list
        :last_editors: HuangJingCan
        """
        act_id = int(self.get_param("act_id", 0))
        start_date = self.get_param("start_date")
        end_date = self.get_param("end_date")

        act_dict = ActInfoModel(context=self).get_dict_by_id(act_id)
        if not act_dict:
            return self.reponse_json_success([])

        act_type = act_dict['act_type']

        date_list = self.get_date_list(start_date, end_date)

        condition = "act_id=%s"
        params = [act_id]

        if start_date != "":
            condition += " and create_date>=%s"
            params.append(start_date)
        if end_date != "":
            condition += " and create_date<%s"
            params.append(TimeHelper.add_days_by_format_time(end_date, 1))

        behavior_orm_model = BehaviorOrmModel(context=self)
        behavior_report_model = BehaviorReportModel(context=self)

        # behavior_orm_list = behavior_orm_model.get_list("(is_common=1 and act_type=%s) or act_id=%s", order_by="sort_index asc", params=[act_type, act_id])
        behavior_orm_list = behavior_orm_model.get_list("((is_common=1 and act_type=%s) or act_id=%s) and is_release=1", order_by="sort_index asc", params=[act_type, act_id])
        behavior_report_list = behavior_report_model.get_dict_list(condition, field="key_name,key_value,DATE_FORMAT(create_date,'%%Y-%%m-%%d') AS create_date", params=params)

        #公共映射组（未去重）
        common_groups_1 = [orm.group_name for orm in behavior_orm_list if orm.is_common == 1]
        #公共映射组(去重)
        common_groups = list(set(common_groups_1))
        common_groups.sort(key=common_groups_1.index)

        common_group_data_list = []

        for common_group in common_groups:
            group_data = {}
            group_data["group_name"] = common_group
            data_list = []

            # 无子节点
            orm_list = [orm for orm in behavior_orm_list if orm.group_name == common_group and orm.group_sub_name == '']
            for orm in orm_list:
                data = {}
                data["title"] = orm.key_value
                data["value"] = []
                for date_day in date_list:
                    behavior_date_report = {}
                    for behavior_report in behavior_report_list:
                        if behavior_report["key_name"] == orm.key_name and behavior_report["create_date"] == date_day:
                            if orm.value_type != 2:
                                behavior_report["key_value"] = int(behavior_report["key_value"])
                            behavior_date_report = {"title": orm.key_value, "date": date_day, "value": behavior_report["key_value"]}
                            break
                    if not behavior_date_report:
                        behavior_date_report = {"title": orm.key_value, "date": date_day, "value": 0}
                    data["value"].append(behavior_date_report)
                data_list.append(data)
            if len(data_list) > 0:
                group_data["data_list"] = data_list

            # 有子节点
            orm_list_sub = [orm for orm in behavior_orm_list if orm.group_name == common_group and orm.group_sub_name != '']
            if orm_list_sub:
                groups_sub_name = [orm.group_sub_name for orm in orm_list_sub]
                #公共映射组(去重)
                sub_names = list(set(groups_sub_name))
                sub_names.sort(key=groups_sub_name.index)
                sub_group_data_list = []
                for sub_name in sub_names:
                    sub_group_data = {}
                    sub_group_data["group_name"] = sub_name
                    sub_data_list = []

                    # 无子节点
                    orm_list_1 = [orm for orm in behavior_orm_list if orm.group_sub_name == sub_name]
                    for orm in orm_list_1:
                        data = {}
                        data["title"] = orm.key_value
                        data["value"] = []
                        for date_day in date_list:
                            behavior_date_report = {}
                            for behavior_report in behavior_report_list:
                                if behavior_report["key_name"] == orm.key_name and behavior_report["create_date"] == date_day:
                                    if orm.value_type != 2:
                                        behavior_report["key_value"] = int(behavior_report["key_value"])
                                    behavior_date_report = {"title": orm.key_value, "date": date_day, "value": behavior_report["key_value"]}
                                    break
                            if not behavior_date_report:
                                behavior_date_report = {"title": orm.key_value, "date": date_day, "value": 0}
                            data["value"].append(behavior_date_report)
                        sub_data_list.append(data)
                    sub_group_data["data_list"] = sub_data_list
                    sub_group_data_list.append(sub_group_data)
                group_data["sub_data_list"] = sub_group_data_list

            common_group_data_list.append(group_data)

        return self.reponse_json_success(common_group_data_list)