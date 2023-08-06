
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class RolePowerModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(RolePowerModel, self).__init__(RolePower, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class RolePower:

    def __init__(self):
        super(RolePower, self).__init__()
        self.id = 0  # id
        self.role_id = 0  # 角色标识
        self.menu_id = 0  # 菜单标识

    @classmethod
    def get_field_list(self):
        return ['id', 'role_id', 'menu_id']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "role_power_tb"
    