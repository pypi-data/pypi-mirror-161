
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class GearLogModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(GearLogModel, self).__init__(GearLog, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class GearLog:

    def __init__(self):
        super(GearLog, self).__init__()
        self.id = 0  # id
        self.app_id = ""  # app_id
        self.act_id = 0  # act_id
        self.open_id = ""  # open_id
        self.sku_id = ""  # sku_id
        self.price_gears_id = 0  # 价格档位id
        self.source_type = 0  # 来源类型：1-购买2-任务3-手动配置
        self.type_value = 0  # 操作类型 0累计 1消耗
        self.current_value = 0  # 修改次数
        self.history_value = 0  # 历史剩余次数
        self.create_date = "1900-01-01 00:00:00"  # 创建时间

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'act_id', 'open_id', 'sku_id', 'price_gears_id', 'source_type', 'type_value', 'current_value', 'history_value', 'create_date']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "gear_log_tb"
    