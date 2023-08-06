
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class TaskCountModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(TaskCountModel, self).__init__(TaskCount, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class TaskCount:

    def __init__(self):
        super(TaskCount, self).__init__()
        self.id = 0  # 标识
        self.app_id = ""  # 应用唯一标识
        self.act_id = 0  # 活动标识
        self.open_id = ""  # open_id
        self.task_type = 0  # 任务类型（枚举TaskType）
        self.task_sub_type = ""  # 任务子类型(用于指定任务里的再细分)
        self.count_value = 0  # 计数值
        self.last_date = "1900-01-01 00:00:00"  # 最后修改时间
        self.last_day = 0  # 修改天(yyyyDD)

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'act_id', 'open_id', 'task_type', 'task_sub_type', 'count_value', 'last_date', 'last_day']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "task_count_tb"
    