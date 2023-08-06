
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class ThrowGoodsModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(ThrowGoodsModel, self).__init__(ThrowGoods, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class ThrowGoods:

    def __init__(self):
        super(ThrowGoods, self).__init__()
        self.id = 0  # ID
        self.app_id = ""  # app_id
        self.act_id = 0  # 活动ID
        self.goods_id = 0  # 商品ID
        self.prize_id = 0  # 奖品ID
        self.is_throw = 0  # 是否投放(0：不投放  1：投放)
        self.is_sync = 0  # 是否同步（0不同步  1：同步）
        self.error_message = ""  # 同步失败原因
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.throw_date = "1900-01-01 00:00:00"  # 投放时间
        self.sync_date = "1900-01-01 00:00:00"  # 同步时间

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'act_id', 'goods_id', 'prize_id', 'is_throw', 'is_sync', 'error_message', 'create_date', 'throw_date', 'sync_date']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "throw_goods_tb"
    