
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class RecommendGoodsModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(RecommendGoodsModel, self).__init__(RecommendGoods, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class RecommendGoods:

    def __init__(self):
        super(RecommendGoods, self).__init__()
        self.id = 0  # 标识
        self.act_id = 0  # 活动标识
        self.app_id = ""  # 应用唯一标识
        self.is_release = 0  # 是否发布
        self.goods_ids = ""  # 推荐商品id(逗号,分隔)
        self.goods_list = ""  # 推荐商品列表
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 更新时间

    @classmethod
    def get_field_list(self):
        return ['id', 'act_id', 'app_id', 'is_release', 'goods_ids', 'goods_list', 'create_date', 'modify_date']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "recommend_goods_tb"
    