
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class IpSeriesModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(IpSeriesModel, self).__init__(IpSeries, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class IpSeries:

    def __init__(self):
        super(IpSeries, self).__init__()
        self.id = 0  # id
        self.app_id = ""  # app_id
        self.act_id = 0  # 活动ID
        self.series_name = ""  # 系列名称
        self.series_pic = ""  # 系列图
        self.show_pic = ""  # 展示图片
        self.sort_index = 0  # 排序
        self.is_release = 0  # 是否发布
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 修改时间

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'act_id', 'series_name', 'series_pic', 'show_pic', 'sort_index', 'is_release', 'create_date', 'modify_date']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "ip_series_tb"
    