# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-05-19 09:40:27
:LastEditTime: 2020-08-12 10:06:14
:LastEditors: HuangJingCan
:description: 淘宝系统参数
"""


class TaoBaoParam():
    """
    :description: 淘宝参数实体
    :last_editors: HuangJingCan
    """
    def __init__(self):
        # 商家应用的appKey
        self.app_key = ""
        # 当前登录用户的昵称(需要用户授权)
        self.user_nick = ""
        # 当前登录用户的openId
        self.open_id = ""
        # 当前云应用调用环境，入参为：test或者online，对应在云开发中绑定的云容器的测试环境和正式环境。在发布上线的前注意调整env为online，调用正式环境。
        self.env = ""
        # 运行时使用的小程序ID，
        # 1,如果是BC模式，那么这里是B端小程序ID;
        # 2,如果是模板开发模式，这里是模板小程序ID;
        # 3,如果是插件开发模式，这里是宿主小程序的小程序ID;
        self.mini_app_id = ""
        # 当前登录用户的授权token，也是sessionkey（需要用户授权）
        self.access_token = ""
        # 使用当前小程序appkey和secret进行对参数进行加签后的签名
        self.sign = ""
        # 当前登录用户的混淆nick
        self.mix_nick = ""
        # 当前登录用户的userId，仅对老应用迁移生效
        self.user_id = ""
        # 主账号userId，千牛子账号登录授权后可与获取，仅对老应用迁移生效
        self.main_user_id = ""
        # 当前调用小程序的小程序ID
        # 1,如果是BC模式，那么这里是C端小程序ID;
        # 2,如果是模板开发模式，这里是实例化小程序ID;
        # 3,如果是插件开发模式，这里是插件的小程序ID;
        self.source_app_id = ""
        # request_id
        self.request_id = ""