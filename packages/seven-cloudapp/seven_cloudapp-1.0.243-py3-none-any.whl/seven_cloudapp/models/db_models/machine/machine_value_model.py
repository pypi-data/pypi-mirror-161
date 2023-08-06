
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class MachineValueModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(MachineValueModel, self).__init__(MachineValue, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class MachineValue:

    def __init__(self):
        super(MachineValue, self).__init__()
        self.id = 0  # id
        self.act_id = 0  # act_id
        self.app_id = ""  # app_id
        self.open_id = ""  # open_id
        self.machine_id = 0  # 机台id
        self.open_value = 0  # 打开次数
        self.surplus_value = 0  # 剩余次数
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 修改时间

    @classmethod
    def get_field_list(self):
        return ['id', 'act_id', 'app_id', 'open_id', 'machine_id', 'open_value', 'surplus_value', 'create_date', 'modify_date']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "machine_value_tb"
    