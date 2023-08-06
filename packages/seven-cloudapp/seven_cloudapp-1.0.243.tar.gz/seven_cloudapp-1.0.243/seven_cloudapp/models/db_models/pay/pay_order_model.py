
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class PayOrderModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(PayOrderModel, self).__init__(PayOrder, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class PayOrder:

    def __init__(self):
        super(PayOrder, self).__init__()
        self.id = 0  # id
        self.app_id = ""  # app_id
        self.act_id = 0  # act_id
        self.open_id = ""  # open_id
        self.owner_open_id = ""  # 商家OpenID
        self.user_nick = ""  # 用户昵称
        self.real_name = ""  # 真实姓名
        self.main_order_no = ""  # 淘宝主订单号
        self.order_no = ""  # 淘宝订单号
        self.goods_code = ""  # 商品编码
        self.goods_name = ""  # 商品名称
        self.sku_id = ""  # sku_id
        self.sku_name = ""  # sku_name
        self.buy_num = 0  # 购买数量
        self.pay_price = 0  # 购买金额
        self.telephone = ""  # 联系电话
        self.address = ""  # 发货地址
        self.order_status = ""  # 订单状态
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.pay_date = "1900-01-01 00:00:00"  # 支付时间

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'act_id', 'open_id', 'owner_open_id', 'user_nick', 'real_name', 'main_order_no', 'order_no', 'goods_code', 'goods_name', 'sku_id', 'sku_name', 'buy_num', 'pay_price', 'telephone', 'address', 'order_status', 'create_date', 'pay_date']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "pay_order_tb"
    