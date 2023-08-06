
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class RoleUserModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(RoleUserModel, self).__init__(RoleUser, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class RoleUser:

    def __init__(self):
        super(RoleUser, self).__init__()
        self.id = 0  # id
        self.app_id = ""  # app_id
        self.role_id = 0  # 角色标识
        self.is_power = 0  # 是否授权
        self.service_date_start = "1900-01-01 00:00:00"  # 服务开始时间
        self.service_date_end = "1900-01-01 00:00:00"  # 服务结束时间
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 修改时间

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'role_id', 'is_power', 'service_date_start', 'service_date_end', 'create_date', 'modify_date']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "role_user_tb"
    