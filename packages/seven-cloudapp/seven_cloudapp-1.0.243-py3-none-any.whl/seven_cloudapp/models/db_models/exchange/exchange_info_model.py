
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class ExchangeInfoModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(ExchangeInfoModel, self).__init__(ExchangeInfo, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class ExchangeInfo:

    def __init__(self):
        super(ExchangeInfo, self).__init__()
        self.id = 0  # 标识
        self.app_id = ""  # app_id
        self.act_id = 0  # act_id
        self.goods_type = 0  # 商品类型(1实物2透视卡3提示卡4重抽卡5优惠券)
        self.need_value = 0  # 所需T币数量
        self.goods_img = ""  # 商品图片
        self.goods_name = ""  # 商品名称
        self.goods_price = 0  # 商品价值
        self.goods_code = ""  # 商品编码
        self.day_limit = 0  # 每日上限
        self.stock_num = 0  # 库存数量
        self.draw_num = 0  # 领取数量
        self.sort_index = 0  # 排序
        self.is_release = 0  # 是否发布：0否1是
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 更新时间

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'act_id', 'goods_type', 'need_value', 'goods_img', 'goods_name', 'goods_price', 'goods_code', 'day_limit', 'stock_num', 'draw_num', 'sort_index', 'is_release', 'create_date', 'modify_date']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "exchange_info_tb"
    