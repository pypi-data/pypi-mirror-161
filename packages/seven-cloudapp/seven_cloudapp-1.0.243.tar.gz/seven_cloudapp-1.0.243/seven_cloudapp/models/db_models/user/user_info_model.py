
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class UserInfoModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(UserInfoModel, self).__init__(UserInfo, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class UserInfo:

    def __init__(self):
        super(UserInfo, self).__init__()
        self.id = 0  # id
        self.app_id = ""  # app_id
        self.act_id = 0  # act_id
        self.open_id = ""  # open_id
        self.user_nick = ""  # 昵称
        self.avatar = ""  # 头像
        self.is_auth = 0  # 是否授权（1是0否）
        self.is_new = 0  # 是否新用户
        self.owner_open_id = ""  # 应用拥有者唯一标识
        self.store_pay_price = 0  # 淘宝累计支付金额
        self.pay_price = 0  # 累计支付金额
        self.pay_num = 0  # 累计支付笔数
        self.login_token = ""  # 登录令牌
        self.signin = ""  # 签到信息
        self.lottery_value = 0  # 抽奖次数
        self.surplus_integral = 0  # 剩余积分
        self.user_state = 0  # 用户状态（0-正常，1-黑名单）
        self.is_member = 0  # 是否会员
        self.is_member_before = 0  # 用户最初会员状态（0未入会1已入会）
        self.is_favor = 0  # 是否关注店铺
        self.is_favor_before = 0  # 用户最初关注状态（0未关注1已关注）
        self.lottery_sum = 0  # 抽奖累计次数
        self.relieve_date = "1900-01-01 00:00:00"  # 解禁时间
        self.store_pay_price_date = "1900-01-01 00:00:00"  # 淘宝累计金额开始时间
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 修改时间

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'act_id', 'open_id', 'user_nick', 'avatar', 'is_auth', 'is_new', 'owner_open_id', 'store_pay_price', 'pay_price', 'pay_num', 'login_token', 'signin', 'lottery_value', 'surplus_integral', 'user_state', 'is_member', 'is_member_before', 'is_favor', 'is_favor_before', 'lottery_sum', 'relieve_date', 'store_pay_price_date', 'create_date', 'modify_date']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "user_info_tb"
    