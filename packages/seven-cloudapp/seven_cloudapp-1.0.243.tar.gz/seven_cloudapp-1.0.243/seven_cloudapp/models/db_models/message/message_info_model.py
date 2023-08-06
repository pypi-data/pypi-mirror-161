
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class MessageInfoModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(MessageInfoModel, self).__init__(MessageInfo, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class MessageInfo:

    def __init__(self):
        super(MessageInfo, self).__init__()
        self.id = 0  # 
        self.title = ""  # 消息标题
        self.news_type = 0  # 消息类型（1公告2消息3活动）
        self.content = ""  # 内容
        self.is_popup_window = 0  # 是否弹窗（1是0否）
        self.popup_window_position = ""  # 弹窗位置 
        self.popup_window_frequency = 0  # 弹窗频率
        self.popup_window_date_start = "1900-01-01 00:00:00"  # 弹窗推送开始时间
        self.popup_window_date_end = "1900-01-01 00:00:00"  # 弹窗推送结束时间
        self.sort_index = 0  # 排序
        self.is_release = 0  # 是否发布（1是0否）
        self.release_date_start = "1900-01-01 00:00:00"  # 开始上架时间
        self.release_date_end = "1900-01-01 00:00:00"  # 结束上架时间
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 更新时间

    @classmethod
    def get_field_list(self):
        return ['id', 'title', 'news_type', 'content', 'is_popup_window', 'popup_window_position', 'popup_window_frequency', 'popup_window_date_start', 'popup_window_date_end', 'sort_index', 'is_release', 'release_date_start', 'release_date_end', 'create_date', 'modify_date']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "message_info_tb"
    