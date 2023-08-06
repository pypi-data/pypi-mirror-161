
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class RoleMenuModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(RoleMenuModel, self).__init__(RoleMenu, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class RoleMenu:

    def __init__(self):
        super(RoleMenu, self).__init__()
        self.id = 0  # id
        self.menu_name = ""  # 菜单名称
        self.sort_index = 0  # 排序
        self.Is_show = 0  # 是否显示0不显示1显示
        self.create_date = "1900-01-01 00:00:00"  # 创建时间

    @classmethod
    def get_field_list(self):
        return ['id', 'menu_name', 'sort_index', 'Is_show', 'create_date']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "role_menu_tb"
    