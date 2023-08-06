#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class LotteryValueLogModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(LotteryValueLogModel, self).__init__(LotteryValueLog, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class LotteryValueLog:

    def __init__(self):
        super(LotteryValueLog, self).__init__()
        self.id = 0  # id
        self.app_id = ""  # app_id
        self.act_id = 0  # act_id
        self.open_id = ""  # open_id
        self.user_nick = ""  # 用户昵称
        self.log_title = ""  # 标题
        self.log_desc = ""  # 备注
        self.log_info = ""  # 信息
        self.currency_type = 0  # 抽奖货币类型（0无1次数2积分3价格档位4会员积分）
        self.source_type = 0  # 来源类型：1-购买2-任务3-手动配置4抽奖
        self.change_type = 0  # 变动类型(来源类型+对用的子类型  如:101下单购买201新人有礼202每日签到301手动增加302手动减少401抽奖增加402抽奖减少)
        self.operate_type = 0  # 操作类型(0累计 1消耗)
        self.current_value = 0  # 改动的值
        self.history_value = 0  # 未变化前用户值
        self.main_pay_order_no = ""  # 淘宝主订单号
        self.operator = ""  # 操作人
        self.create_date = "1900-01-01 00:00:00"  # 创建时间

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'act_id', 'open_id', 'user_nick', 'log_title', 'log_desc', 'log_info', 'currency_type', 'source_type', 'change_type', 'operate_type', 'current_value', 'history_value', 'main_pay_order_no', 'operator', 'create_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "lottery_value_log_tb"
