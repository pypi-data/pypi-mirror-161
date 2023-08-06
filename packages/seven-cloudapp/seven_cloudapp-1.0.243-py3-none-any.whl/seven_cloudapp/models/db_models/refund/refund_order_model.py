
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class RefundOrderModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(RefundOrderModel, self).__init__(RefundOrder, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class RefundOrder:

    def __init__(self):
        super(RefundOrder, self).__init__()
        self.id = 0  # id
        self.app_id = ""  # app_id
        self.act_id = 0  # act_id
        self.open_id = ""  # open_id
        self.user_nick = ""  # 买家昵称
        self.refund_id = ""  # 退款单号
        self.main_order_no = ""  # 淘宝主订单号
        self.seller_nick = ""  # 卖家昵称
        self.refund_created = "1900-01-01 00:00:00"  # 退款申请时间
        self.refund_fee = 0  # 退款总金额
        self.refund_num = 0  # 退款数量
        self.pay_order_id = 0  # 支付订单表对应id
        self.lottery_value_log_id = 0  # 积分明细表对应获得id
        self.create_date = "1900-01-01 00:00:00"  # 创建时间

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'act_id', 'open_id', 'user_nick', 'refund_id', 'main_order_no', 'seller_nick', 'refund_created', 'refund_fee', 'refund_num', 'pay_order_id', 'lottery_value_log_id', 'create_date']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "refund_order_tb"
    