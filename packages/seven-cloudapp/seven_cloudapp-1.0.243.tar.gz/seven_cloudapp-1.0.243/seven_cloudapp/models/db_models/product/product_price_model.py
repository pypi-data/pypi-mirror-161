
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class ProductPriceModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(ProductPriceModel, self).__init__(ProductPrice, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class ProductPrice:

    def __init__(self):
        super(ProductPrice, self).__init__()
        self.id = 0  # id
        self.plan_name = ""  # 计划名称
        self.begin_time = "1900-01-01 00:00:00"  # 开始时间
        self.end_time = "1900-01-01 00:00:00"  # 结束时间
        self.content = ""  # 内容
        self.is_release = 0  # 是否发布（1是0否）
        self.release_date = "1900-01-01 00:00:00"  # 发布时间
        self.create_time = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 更新时间

    @classmethod
    def get_field_list(self):
        return ['id', 'plan_name', 'begin_time', 'end_time', 'content', 'is_release', 'release_date', 'create_time', 'modify_date']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "product_price_tb"
    