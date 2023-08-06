
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class CoinOrderModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(CoinOrderModel, self).__init__(CoinOrder, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class CoinOrder:

    def __init__(self):
        super(CoinOrder, self).__init__()
        self.id = 0  # id
        self.open_id = ""  # open_id
        self.app_id = ""  # app_id
        self.act_id = 0  # act_id
        self.machine_id = 0  # 机台id
        self.reward_type = 0  # 奖励类型
        self.goods_name = ""  # 商品名称
        self.goods_price = 0  # 商品价格
        self.sku = ""  # 商品sku
        self.price_gears_id = 0  # 价格档位ID
        self.nick_name = ""  # 淘宝昵称
        self.main_pay_order_no = ""  # 淘宝主订单编号
        self.pay_order_no = ""  # 淘宝子订单编号
        self.pay_order_id = 0  # 交易订单ID
        self.surplus_count = 0  # 剩余配对数
        self.buy_count = 0  # 购买数量
        self.prize_ids = ""  # 奖品ID列表（逗号隔开）
        self.remark = ""  # 备注
        self.pay_date = "1900-01-01 00:00:00"  # 支付时间
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 修改时间

    @classmethod
    def get_field_list(self):
        return ['id', 'open_id', 'app_id', 'act_id', 'machine_id', 'reward_type', 'goods_name', 'goods_price', 'sku', 'price_gears_id', 'nick_name', 'main_pay_order_no', 'pay_order_no', 'pay_order_id', 'surplus_count', 'buy_count', 'prize_ids', 'remark', 'pay_date', 'create_date', 'modify_date']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "coin_order_tb"
    