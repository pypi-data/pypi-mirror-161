
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class PrizeOrderModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(PrizeOrderModel, self).__init__(PrizeOrder, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class PrizeOrder:

    def __init__(self):
        super(PrizeOrder, self).__init__()
        self.id = 0  # id
        self.order_no = ""  # 订单号
        self.app_id = ""  # app_id
        self.act_id = 0  # act_id
        self.open_id = ""  # open_id
        self.owner_open_id = ""  # 商家OpenID
        self.user_nick = ""  # 用户昵称
        self.real_name = ""  # 真实姓名
        self.telephone = ""  # 手机号码
        self.province = ""  # 所在省
        self.city = ""  # 所在市
        self.county = ""  # 所在区
        self.street = ""  # 所在街道
        self.adress = ""  # 收货地址
        self.deliver_date = "1900-01-01 00:00:00"  # 发货时间
        self.express_no = ""  # 快递单号
        self.express_company = ""  # 快递公司
        self.order_status = 0  # 状态（0未发货1已发货2不予发货）
        self.remarks = ""  # 备注
        self.sync_status = 0  # 订单同步状态（0-未同步，1-同步成功，2-同步失败）
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 修改时间

    @classmethod
    def get_field_list(self):
        return ['id', 'order_no', 'app_id', 'act_id', 'open_id', 'owner_open_id', 'user_nick', 'real_name', 'telephone', 'province', 'city', 'county', 'street', 'adress', 'deliver_date', 'express_no', 'express_company', 'order_status', 'remarks', 'sync_status', 'create_date', 'modify_date']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "prize_order_tb"
    