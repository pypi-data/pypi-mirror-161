# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-06-02 14:32:40
:LastEditTime: 2021-03-10 18:23:27
:LastEditors: HuangJingCan
:description: 枚举类
"""

from enum import Enum, unique


class TagType(Enum):
    """
    :description: 标签类型
    """
    无 = 0
    限定 = 1
    稀有 = 2
    绝版 = 3
    隐藏 = 4


class SourceType(Enum):
    """
    :description: 用户次数配置来源类型
    """
    购买 = 1
    任务 = 2
    手动配置 = 3


class OperationType(Enum):
    """
    :description: 用户操作日志类型
    """
    add = 1
    update = 2
    delete = 3


class TaskType(Enum):
    """
    docstring：任务类型
    """
    # 新人有礼，格式：{"reward_value":0}
    free = 1
    # 每日签到，格式：{"reward_value":0}
    sign = 2
    # 邀请新用户，格式：{"reward_value":0,"user_limit":0}
    invite = 3
    # 关注店铺，格式：{"reward_value":0}
    favor = 4
    # 加入店铺会员，格式：{"reward_value":0}
    member = 5
    # 下单购买指定商品，格式：{"reward_value":0,"num_limit":0,"effective_date_start":'1900-01-01 00:00:00',"effective_date_end":'1900-01-01 00:00:00',"goods_ids":"","goods_list":[]}
    buy = 6
    # 收藏商品，格式：{"reward_value":0,"num_limit":0,"goods_ids":"","goods_list":[]}
    collect = 7
    # 浏览商品，格式：{"reward_value":0,"num_limit":0,"goods_ids":"","goods_list":[]}
    browse = 8
    # 加入群聊，格式：{"reward_value":0,"join_type":（1商家群链接2选择单群聊）,"join_url":"","chatting_id":"","chatting_name":""}
    join_chatting = 9
    # 分享群聊，格式：{"reward_value":0,"chatting_id":"","chatting_name":""}
    share_chatting = 10
    # 直播，格式：云应用未开放此功能
    live_telecast = 11
    # 每周签到，格式：{"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0}
    weekly_sign = 12
    # 下单任意消费，格式：{"reward_value":0,"effective_date_start":'1900-01-01 00:00:00',"effective_date_end":'1900-01-01 00:00:00'}
    arbitrarily_consumption = 13
    # 累计消费，格式：{"effective_date_start":'1900-01-01 00:00:00',"effective_date_end":'1900-01-01 00:00:00',"reward_list":[{"key":"前端算唯一值","money":500,"reward_value":0}]}
    totle_consumption = 14
    # 单笔订单消费，格式：{"effective_date_start":'1900-01-01 00:00:00',"effective_date_end":'1900-01-01 00:00:00',"reward_list":[{"key":"前端算唯一值","money":500,"reward_value":0}]}
    one_consumption = 15
    # 店长好礼，格式：从活动奖品表配置
    shopowner_gift = 16
    # 抽奖送积分
    lottery_points = 17
