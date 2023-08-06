
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class SurplusQueueModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(SurplusQueueModel, self).__init__(SurplusQueue, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class SurplusQueue:

    def __init__(self):
        super(SurplusQueue, self).__init__()
        self.id = 0  # 标识
        self.machine_id = 0  # 机台id
        self.app_id = ""  # app_id
        self.prize_id = 0  # 奖品id
        self.act_id = 0  # act_id
        self.open_id = ""  # open_id
        self.key_id = ""  # 中盒分配唯一标识
        self.withhold_value = 0  # 计数
        self.ProcessType = 0  # 处理方式(1默认2按条件)
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.expire_date = "1900-01-01 00:00:00"  # 过期回收时间

    @classmethod
    def get_field_list(self):
        return ['id', 'machine_id', 'app_id', 'prize_id', 'act_id', 'open_id', 'key_id', 'withhold_value', 'ProcessType', 'create_date', 'expire_date']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "surplus_queue_tb"
    