
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class UserUnbindLogModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(UserUnbindLogModel, self).__init__(UserUnbindLog, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class UserUnbindLog:

    def __init__(self):
        super(UserUnbindLog, self).__init__()
        self.id = 0  # 标识
        self.app_id = ""  # 应用唯一标识
        self.act_id = 0  # 活动标识
        self.open_id = ""  # open_id
        self.reason = ""  # 申请原因
        self.audit_status = 0  # 审核状态(1申请中2同意3拒绝)
        self.audit_remark = ""  # 审核备注
        self.create_date = "1900-01-01 00:00:00"  # 申请时间
        self.audit_date = "1900-01-01 00:00:00"  # 审核时间

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'act_id', 'open_id', 'reason', 'audit_status', 'audit_remark', 'create_date', 'audit_date']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "user_unbind_log_tb"
    