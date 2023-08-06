# -*- coding: utf-8 -*-
"""
:Author: HuangJianYi
:Date: 2020-06-22 10:30:00
:LastEditTime: 2021-04-22 17:36:28
:LastEditors: HuangJingCan
:description: ip系列
"""
from seven_cloudapp.handlers.seven_base import *

from seven_cloudapp.models.seven_model import PageInfo
from seven_cloudapp.models.enum import *
from seven_cloudapp.models.db_models.ip.ip_series_model import *


class SeriesHandler(SevenBaseHandler):
    """
    :description: 保存IP系列
    """
    @filter_check_params("app_id,act_id,series_name,series_pic")
    def get_async(self):
        """
        :description: 保存IP系列
        :param series_id 系列id
        :return: reponse_json_success
        :last_editors: HuangJianYi
        """
        # app_id = "3000000003444475"
        # ip_series = IpSeries()
        # ip_series.act_id=1
        # ip_series.app_id=2
        # ip_series.series_name = "海贼王"
        # self.create_operation_log(OperationType.add.value, ip_series.__str__(), "SeriesHandler", None, self.json_dumps(ip_series.__dict__))
        app_id = self.get_param("app_id")
        open_id = self.get_taobao_param().open_id
        series_id = int(self.get_param("series_id", 0))
        act_id = int(self.get_param("act_id", 0))
        series_name = self.get_param("series_name")
        series_pic = self.get_param("series_pic")
        show_pic = self.get_param("show_pic")
        sort_index = int(self.get_param("sort_index", 0))
        is_release = int(self.get_param("is_release", 1))

        if act_id <= 0:
            return self.reponse_json_error_params()

        ip_series = None
        ip_series_model = IpSeriesModel(context=self)
        if series_id > 0:
            ip_series = ip_series_model.get_entity_by_id(series_id)

        is_add = False
        if not ip_series:
            is_add = True
            ip_series = IpSeries()

        old_ip_series = ip_series
        ip_series.act_id = act_id
        ip_series.app_id = app_id
        ip_series.series_name = series_name
        ip_series.series_pic = series_pic
        ip_series.show_pic = show_pic
        ip_series.sort_index = sort_index
        ip_series.is_release = is_release
        ip_series.modify_date = self.get_now_datetime()

        if is_add:
            ip_series.create_date = ip_series.modify_date
            ip_series.id = ip_series_model.add_entity(ip_series)
            # 记录日志
            self.create_operation_log(OperationType.add.value, ip_series.__str__(), "SeriesHandler", None, self.json_dumps(ip_series))
        else:
            ip_series_model.update_entity(ip_series)
            # 记录日志
            self.create_operation_log(OperationType.update.value, ip_series.__str__(), "SeriesHandler", self.json_dumps(old_ip_series), self.json_dumps(ip_series))

        self.reponse_json_success(ip_series.id)


class SeriesListHandler(SevenBaseHandler):
    """
    :description: IP系列信息
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 获取IP系列列表
        :param act_id：活动id
        :param page_index：页索引
        :param page_size：页大小
        :return: list
        :last_editors: HuangJianYi
        """
        act_id = int(self.get_param("act_id", 0))
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 10))

        if act_id <= 0:
            return self.reponse_json_error_params()

        condition = "act_id=%s"
        params = [act_id]
        order_by = "sort_index desc"

        page_list, total = IpSeriesModel(context=self).get_dict_page_list("*", page_index, page_size, condition, "", order_by, params)

        page_info = PageInfo(page_index, page_size, total, page_list)

        self.reponse_json_success(page_info)


class SeriesDelHandler(SevenBaseHandler):
    """
    :description: 删除系列
    """
    @filter_check_params("series_id")
    def get_async(self):
        """
        :description: 删除系列
        :param series_id：系列id
        :return: reponse_json_success
        :last_editors: HuangJianYi
        """
        open_id = self.get_taobao_param().open_id
        series_id = int(self.get_param("series_id", 0))

        if series_id <= 0:
            return self.reponse_json_error_params()

        IpSeriesModel(context=self).del_entity("id=%s", series_id)

        self.create_operation_log(OperationType.delete.value, "ip_series_tb", "SeriesDelHandler", None, series_id)

        self.reponse_json_success()


class SeriesReleaseHandler(SevenBaseHandler):
    """
    :description: 系列上下架
    """
    @filter_check_params("series_id,is_release")
    def get_async(self):
        """
        :description: 系列上下架
        :param series_id：系列id
        :param is_release：是否发布（0下架1上架）
        :return: reponse_json_success
        :last_editors: HuangJianYi
        """
        series_id = int(self.get_param("series_id", 0))
        is_release = int(self.get_param("is_release", 0))

        if series_id <= 0:
            return self.reponse_json_error_params()

        IpSeriesModel(context=self).update_table("is_release=%s", "id=%s", [is_release, series_id])

        self.reponse_json_success()