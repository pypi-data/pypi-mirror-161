
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class BehaviorOrmModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(BehaviorOrmModel, self).__init__(BehaviorOrm, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class BehaviorOrm:

    def __init__(self):
        super(BehaviorOrm, self).__init__()
        self.id = 0  # id
        self.app_id = ""  # app_id
        self.act_id = 0  # 活动ID
        self.act_type = 0  # 活动类型id
        self.orm_type = 0  # 类型（1活动2基础）
        self.task_type = 0  # 任务类型
        self.group_name = ""  # 分组名称
        self.group_sub_name = ""  # 分组子名称
        self.key_name = ""  # key名称
        self.key_value = ""  # key值
        self.value_type = 0  # 输出类型：1-int，2-decimal
        self.is_repeat = 0  # 是否去重(1是0否)
        self.repeat_type = 0  # 去重方式(1当日去重2全部去重)
        self.is_common = 0  # 是否公用（1公用0私有）
        self.owner_open_id = ""  # 应用拥有者标识
        self.sort_index = 0  # 排序号
        self.is_release = 0  # 是否发布
        self.create_date = "1900-01-01 00:00:00"  # 创建时间

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'act_id', 'act_type', 'orm_type', 'task_type', 'group_name', 'group_sub_name', 'key_name', 'key_value', 'value_type', 'is_repeat', 'repeat_type', 'is_common', 'owner_open_id', 'sort_index', 'is_release', 'create_date']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "behavior_orm_tb"
    