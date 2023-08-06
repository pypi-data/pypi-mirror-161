
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class MaterialInfoModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(MaterialInfoModel, self).__init__(MaterialInfo, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class MaterialInfo:

    def __init__(self):
        super(MaterialInfo, self).__init__()
        self.id = 0  # id
        self.position_id = 0  # 素材位置（1店铺首页装修图2商品详情页装修海报3直播间活动浮窗半图卡片4直播间互动浮窗全图卡片）
        self.title = ""  # 素材名称
        self.icon = ""  # 素材图
        self.link = ""  # 链接地址
        self.sort_index = 0  # 排序
        self.is_release = 0  # 是否发布（1是0否）
        self.release_date = "1900-01-01 00:00:00"  # 发布时间
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 更新时间

    @classmethod
    def get_field_list(self):
        return ['id', 'position_id', 'title', 'icon', 'link', 'sort_index', 'is_release', 'release_date', 'create_date', 'modify_date']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "material_info_tb"
    