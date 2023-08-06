
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class ThemeInfoModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(ThemeInfoModel, self).__init__(ThemeInfo, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class ThemeInfo:

    def __init__(self):
        super(ThemeInfo, self).__init__()
        self.id = 0  # id
        self.app_id = ""  # 应用唯一标识
        self.is_private = 0  # 是否发布（1私有0公用）
        self.theme_name = ""  # 主题名称
        self.client_json = ""  # 客户端内容json
        self.server_json = ""  # 服务端内容json
        self.out_id = ""  # 外部id
        self.sort_index = 0  # 排序号
        self.is_release = 0  # 是否发布（1发布0未发布）
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 修改时间

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'is_private', 'theme_name', 'client_json', 'server_json', 'out_id', 'sort_index', 'is_release', 'create_date', 'modify_date']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "theme_info_tb"
    