# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-10-20 16:34:38
@LastEditTime: 2022-02-16 19:09:19
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class EndboxOrderModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(EndboxOrderModel, self).__init__(EndboxOrder, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class EndboxOrder:

    def __init__(self):
        super(EndboxOrder, self).__init__()
        self.id = 0  # id
        self.order_no = ""  # 订单号
        self.app_id = ""  # app_id
        self.act_id = 0  # act_id
        self.open_id = ""  # open_id
        self.user_nick = ""  # 用户昵称
        self.series_id = 0  # IP系列id
        self.machine_id = 0  # 机台id
        self.machine_type = 0  # 机台类型：1消耗积分2消耗次数3会员积分
        self.machine_name = ""  # 机台名称
        self.specs_type = 0  # 端盒规格
        self.endbox_price = 0  # 端盒价格
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 修改时间

    @classmethod
    def get_field_list(self):
        return ['id', 'order_no', 'app_id', 'act_id', 'open_id', 'user_nick', 'series_id', 'machine_id', 'machine_type', 'machine_name', 'specs_type', 'endbox_price', 'create_date', 'modify_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "endbox_order_tb"
