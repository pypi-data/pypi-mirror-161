
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class PropLogModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(PropLogModel, self).__init__(PropLog, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class PropLog:

    def __init__(self):
        super(PropLog, self).__init__()
        self.id = 0  # id
        self.app_id = ""  # app_id
        self.act_id = 0  # act_id
        self.open_id = ""  # open_id
        self.user_nick = ""  # 用户昵称
        self.change_type = 0  # 变动类型(1手动配置2兑换3使用)
        self.operate_type = 0  # 操作类型(0累计 1消耗)
        self.prop_type = 0  # 道具类型(2透视卡3提示卡4重抽卡)
        self.machine_name = ""  # 机台名称
        self.specs_type = 0  # 中盒规格(5.6,7.8.9.10.12)
        self.operate_value = 0  # 变动值
        self.history_value = 0  # 历史值
        self.title = ""  # 标题
        self.remark = ""  # 备注
        self.create_date_int = 0  # 创建天
        self.create_date = "1900-01-01 00:00:00"  # 创建时间

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'act_id', 'open_id', 'user_nick', 'change_type', 'operate_type', 'prop_type', 'machine_name', 'specs_type', 'operate_value', 'history_value', 'title', 'remark', 'create_date_int', 'create_date']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "prop_log_tb"
    