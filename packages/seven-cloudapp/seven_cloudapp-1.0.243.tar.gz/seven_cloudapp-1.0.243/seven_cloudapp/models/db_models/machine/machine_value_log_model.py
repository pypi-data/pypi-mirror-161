
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class MachineValueLogModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(MachineValueLogModel, self).__init__(MachineValueLog, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class MachineValueLog:

    def __init__(self):
        super(MachineValueLog, self).__init__()
        self.id = 0  # id
        self.app_id = ""  # app_id
        self.act_id = 0  # act_id
        self.open_id = ""  # open_id
        self.machine_id = 0  # 机台id
        self.source_type = 0  # 来源类型：1-购买2-任务3-手动配置
        self.increase_value = 0  # 改动的值
        self.old_surplus_value = 0  # 未变化前用户值
        self.create_date = "1900-01-01 00:00:00"  # 创建时间

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'act_id', 'open_id', 'machine_id', 'source_type', 'increase_value', 'old_surplus_value', 'create_date']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "machine_value_log_tb"
    