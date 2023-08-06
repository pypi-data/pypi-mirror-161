
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class TaskInfoModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(TaskInfoModel, self).__init__(TaskInfo, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class TaskInfo:

    def __init__(self):
        super(TaskInfo, self).__init__()
        self.id = 0  # 标识
        self.act_id = 0  # 活动标识
        self.app_id = ""  # 应用唯一标识
        self.task_type = 0  # 任务类型（枚举TaskType）
        self.task_config = ""  # 任务配置（json字符串，TaskType里面的注释都有详细例子）
        self.sort_index = 0  # 排序
        self.is_release = 0  # 是否发布
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 更新时间

    @classmethod
    def get_field_list(self):
        return ['id', 'act_id', 'app_id', 'task_type', 'task_config', 'sort_index', 'is_release', 'create_date', 'modify_date']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "task_info_tb"
    