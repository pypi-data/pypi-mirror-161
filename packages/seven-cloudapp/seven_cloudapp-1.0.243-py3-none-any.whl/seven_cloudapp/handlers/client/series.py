# -*- coding: utf-8 -*-
"""
:Author: HuangJianYi
:Date: 2020-06-22 17:27:07
:LastEditTime: 2021-04-16 11:07:01
:LastEditors: HuangJingCan
:description: 
"""
from seven_cloudapp.handlers.seven_base import *

from seven_cloudapp.models.seven_model import PageInfo
from seven_cloudapp.models.db_models.ip.ip_series_model import *


class SeriesListHandler(SevenBaseHandler):
    """
    :description: IP系列列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 获取IP系列列表
        :param act_id:活动id
        :param page_index:页索引
        :param page_size:页大小
        :return: PageInfo
        :last_editors: HuangJianYi
        """
        act_id = int(self.get_param("act_id", 0))
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 20))

        if act_id <= 0:
            return self.reponse_json_error_params()

        condition = "act_id=%s AND is_release=1"
        params = [act_id]
        order_by = "sort_index desc"

        page_list, total = IpSeriesModel(context=self).get_dict_page_list("*", page_index, page_size, condition, "", order_by, params)

        page_info = PageInfo(page_index, page_size, total, page_list)

        return self.reponse_json_success(page_info)