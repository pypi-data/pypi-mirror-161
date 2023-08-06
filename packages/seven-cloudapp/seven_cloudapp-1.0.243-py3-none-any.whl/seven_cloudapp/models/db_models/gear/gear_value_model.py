
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class GearValueModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(GearValueModel, self).__init__(GearValue, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class GearValue:

    def __init__(self):
        super(GearValue, self).__init__()
        self.id = 0  # id
        self.app_id = ""  # app_id
        self.open_id = ""  # open_id
        self.act_id = 0  # act_id
        self.price_gears_id = 0  # 价格档位id
        self.sku_id = ""  # sku_id
        self.current_value = 0  # 当前次数
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 修改时间

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'open_id', 'act_id', 'price_gears_id', 'sku_id', 'current_value', 'create_date', 'modify_date']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "gear_value_tb"
    