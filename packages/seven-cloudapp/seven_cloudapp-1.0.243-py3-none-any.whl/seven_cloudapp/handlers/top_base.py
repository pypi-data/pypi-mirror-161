# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-08-12 09:06:24
@LastEditTime: 2022-07-29 17:31:27
@LastEditors: HuangJianYi
:description: 淘宝top接口基础类
"""
from seven_cloudapp.handlers.seven_base import *

from seven_top import top

from seven_cloudapp.models.enum import OperationType
from seven_cloudapp.models.seven_model import *
from seven_cloudapp.models.db_models.base.base_info_model import *
from seven_cloudapp.models.db_models.app.app_info_model import *
from seven_cloudapp.models.db_models.act.act_prize_model import *


class TopBaseHandler(SevenBaseHandler):
    """
    :description: 淘宝top接口基础类
    """
    def get_sku_info(self, num_iids, access_token):
        """
        :description: 获取sku信息
        :param num_iids：num_iids
        :param access_token：access_token
        :return 
        :last_editors: HuangJingCan
        """
        try:
            resp = self.get_goods_list_for_goodsids(num_iids, access_token)
            # self.logging_link_info(str(resp) + "【access_token】：" + self.get_taobao_param().access_token)
            if "items_seller_list_get_response" in resp.keys():
                if "items" in resp["items_seller_list_get_response"].keys():
                    return self.reponse_json_success(resp["items_seller_list_get_response"])
                else:
                    act_prize = ActPrizeModel(context=self).get_dict("goods_id=%s and sku_detail<>'' and is_sku=1 ", params=int(num_iids))
                    if act_prize:
                        # sku_detail = json.loads(prize.sku_detail.replace('\'', '\"'))
                        sku_detail = self.json_loads(act_prize['sku_detail'])
                        return self.reponse_json_success(sku_detail["items_seller_list_get_response"])
                    return self.reponse_json_error("NoSku", "对不起，找不到该商品的sku")
            else:
                return self.reponse_json_success(resp)
        except Exception as ex:
            self.logging_link_error(traceback.format_exc())
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        return self.reponse_json_error("NoPower", content[len("submsg="):])
                    if "submsg=" in content:
                        return self.reponse_json_error("Error", content[len("submsg="):])

    def get_sku_name(self, num_iids, sku_id, access_token):
        """
        :description: 获取sku名称
        :param num_iids：num_iids
        :param sku_id：sku_id
        :param access_token：access_token
        :return 
        :last_editors: HuangJingCan
        """
        try:
            app_key, app_secret = self.get_app_key_secret()
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.ItemsSellerListGetRequest()

            req.fields = "num_iid,title,nick,input_str,property_alias,sku,props_name,pic_url"
            req.num_iids = num_iids

            resp = req.getResponse(access_token)

            # self.logging_link_info(str(resp) + "【access_token】：" + self.get_taobao_param().access_token)
            if "items_seller_list_get_response" in resp.keys():
                if "items" in resp["items_seller_list_get_response"].keys():
                    props_names = resp["items_seller_list_get_response"]["items"]["item"][0]["props_name"].split(';')
                    for sku in resp["items_seller_list_get_response"]["items"]["item"][0]["skus"]["sku"]:
                        if sku["sku_id"] == sku_id:
                            properties_name_list = sku["properties_name"].split(';')
                            properties_list = sku["properties"].split(';')
                            props_name = ""
                            for properties_name in properties_name_list:
                                for properties in properties_list:
                                    properties_name = properties_name.replace(properties + ":", "")
                                if props_name != '':
                                    props_name += ";"
                                props_name += properties_name
                            # props_name = [i for i in props_names if sku["properties"] in i]
                            # if len(props_name) > 0:
                            #     # self.logging_link_info(props_name[0][(len(sku["properties"]) + 1):])
                            #     return props_name[0][(len(sku["properties"]) + 1):]
                            # # self.logging_link_info(sku["properties_name"].split(':')[1])
                            if props_name == "":
                                props_name = sku["properties_name"]
                            return props_name
                            #return sku["properties_name"].split(':')[1]
            return ""
        except Exception as ex:
            self.logging_link_error(traceback.format_exc())
            return ""

    def get_taobao_order(self, open_id, access_token, start_created="", end_created="", page_size=40, type="fixed,step"):
        """
        :description: 获取淘宝订单
        :param open_id：open_id
        :param access_token：access_token
        :param start_created：开始时间
        :param end_created：结束时间
        :param page_size：页大小
        :param type：订单类型
        :return 
        :last_editors: HuangJingCan
        """
        all_order = []
        has_next = True
        try:
            app_key, app_secret = self.get_app_key_secret()
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.OpenTradesSoldGetRequest()

            req.fields = "tid,status,payment,price,created,orders,num,pay_time,step_trade_status,step_paid_fee,type"
            # req.type = "fixed,step"
            req.type = type
            req.buyer_open_id = open_id
            req.page_size = page_size
            req.page_no = 1
            req.use_has_next = "true"

            if start_created == "":
                start_timestamp = TimeHelper.get_now_timestamp() - 90 * 24 * 60 * 60
                start_created = TimeHelper.timestamp_to_format_time(start_timestamp)
            # start_created = "2020-06-01 00:00:00"
            req.start_created = start_created
            if end_created != "":
                req.end_created = end_created

            while has_next:
                resp = req.getResponse(access_token)
                is_log_top = config.get_value("is_log_top",False)
                if is_log_top == True:
                    self.logging_link_info(str(resp) + "【access_token】：" + self.get_taobao_param().access_token + "【获取订单】")
                if "open_trades_sold_get_response" in resp.keys():
                    if "trades" in resp["open_trades_sold_get_response"].keys():
                        all_order = all_order + resp["open_trades_sold_get_response"]["trades"]["trade"]
                    req.page_no += 1
                    has_next = resp["open_trades_sold_get_response"]["has_next"]

            return all_order
        except Exception as ex:
            self.logging_link_error(traceback.format_exc())
            return []

    def rewards_status(self):
        """
        :description: rewards_status
        :param 
        :return: 
        :last_editors: CaiYouBin
        """
        status = [
            #等待卖家发货
            "WAIT_SELLER_SEND_GOODS",
            #卖家部分发货
            "SELLER_CONSIGNED_PART",
            #等待买家确认收货
            "WAIT_BUYER_CONFIRM_GOODS",
            #买家已签收（货到付款专用）
            "TRADE_BUYER_SIGNED",
            #交易成功
            "TRADE_FINISHED"
        ]
        return status

    def refund_status(self):
        """
        :description: 给予奖励的子订单退款状态
        :param 
        :return: 
        :last_editors: CaiYouBin
        """
        status = [
            #没有退款
            "NO_REFUND",
            #退款关闭
            "CLOSED",
            #卖家拒绝退款
            "WAIT_SELLER_AGREE"
        ]
        return status

    def instantiate_new(self):
        """
        :description: 实例化
        :param self:self
        :return app_info
        :last_editors: HuangJingCan
        """
        base_info = BaseInfoModel(context=self).get_entity()
        if not base_info:
            return self.reponse_json_error("BaseInfoError", "基础信息出错")
        app_name = base_info.product_name
        description = base_info.product_desc
        icon = base_info.product_icon
        template_id = config.get_value("client_template_id")
        template_version = base_info.client_ver
        access_token = self.get_taobao_param().access_token
        user_nick = self.get_taobao_param().user_nick
        open_id = self.get_taobao_param().open_id
        main_user_open_id = self.get_param("main_user_open_id")
        app_info_model = AppInfoModel(context=self)
        app_info = None

        # 产品千牛后台GM工具（运营人员模拟登录）
        app_id = self.get_param("app_id")
        if app_id:
            app_info = app_info_model.get_entity("app_id=%s", params=app_id)
            if app_info:
                return self.reponse_json_success({"app_id": app_info.app_id, "store_user_nick": app_info.store_user_nick, "user_nick": app_info.store_user_nick, "access_token": app_info.access_token})
            return self.reponse_json_error("Error", "对不起，该店铺未实例化。")

        if not user_nick:
            return self.reponse_json_error("Error", "对不起,请先授权登录")
        store_user_nick = user_nick.split(':')[0]
        if not store_user_nick:
            return self.reponse_json_error("Error", "对不起，请先授权登录")
        store_user_nick = user_nick.split(':')[0]
        app_info = app_info_model.get_entity("store_user_nick=%s", params=store_user_nick)
        # 有效时间获取
        dead_date = self.get_dead_date(store_user_nick)
        if app_info:
            if dead_date != "expire":
                app_info.expiration_date = dead_date
            access_token = self.get_token()
            if access_token != "":
                app_info.access_token = access_token
            if main_user_open_id != "" and app_info.main_user_open_id == "":
                app_info.main_user_open_id = main_user_open_id
            app_info_model.update_entity(app_info, "main_user_open_id,expiration_date,access_token")
            return self.reponse_json_success({"app_id": app_info.app_id, "store_user_nick": app_info.store_user_nick, "user_nick": user_nick, "access_token": app_info.access_token})

        # if self.get_is_test():
        #     return self.reponse_json_success()
        if ":" in user_nick:
            return self.reponse_json_error("AccountError", "对不起，初次创建活动包含实例化，请使用主账号进行创建。")

        try:
            app_key, app_secret = self.get_app_key_secret()
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.MiniappTemplateInstantiateRequest()

            req.clients = "taobao,tmall"
            req.description = description
            shop_info = self.get_shop(access_token)

            # self.logging_link_info("【实例化名称】" + ":" + str(app_name))
            req.ext_json = "{ \"name\":\"" + app_name + "\"}"
            req.icon = icon
            req.alias = app_name
            req.template_id = template_id
            req.template_version = template_version
            resp = req.getResponse(access_token)

            #录入数据库
            result_app = resp["miniapp_template_instantiate_response"]
            app_info = AppInfo()
            app_info.clients = req.clients
            app_info.app_desc = result_app["app_description"]
            app_info.app_icon = result_app["app_icon"]
            app_info.app_id = result_app["app_id"]
            app_info.app_name = result_app["app_name"]
            app_info.app_ver = result_app["app_version"]
            app_info.app_key = result_app["appkey"]
            app_info.preview_url = result_app["pre_view_url"]
            app_info.template_id = req.template_id
            app_info.template_ver = req.template_version
            app_info.access_token = access_token
            app_info.expiration_date = dead_date

            if "shop_seller_get_response" in shop_info.keys():
                app_info.store_name = shop_info["shop_seller_get_response"]["shop"]["title"]
                app_info.store_id = shop_info["shop_seller_get_response"]["shop"]["sid"]
                app_info.store_icon = shop_info["shop_seller_get_response"]["shop"]["pic_path"]
                if app_info.store_icon != "":
                    app_info.store_icon = "http://logo.taobao.com/shop-logo" + app_info.store_icon
                # if app_info.store_icon.find("http://") == -1:
                #     app_info.store_icon = "http://logo.taobao.com/shop-logo" + app_info.store_icon

            user_seller = self.get_user_seller(access_token)
            if "user_seller_get_response" in user_seller.keys():
                app_info.seller_id = user_seller["user_seller_get_response"]["user"]["user_id"]

            app_info.is_instance = 1
            app_info.store_user_nick = store_user_nick
            app_info.owner_open_id = open_id
            app_info.main_user_open_id = main_user_open_id
            app_info.instance_date = self.get_now_datetime()
            app_info.modify_date = self.get_now_datetime()
            #上线
            online_app_info = self.online_app(app_info.app_id, template_id, template_version, app_info.app_ver, access_token)
            if "miniapp_template_onlineapp_response" in online_app_info.keys():
                app_info.app_url = online_app_info["miniapp_template_onlineapp_response"]["app_info"]["online_url"]

            app_info.id = app_info_model.add_entity(app_info)

            self.create_operation_log(OperationType.add.value, app_info.__str__(), "instantiate_app", None, self.json_dumps(app_info))

            return self.reponse_json_success({"app_id": app_info.app_id, "store_user_nick": store_user_nick, "user_nick": user_nick, "access_token": access_token})
        except Exception as ex:
            self.logging_link_error(traceback.format_exc())
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=" in content:
                        if "名称已经存在" in content:
                            return self.reponse_json_error("CreateError", content[len("submsg="):], {"icon": icon, "app_name": app_name})
                        if "应用名称不合法" in content:
                            return self.reponse_json_error("CreateError", content[len("submsg="):], {"icon": icon, "app_name": app_name})
                        return self.reponse_json_error("CreateError", content[len("submsg="):], {"icon": icon, "app_name": app_name})

    def instantiate(self, user_nick, act_name, description, icon, name_ending):
        """
        :description: 实例化
        :param user_nick：用户昵称
        :param act_name：活动名称
        :param description：活动简介
        :param icon：活动图标
        :param name_ending：名称结尾
        :return app_info
        :last_editors: HuangJingCan
        """
        open_id = self.get_taobao_param().open_id

        app_info_model = AppInfoModel(context=self)
        store_user_nick = user_nick.split(':')[0]
        app_info = app_info_model.get_entity("store_user_nick=%s", params=store_user_nick)
        if not app_info:
            if ":" in user_nick:
                return self.reponse_json_error("Error", "对不起，初次创建活动包含实例化，请使用主账号进行创建。")
            base_info_model = BaseInfoModel(context=self)
            base_info = base_info_model.get_entity()
            template_id = config.get_value("client_template_id")
            template_version = base_info.client_ver
            product_name = base_info.product_name
            access_token = self.get_taobao_param().access_token
            app_info = self.instantiate_app(user_nick, open_id, description, icon, act_name, template_id, template_version, 1, access_token, name_ending, product_name)

            if isinstance(app_info, dict):
                if "error" in app_info.keys():
                    return self.reponse_json_error(app_info["error"], app_info["message"])

            self.create_operation_log(OperationType.add.value, app_info.__str__(), "instantiate", None, self.json_dumps(app_info))

        return app_info

    def instantiate_app(self, user_nick, open_id, description, icon, name, template_id, template_version, isfirst, access_token, name_ending, product_name):
        """
        :description: 实例化
        :param user_nick：用户昵称
        :param open_id：用户唯一标识
        :param description：活动简介
        :param icon：活动图标
        :param name：活动名称
        :param template_id：模板id
        :param template_version：模板版本
        :param isfirst：是否第一次
        :param access_token：access_token
        :param name_ending：name_ending
        :param product_name：项目名称
        :return app_info
        :last_editors: HuangJingCan
        """
        try:
            app_key, app_secret = self.get_app_key_secret()
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.MiniappTemplateInstantiateRequest()

            req.clients = "taobao,tmall"
            req.description = description
            shop_info = self.get_shop(access_token)

            if isfirst == 1 and shop_info:
                app_name = shop_info["shop_seller_get_response"]["shop"]["title"] + name_ending
            else:
                app_name = name
            # self.logging_link_info("【实例化名称】" + ":" + str(app_name))
            req.ext_json = "{ \"name\":\"" + app_name + "\"}"
            req.icon = icon
            req.name = app_name
            req.alias = product_name
            req.template_id = template_id
            req.template_version = template_version
            resp = req.getResponse(access_token)

            #录入数据库
            result_app = resp["miniapp_template_instantiate_response"]
            app_info_model = AppInfoModel(context=self)
            app_info = AppInfo()
            app_info.clients = req.clients
            app_info.app_desc = result_app["app_description"]
            app_info.app_icon = result_app["app_icon"]
            app_info.app_id = result_app["app_id"]
            app_info.app_name = result_app["app_name"]
            app_info.app_ver = result_app["app_version"]
            app_info.app_key = result_app["appkey"]
            app_info.preview_url = result_app["pre_view_url"]
            app_info.template_id = req.template_id
            app_info.template_ver = req.template_version

            if "shop_seller_get_response" in shop_info.keys():
                app_info.store_name = shop_info["shop_seller_get_response"]["shop"]["title"]
                app_info.store_id = shop_info["shop_seller_get_response"]["shop"]["sid"]

            user_seller = self.get_user_seller(access_token)
            if "user_seller_get_response" in user_seller.keys():
                app_info.seller_id = user_seller["user_seller_get_response"]["user"]["user_id"]

            app_info.is_instance = 1
            app_info.store_user_nick = user_nick.split(':')[0]
            app_info.owner_open_id = open_id
            app_info.instance_date = self.get_now_datetime()
            app_info.modify_date = self.get_now_datetime()
            #上线
            online_app_info = self.online_app(app_info.app_id, template_id, template_version, app_info.app_ver, access_token)
            if "miniapp_template_onlineapp_response" in online_app_info.keys():
                app_info.app_url = online_app_info["miniapp_template_onlineapp_response"]["app_info"]["online_url"]

            app_info.id = AppInfoModel(context=self).add_entity(app_info)

            return app_info
        except Exception as ex:
            self.logging_link_error(traceback.format_exc())
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=" in content:
                        if "名称已经存在" in content:
                            if isfirst == 1:
                                return self.instantiate_app(user_nick, open_id, description, icon, name, template_id, template_version, 0, access_token, name_ending, product_name)
                            else:
                                return {"error": "CreateError", "message": content[len("submsg="):]}
                        if "应用名称不合法" in content:
                            if isfirst == 1:
                                return self.instantiate_app(user_nick, open_id, description, icon, name, template_id, template_version, 0, access_token, name_ending, product_name)
                            else:
                                return {"error": "CreateError", "message": content[len("submsg="):]}
                        return {"error": "CreateError", "message": content[len("submsg="):]}

    def online_app(self, app_id, template_id, template_version, app_version, access_token):
        """
        :description: app上线
        :param app_id：app_id
        :param template_id：模板id
        :param template_version：模板版本
        :param app_version：app版本
        :param access_token：access_token
        :return 
        :last_editors: HuangJingCan
        """
        try:
            app_key, app_secret = self.get_app_key_secret()
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.MiniappTemplateOnlineappRequest()

            req.clients = "taobao,tmall"
            req.app_id = app_id
            req.template_id = template_id
            req.template_version = template_version
            req.app_version = app_version
            resp = req.getResponse(access_token)
            return resp
        except Exception as ex:
            self.logging_link_error(traceback.format_exc())
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        return self.reponse_json_error("NoPower", content[len("submsg="):])
                    if "submsg=" in content:
                        return self.reponse_json_error("Error", content[len("submsg="):])

    def get_shop(self, access_token):
        """
        :description: 获取店铺信息
        :param access_token：access_token
        :return: 
        :last_editors: HuangJingCan
        """
        try:
            app_key, app_secret = self.get_app_key_secret()
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.ShopSellerGetRequest()

            req.fields = "sid,title,pic_path"
            resp = req.getResponse(access_token)
            return resp
        except Exception as ex:
            self.logging_link_error(traceback.format_exc())
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        return self.reponse_json_error("NoPower", content[len("submsg="):])
                    if "submsg=" in content:
                        return self.reponse_json_error("Error", content[len("submsg="):])

    def get_user_seller(self, access_token):
        """
        :description: 获取关注店铺用户信息
        :param access_token：access_token
        :return: 
        :last_editors: HuangJingCan
        """
        try:
            app_key, app_secret = self.get_app_key_secret()
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.UserSellerGetRequest()

            req.fields = "user_id,nick,sex"
            resp = req.getResponse(access_token)
            return resp
        except Exception as ex:
            self.logging_link_error(traceback.format_exc())
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        return self.reponse_json_error("NoPower", content[len("submsg="):])
                    if "submsg=" in content:
                        return self.reponse_json_error("Error", content[len("submsg="):])

    def get_dead_date(self, user_nick):
        """
        :description: 获取过期时间
        :param user_nick：用户昵称
        :return 
        :last_editors: HuangJingCan
        """
        if self.get_is_test() == True:
            return config.get_value("test_dead_date")
        try:
            app_key, app_secret = self.get_app_key_secret()
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.VasSubscribeGetRequest()

            req.article_code = config.get_value("article_code")
            req.nick = user_nick
            resp = req.getResponse(self.get_taobao_param().access_token)
            if "article_user_subscribe" not in resp["vas_subscribe_get_response"]["article_user_subscribes"].keys():
                return "expire"
            return resp["vas_subscribe_get_response"]["article_user_subscribes"]["article_user_subscribe"][0]["deadline"]
        except Exception as ex:
            self.logging_link_error(traceback.format_exc())
            return "expire"

    def get_token(self):
        """
        :description: 获取授权token
        :param 
        :return: 
        :last_editors: CaiYouBin
        """
        if self.get_is_test() == True:
            return ""
        try:
            app_key, app_secret = self.get_app_key_secret()
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.ItemsOnsaleGetRequest()

            req.fields = "num_iid,title,nick,input_str,property_alias,sku,props_name,pic_url"
            req.page_no = 1
            req.page_size = 10
            resp = req.getResponse(self.get_taobao_param().access_token)

            return self.get_taobao_param().access_token
        except Exception as ex:
            self.logging_link_error(traceback.format_exc())
            return ""

    def get_goods_list(self, page_index, page_size, goods_name, order_tag, order_by, access_token):
        """
        :description: 导入商品列表（获取当前会话用户出售中的商品列表）
        :param page_index：页索引
        :param page_size：页大小
        :param goods_name：商品名称
        :param order_tag：order_tag
        :param order_by：排序类型
        :param access_token：access_token
        :return 
        :last_editors: HuangJingCan
        """
        try:
            app_key, app_secret = self.get_app_key_secret()
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.ItemsOnsaleGetRequest()

            req.fields = "num_iid,title,nick,price,input_str,property_alias,sku,props_name,pic_url"
            req.page_no = page_index + 1
            req.page_size = page_size
            if goods_name != "":
                req.q = goods_name
            req.order_by = order_tag + ":" + order_by

            resp = req.getResponse(access_token)
            if resp:
                resp["pageSize"] = page_size
                resp["pageIndex"] = page_index

            # self.logging_link_info(str(resp) + "【access_token】：" + self.get_taobao_param().access_token)
            return self.reponse_json_success(resp)
        except Exception as ex:
            self.logging_link_error(traceback.format_exc())
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        return self.reponse_json_error("NoPower", content[len("submsg="):])
                    if "submsg=" in content:
                        return self.reponse_json_error("Error", content[len("submsg="):])

    def get_goods_list_client(self, page_index, page_size, access_token):
        """
        :description: 导入商品列表（客户端）
        :param page_index：页索引
        :param page_size：页大小
        :param access_token：access_token
        :return 
        :last_editors: HuangJingCan
        """
        try:
            app_key, app_secret = self.get_app_key_secret()
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.ItemsOnsaleGetRequest()

            req.fields = "num_iid,title,nick,pic_url,price"
            req.page_no = page_index + 1
            req.page_size = page_size

            resp = req.getResponse(access_token)
            # self.logging_link_info(str(resp))
            goods_list = []
            if "items_onsale_get_response" in resp.keys():
                if "items" in resp["items_onsale_get_response"]:
                    if "item" in resp["items_onsale_get_response"]["items"]:
                        if len(resp["items_onsale_get_response"]["items"]["item"]) > 10:
                            goods_index_list = range(len(resp["items_onsale_get_response"]["items"]["item"]))
                            indexs = random.sample(goods_index_list, 10)
                            for i in range(0, 10):
                                goods_list.append(resp["items_onsale_get_response"]["items"]["item"][indexs[i]])
                        else:
                            goods_list = resp["items_onsale_get_response"]["items"]["item"]

                        random.randint(0, len(resp["items_onsale_get_response"]["items"]["item"]))
            if resp:
                resp["pageSize"] = page_size
                resp["pageIndex"] = page_index

            return self.reponse_json_success(goods_list)
        except Exception as ex:
            self.logging_link_error(traceback.format_exc())
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        return self.reponse_json_error("NoPower", content[len("submsg="):])
                    if "submsg=" in content:
                        return self.reponse_json_error("Error", content[len("submsg="):])

    def get_goods_info(self, num_iid, access_token):
        """
        :description: 导入商品列表
        :param num_iids：num_iids
        :param access_token：access_token
        :return 
        :last_editors: HuangJingCan
        """
        try:
            app_key, app_secret = self.get_app_key_secret()
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.ItemSellerGetRequest()

            req.fields = "num_iid,title,nick,pic_url,price,item_img.url,outer_id,sku,approve_status,prop_img"
            req.num_iid = num_iid
            resp = req.getResponse(access_token)
            # self.logging_link_info(str(resp))
            return self.reponse_json_success(resp)
        except Exception as ex:
            self.logging_link_error(traceback.format_exc())
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        return self.reponse_json_error("NoPower", content[len("submsg="):])
                    if "submsg=该商品已被删除" in content:
                        return self.reponse_json_error("GoodsDel", content[len("submsg="):])
                    if "submsg=" in content:
                        return self.reponse_json_error("Error", content[len("submsg="):])

    def app_update(self, app_id, client_template_id, client_ver, access_token, app_info, old_app_info):
        """
        :description: app更新
        :param app_id:app_id
        :param client_template_id:client_template_id
        :param client_ver:client_ver
        :param access_token:access_token
        :param app_info:app_info
        :param old_app_info:old_app_info
        :return 
        :last_editors: HuangJingCan
        """
        try:
            app_key, app_secret = self.get_app_key_secret()
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.MiniappTemplateUpdateappRequest()

            req.clients = "taobao,tmall"
            req.app_id = app_id
            req.template_id = client_template_id
            req.template_version = client_ver
            resp = req.getResponse(access_token)

            if resp and ("miniapp_template_updateapp_response" in resp.keys()):
                app_version = resp["miniapp_template_updateapp_response"]["app_version"]
                online_app_info = self.online_app(app_id, client_template_id, client_ver, app_version, access_token)
                if "miniapp_template_onlineapp_response" in online_app_info.keys():
                    app_info.app_ver = resp["miniapp_template_updateapp_response"]["app_version"]
                    app_info.template_ver = client_ver
                    app_info.modify_date = self.get_now_datetime()
                    AppInfoModel(context=self).update_entity(app_info)
                    # self.logging_link_info(str(resp) + "【更新】")
                    self.create_operation_log(OperationType.update.value, app_info.__str__(), "AppUpdateHandler", self.json_dumps(old_app_info), self.json_dumps(app_info))
            return self.reponse_json_success()
        except Exception as ex:
            self.logging_link_error(traceback.format_exc())
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        return self.reponse_json_error("NoPower", content[len("submsg="):])
                    if "submsg=" in content:
                        return self.reponse_json_error("Error", content[len("submsg="):])

    def change_throw_goods_list_status(self, throw_goods_ids, url, status):
        """
        :description: change_throw_goods_list_status
        :param throw_goods_ids：throw_goods_ids
        :param url：链接地址
        :param status：状态
        :return 
        :last_editors: HuangJingCan
        """
        try:
            app_key, app_secret = self.get_app_key_secret()
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.MiniappDistributionItemsBindRequest()

            req.target_entity_list = throw_goods_ids
            req.url = url
            req.add_bind = status
            resp = req.getResponse(self.get_taobao_param().access_token)
            return resp
        except Exception as ex:
            self.logging_link_error(traceback.format_exc())
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        return self.return_dict_error("NoPower", content[len("submsg="):])
                    if "submsg=" in content:
                        return self.return_dict_error("Error", content[len("submsg="):])

    def get_goods_list_for_goodsids(self, num_iids, access_token, fields="num_iid,title,nick,pic_url,price,input_str,property_alias,sku,props_name,outer_id,prop_img"):
        """
        :description: 批量获取商品详细信息(num_iids上限20个，超过淘宝会报错)
        :param num_iids：商品id列表
        :param access_token：access_token
        :param fields：返回字段
        :return list
        :last_editors: HuangJingCan
        """
        num_iid_list = num_iids.split(',')
        page_size = 20
        page_count = int(len(num_iid_list) / page_size) if len(num_iid_list) % page_size == 0 else int(len(num_iid_list) / page_size) + 1
        goods_list = []
        for i in range(0, page_count):
            cur_num_iids = ",".join(num_iid_list[i * page_size:page_size * (i + 1)])
            try:
                app_key, app_secret = self.get_app_key_secret()
                top.setDefaultAppInfo(app_key, app_secret)
                req = top.api.ItemsSellerListGetRequest()

                req.fields = fields
                req.num_iids = cur_num_iids
                resp = req.getResponse(access_token)
                if "items_seller_list_get_response" in resp.keys():
                    if "items" in resp["items_seller_list_get_response"].keys():
                        if "item" in resp["items_seller_list_get_response"]["items"].keys():
                            goods_list.extend(resp["items_seller_list_get_response"]["items"]["item"])
            except Exception as ex:
                self.logging_link_error(traceback.format_exc())
                if "submsg" in str(ex):
                    content_list = str(ex).split()
                    for content in content_list:
                        if "submsg=该子帐号无此操作权限" in content:
                            return self.return_dict_error("NoPower", content[len("submsg="):])
                        if "submsg=" in content:
                            return self.return_dict_error("Error", content[len("submsg="):])

        return {"items_seller_list_get_response": {"items": {"item": goods_list}}}

    def get_taobao_order_info(self, order_no, access_token):
        """
        :description: 获取单笔订单
        :param order_no：订单编号
        :param access_token：access_token
        :return: 
        :last_editors: CaiYouBin
        """
        try:
            app_key, app_secret = self.get_app_key_secret()
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.OpenTradeGetRequest()

            req.fields = "tid,status,payment,price,created,orders,num,pay_time,buyer_open_uid"
            req.tid = order_no
            resp = req.getResponse(access_token)
            if "open_trade_get_response" in resp.keys():
                if "trade" in resp["open_trade_get_response"]:
                    return resp["open_trade_get_response"]["trade"]
                return None
            return resp
        except Exception as ex:
            self.logging_link_error(traceback.format_exc())
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        return self.return_dict_error("NoPower", content[len("submsg="):])
                    if "submsg=" in content:
                        return self.return_dict_error("Error", content[len("submsg="):])

    def get_coupon_details(self, right_ename):
        """
        :description: 获取优惠券详情信息(请求top接口)
        :param right_ename:奖池ID
        :return: dict
        :last_editors: LaiKaiXiang
        """
        right_ename = self.get_param("right_ename")
        access_token = self.get_taobao_param().access_token
        resp = ""
        try:
            app_key, app_secret = self.get_app_key_secret()
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.AlibabaBenefitQueryRequest()
            req.ename = right_ename
            req.app_name = "promotioncenter-" + config.get_value("server_template_id")
            req.award_type = "1"
            resp = req.getResponse(access_token)

            return self.reponse_json_success(resp)
        except Exception as ex:
            self.logging_link_error(traceback.format_exc())
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        return self.reponse_json_error("NoPower", content[len("submsg="):])
                    if "submsg=" in content:
                        return self.reponse_json_error("Error", content[len("submsg="):])

    def benefit_send(self, right_ename, open_id, access_token):
        """
        :description: 发奖接口(请求top接口)
        :param right_ename:奖池ID
        :param open_id:open_id
        :param access_token:access_token
        :return: dict
        :last_editors: HuangJianYi
        """
        resp = {}
        try:
            app_key, app_secret = self.get_app_key_secret()
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.AlibabaBenefitSendRequest()
            req.right_ename = right_ename
            req.receiver_id = open_id
            req.user_type = "taobao"
            req.unique_id = str(open_id) + str(right_ename) + str(TimeHelper.get_now_timestamp())
            req.app_name = "promotioncenter-" + config.get_value("server_template_id")
            resp = req.getResponse(access_token)
            return resp
        except Exception as ex:
            self.logging_link_error(traceback.format_exc())
            return {}

    def get_member_info(self, access_token):
        """
        :description: 获取top接口淘宝会员信息
        :param access_token:access_token
        :return:resp
        :last_editors: HuangJianYi
        """
        try:
            app_key, app_secret = self.get_app_key_secret()
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.CrmMemberIdentityGetRequest()
            req.mix_nick = self.get_taobao_param().mix_nick
            resp = req.getResponse(access_token)
            return resp
        except Exception as ex:
            self.logging_link_error(traceback.format_exc())
            return {}

    def check_is_member(self, access_token):
        """
        :description: 获取top接口淘宝会员信息
        :param access_token:access_token
        :return:bool
        :last_editors: HuangJianYi
        """
        is_member = False
        resp = self.get_member_info(access_token)
        if "crm_member_identity_get_response" in resp.keys():
            if "result" in resp["crm_member_identity_get_response"].keys():
                if "member_info" in resp["crm_member_identity_get_response"]["result"].keys():
                    is_member = True
        return is_member

    def get_user_group_list(self, access_token):
        """
        :description: 获取top接口用户加入的群聊列表
        :param access_token:access_token
        :return:dict
        :last_editors: HuangJianYi
        """
        try:
            app_key, app_secret = self.get_app_key_secret()
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.ChattingPlatformUserGroupListRequest()
            req.user_nick = self.get_taobao_param().user_nick
            resp = req.getResponse(access_token)
            return resp
        except Exception as ex:
            self.logging_link_error(traceback.format_exc())
            return {}

    def check_join_group(self, access_token):
        """
        :description: 请求top接口判断是否加入群聊
        :param access_token:access_token
        :return:bool
        :last_editors: HuangJianYi
        """
        is_join_group = False
        resp = self.get_user_group_list(access_token)
        if "chatting_platform_user_group_list_response" in resp.keys():
            if "result" in resp["chatting_platform_user_group_list_response"].keys():
                if "group_list" in resp["chatting_platform_user_group_list_response"]["result"].keys():
                    if "open_group_info_dto" in resp["chatting_platform_user_group_list_response"]["result"]["group_list"].keys():
                        if len(resp["chatting_platform_user_group_list_response"]["result"]["group_list"]["open_group_info_dto"]) > 0:
                            is_join_group = True
        return is_join_group

    def get_join_member_url(self, access_token):
        """
        :description: 请求top接口获取加入会员地址
        :param access_token:access_token
        :return:str
        :last_editors: HuangJianYi
        """
        join_member_url = ""
        try:
            app_key, app_secret = self.get_app_key_secret()
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.CrmMemberJoinurlGetRequest()
            req.callback_url = ""
            req.extra_info = "{\"source\":\"isvapp\",\"activityId\":\"\",\"entrance\":\"hudong\"}"
            resp = req.getResponse(access_token)
            if "crm_member_joinurl_get_response" in resp.keys():
                if "result" in resp["crm_member_joinurl_get_response"].keys():
                    if "result" in resp["crm_member_joinurl_get_response"]["result"].keys():
                        join_member_url = resp["crm_member_joinurl_get_response"]["result"]["result"]
        except Exception as ex:
            self.logging_link_error(traceback.format_exc())
            return ""

        return join_member_url

    def get_taobao_refund_order(self, buyer_nick, access_token, start_modified="", end_modified=""):
        """
        :description: 获取淘宝退款订单
        :param open_id：open_id
        :param access_token：access_token
        :param start_created：开始时间
        :param end_created：结束时间
        :return list
        :last_editors: HuangJingCan
        """
        all_order = []
        has_next = True
        try:
            top.setDefaultAppInfo(config.get_value("app_key"), config.get_value("app_secret"))
            req = top.api.RefundsReceiveGetRequest()

            req.fields = "refund_id,tid,oid,title,total_fee,status,created,refund_fee,modified,num"
            # refund_id：退款单号, tid：淘宝交易单号, oid：子订单号, title：商品名称 , total_fee：订单总价, status：退款状态,
            # created：退款申请时间, refund_fee：退款金额, modified：更新时间, num: 购买数量
            req.type = "fixed"
            req.buyer_nick = buyer_nick
            req.page_size = 100
            req.page_no = 1
            req.use_has_next = "true"

            if start_modified == "":
                start_timestamp = TimeHelper.get_now_timestamp() - 90 * 24 * 60 * 60
                start_modified = TimeHelper.timestamp_to_format_time(start_timestamp)
            req.start_modified = start_modified
            if end_modified != "":
                req.end_modified = end_modified

            while has_next:
                resp = req.getResponse(access_token)
                if "refunds_receive_get_response" in resp.keys():
                    if "refunds" in resp["refunds_receive_get_response"].keys():
                        all_order = all_order + resp["refunds_receive_get_response"]["refunds"]["refund"]
                    req.page_no += 1
                    has_next = resp["refunds_receive_get_response"]["has_next"]
            return all_order
        except Exception as ex:
            self.logging_link_error("【获取淘宝退款订单失败】" + str(ex))
            return []

    def refund_receive_status(self):
        """
        :description: 退款接口返回的状态判断
        :return: str
        :last_editors: ChenCheng
        """
        status = [
            #卖家已经同意退款，等待买家退货
            "WAIT_BUYER_RETURN_GOODS",
            #买家已经退货，等待卖家确认收货
            "WAIT_SELLER_CONFIRM_GOODS",
            #退款成功
            "SUCCESS",
        ]
        return status

    def get_inventory_goods_list(self, page_index, page_size, goods_name, order_tag, order_by, access_token):
        """
        :description: 导入商品列表（获取当前用户作为卖家的仓库中的商品列表）
        :param page_index：页索引
        :param page_size：页大小
        :param goods_name：商品名称
        :param order_tag：order_tag
        :param order_by：排序类型
        :param access_token：access_token
        :return 
        :last_editors: HuangJingCan
        """
        try:
            app_key, app_secret = self.get_app_key_secret()
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.ItemsInventoryGetRequest()

            req.fields = "num_iid,title,nick,price,input_str,property_alias,sku,props_name,pic_url"
            req.page_no = page_index
            req.page_size = page_size
            if goods_name != "":
                req.q = goods_name
            req.order_by = order_tag + ":" + order_by

            resp = req.getResponse(access_token)
            if resp:
                resp["pageSize"] = page_size
                resp["pageIndex"] = page_index

            # self.logging_link_info(str(resp) + "【access_token】：" + self.get_taobao_param().access_token)
            return self.reponse_json_success(resp)
        except Exception as ex:
            self.logging_link_error(traceback.format_exc())
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        return self.reponse_json_error("NoPower", content[len("submsg="):])
                    if "submsg=" in content:
                        return self.reponse_json_error("Error", content[len("submsg="):])

    def get_crm_point_available(self, mix_nick, access_token, is_log=False):
        """
        :description: 获取店铺会员积分
        :param user_nick：用户昵称
        :param access_token：access_token
        :param is_log：是否记录返回信息
        :return 返回店铺会员积分
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            app_key, app_secret = self.get_app_key_secret()
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.CrmPointAvailableGetRequest()
            req.mix_nick = mix_nick
            resp = req.getResponse(access_token)
            if is_log:
                self.logging_link_info("【req】:" + self.json_dumps(req) + "【resp】:" + str(resp) + "【access_token】：" + access_token + "【获取店铺会员积分】")
            if "crm_point_available_get_response" not in resp:
                invoke_result_data.success = False
                return invoke_result_data
            if "result" not in resp["crm_point_available_get_response"]:
                invoke_result_data.success = False
                return invoke_result_data
            invoke_result_data.data = resp["crm_point_available_get_response"]["result"]
            return invoke_result_data
        except Exception as ex:
            self.logging_link_error(traceback.format_exc())
            invoke_result_data.success = False
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        invoke_result_data.error_code = "no_power"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
                    if "submsg=" in content:
                        invoke_result_data.error_code = "error"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
            return invoke_result_data

    def change_crm_point(self, open_id, change_type, opt_type, quantity, access_token, buyer_nick="", activity_id=0, activity_name="", is_log=False):
        """
        :description: 操作店铺会员积分
        :param open_id：买家id(open_id)
        :param change_type：变更类型：0交易，1：互动活动，2：权益兑换，3：手工调整
        :param opt_type：操作类型，0：增加，1：扣减
        :param quantity：积分数量
        :param access_token：access_token
        :param buyer_nick：买家昵称
        :param activity_id：活动Id
        :param activity_name：活动名称
        :param is_log：是否记录返回信息
        :return 返回操作结果
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            app_key, app_secret = self.get_app_key_secret()
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.CrmPointChangeRequest()
            if activity_id > 0:
                req.activity_id = activity_id
            if activity_name:
                req.activity_name = activity_name
            req.change_type = change_type
            req.opt_type = opt_type
            req.quantity = quantity
            if open_id:
                req.open_id = open_id
            if buyer_nick:
                req.buyer_nick = buyer_nick
            resp = req.getResponse(access_token)
            if is_log:
                self.logging_link_info("【req】:" + self.json_dumps(req) + "【resp】:" + str(resp) +  "【access_token】：" + access_token + "【操作店铺会员积分】")
            if "crm_point_change_response" not in resp:
                invoke_result_data.success = False
                return invoke_result_data
            if "result" not in resp["crm_point_change_response"]:
                invoke_result_data.success = False
                return invoke_result_data
            invoke_result_data.data = resp["crm_point_change_response"]["result"]
            return invoke_result_data
        except Exception as ex:
            self.logging_link_error(traceback.format_exc())
            invoke_result_data.success = False
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        invoke_result_data.error_code = "no_power"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
                    if "submsg=" in content:
                        invoke_result_data.error_code = "error"
                        invoke_result_data.error_message = content[len("submsg="):]
                        return invoke_result_data
            return invoke_result_data

    def get_project_code(self, user_nick):
        """
        :description: 获取项目编码
        :param user_nick：用户昵称
        :return 
        :last_editors: HuangJingCan
        """
        try:
            app_key, app_secret = self.get_app_key_secret()
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.VasSubscribeGetRequest()

            req.article_code = config.get_value("article_code")
            req.nick = user_nick
            resp = req.getResponse(self.get_taobao_param().access_token)
            if "article_user_subscribe" not in resp["vas_subscribe_get_response"]["article_user_subscribes"].keys():
                return ""
            return resp["vas_subscribe_get_response"]["article_user_subscribes"]["article_user_subscribe"][0]["item_code"]
        except Exception as ex:
            self.logging_link_error(traceback.format_exc())
            return ""