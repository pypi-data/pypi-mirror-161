
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class LoginLogModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(LoginLogModel, self).__init__(LoginLog, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class LoginLog:

    def __init__(self):
        super(LoginLog, self).__init__()
        self.id = 0  # id
        self.open_id = ""  # 用户唯一标识
        self.user_nick = ""  # 用户昵称
        self.store_user_nick = ""  # 店铺主帐号名称（会员名）
        self.is_master = 0  # 是否主账号（1是0否）
        self.request_params = ""  # 参数
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 修改时间

    @classmethod
    def get_field_list(self):
        return ['id', 'open_id', 'user_nick', 'store_user_nick', 'is_master', 'request_params', 'create_date', 'modify_date']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "login_log_tb"
    