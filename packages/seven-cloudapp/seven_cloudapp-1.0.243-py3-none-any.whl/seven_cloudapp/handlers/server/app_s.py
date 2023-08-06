# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-05-24 17:26:33
@LastEditTime: 2022-07-28 14:12:23
@LastEditors: HuangJianYi
:description: App相关
"""
from seven_cloudapp.handlers.top_base import *

from seven_cloudapp.models.db_models.app.app_info_model import *
from seven_cloudapp.models.db_models.base.base_info_model import *
from seven_cloudapp.models.db_models.login.login_log_model import *


class BaseInfoHandler(SevenBaseHandler):
    """
    :description: 基础信息处理
    """
    def post_async(self):
        """
        :description: 基础信息处理入库
        :param customer_service: 客服号
        :param experience_img: 案例二维码图
        :param client_ver: 客户端版本号
        :param server_ver: 服务端版本号
        :param update_function: 版本更新内容
        :param store_study_url: 店铺装修教程图文地址（如何上架小程序）
        :param study_url: 后台配置图文教程
        :param video_url: 后台配置视频教程
        :param course_url: 主账号授权子账号教程
        :param price_gare: 价格档位说明
        :param product_price: 产品价格信息
        :param decoration_poster: 装修海报
        :param friend_link: 友情链接
        :param menu_config: 菜单配置信息
        :param is_remind_phone: 是否提醒提示配置手机号
        :return: 
        :last_editors: HuangJingCan
        """
        customer_service = self.get_param("customer_service")
        experience_img = self.get_param("experience_img")
        client_ver = self.get_param("client_ver")
        server_ver = self.get_param("server_ver")
        update_function = self.get_param("update_function")
        store_study_url = self.get_param("store_study_url")
        study_url = self.get_param("study_url")
        video_url = self.get_param("video_url")
        course_url = self.get_param("course_url")
        price_gare = self.get_param("price_gare")
        product_price = self.get_param("product_price")
        decoration_poster = self.get_param("decoration_poster")
        friend_link = self.get_param("friend_link")
        menu_config = self.get_param("menu_config")
        is_remind_phone = int(self.get_param("is_remind_phone", 0))

        # 数据入库
        base_info_model = BaseInfoModel(context=self)
        base_info = base_info_model.get_entity()

        is_add = False
        if not base_info:
            is_add = True
            base_info = BaseInfo()

        base_info.customer_service = customer_service
        base_info.experience_img = experience_img
        base_info.client_ver = client_ver
        base_info.server_ver = server_ver
        base_info.update_function = update_function
        base_info.store_study_url = store_study_url
        base_info.study_url = study_url
        base_info.video_url = video_url
        base_info.course_url = course_url
        base_info.price_gare = price_gare
        base_info.product_price = product_price
        base_info.decoration_poster = decoration_poster
        base_info.friend_link = friend_link
        base_info.menu_config = menu_config
        base_info.is_remind_phone = is_remind_phone
        base_info.modify_date = self.get_now_datetime()

        if is_add:
            base_info.create_date = base_info.modify_date
            base_info_model.add_entity(base_info)
        else:
            base_info_model.update_entity(base_info)

        return self.reponse_json_success()

    def get_async(self):
        """
        :description: 基础信息获取
        :param 
        :return: BaseInfo
        :last_editors: HuangJingCan
        """
        base_info = BaseInfoModel(context=self).get_entity()
        if not base_info:
            return self.reponse_json_error("BaseInfoError", "基础信息出错")

        # 左上角信息
        info = {}
        info["company"] = "天志互联"
        info["miniappName"] = base_info.product_name
        info["logo"] = base_info.product_icon

        # 左边菜单
        menu_list = []
        menu = {}
        menu["name"] = "创建活动"
        menu["key"] = "create_action"
        menu_list.append(menu)
        menu = {}
        menu["name"] = "活动管理"
        menu["key"] = "act_manage"
        menu_list.append(menu)
        menu = {}
        menu["name"] = "装修教程"
        menu["key"] = "decoration_poster"
        menu_list.append(menu)
        menu = {}
        menu["name"] = "版本更新"
        menu["key"] = "update_ver"
        menu_list.append(menu)

        # 左边底部菜单
        bottom_button_list = []
        bottom_button = {}
        bottom_button["title"] = "发票管理"
        bottom_button["handling_event"] = "popup"
        bottom_button["event_name"] = "billManage"
        bottom_button_list.append(bottom_button)
        bottom_button = {}
        bottom_button["title"] = "配置教程"
        bottom_button["handling_event"] = "popup"
        bottom_button["event_name"] = "use_teaching"
        bottom_button_list.append(bottom_button)
        bottom_button = {}
        bottom_button["title"] = "联系旺旺"
        bottom_button["handling_event"] = "outtarget"
        bottom_button["event_name"] = "http://amos.alicdn.com/getcid.aw?v=2&uid=%E5%A4%A9%E5%BF%97%E4%BA%92%E8%81%94&site=cntaobao&s=1&groupid=0&charset=utf-8"
        bottom_button_list.append(bottom_button)
        bottom_button = {}
        bottom_button["title"] = "号码绑定"
        bottom_button["handling_event"] = "popup"
        bottom_button["event_name"] = "bind_phone"
        bottom_button_list.append(bottom_button)

        # 右边使用指引
        use_point_list = []
        use_point = {}
        use_point["index"] = "1"
        use_point["title"] = "创建活动并配置完成"
        use_point_list.append(use_point)
        use_point = {}
        use_point["index"] = "2"
        use_point["title"] = "将淘宝小程序装修至店铺"
        use_point_list.append(use_point)
        use_point = {}
        use_point["index"] = "3"
        use_point["title"] = "正式运营淘宝小程序"
        use_point_list.append(use_point)

        data = {}
        data["serverName"] = "在线拆盲盒模板"
        data["info"] = info
        data["menu"] = menu_list
        data["bottom_button"] = bottom_button_list
        data["use_point"] = use_point_list
        if base_info:
            # 把string转成数组对象
            base_info.update_function = self.json_loads(base_info.update_function) if base_info.update_function else []
            base_info.price_gare = self.json_loads(base_info.price_gare) if base_info.price_gare else []
            base_info.product_price = self.json_loads(base_info.product_price) if base_info.product_price else []
            base_info.decoration_poster = self.json_loads(base_info.decoration_poster) if base_info.decoration_poster else []
            base_info.friend_link = self.json_loads(base_info.friend_link) if base_info.friend_link else []
            base_info.menu_config = self.json_loads(base_info.menu_config) if base_info.menu_config else []
            data["base_info"] = base_info.__dict__

        if base_info:
            return self.reponse_json_success(data)
        else:
            return self.reponse_json_error("BaseInfoError", "基础信息出错")


class InstantiateAppHandler(TopBaseHandler):
    """
    :description: 实例化小程序
    """
    @filter_check_params()
    def get_async(self):
        """
        :description: 实例化
        :return app_info
        :last_editors: HuangJingCan
        """
        # if self.get_is_test():
        #     return self.reponse_json_success({"app_id": "3000000026366853", "store_user_nick": "loveyouhk", "user_nick": "loveyouhk", "access_token": "50000400c44tV0dokOtB9blVhqxExuGaBgQhrVujjfJn0erSGRlxbEzI1a99a16dAZu"})
        return self.instantiate_new()


class TelephoneHandler(SevenBaseHandler):
    """
    :description: 更新手机号
    """
    @filter_check_params("telephone")
    def get_async(self):
        """
        :description: 更新手机号
        :param telephone：手机号
        :param check_code：验证码
        :return: 
        :last_editors: HuangJingCan
        """
        open_id = self.get_taobao_param().open_id
        app_id = self.get_param("app_id")
        telephone = self.get_param("telephone")
        check_code = self.get_param("check_code")
        modify_date = self.get_now_datetime()

        check_code_re = self.redis_init().get("user_" + open_id + "_bind_phone_code")
        if check_code_re == None:
            return self.reponse_json_error("CheckCodeError", "验证码已过期")

        check_code_re = str(check_code_re, 'utf-8')

        if check_code != check_code_re:
            return self.reponse_json_error("CheckCodeError", "验证码错误")

        AppInfoModel(context=self).update_table("app_telephone=%s,modify_date=%s", "app_id=%s", [telephone, modify_date, app_id])

        return self.reponse_json_success()


class AppUpdateHandler(TopBaseHandler):
    """
    :description: 前端版本更新
    """
    @filter_check_params()
    def get_async(self):
        """
        :description: 前端版本更新
        :param app_id:app_id
        :return: 
        :last_editors: HuangJingCan
        """
        app_id = self.get_param("app_id")
        client_template_id = config.get_value("client_template_id")
        test_client_ver = config.get_value("test_client_ver")
        access_token = self.get_taobao_param().access_token

        base_info = BaseInfoModel(context=self).get_entity()
        client_ver = base_info.client_ver

        app_info = AppInfoModel(context=self).get_entity("app_id=%s", params=app_id)
        if not app_info:
            return self.reponse_json_error("NoApp", "对不起，找不到该APP")

        old_app_info = deepcopy(app_info)

        #指定账号升级
        if test_client_ver:
            user_nick = self.get_taobao_param().user_nick
            if user_nick:
                if user_nick == config.get_value("test_user_nick"):
                    client_ver = test_client_ver

        return self.app_update(app_id, client_template_id, client_ver, access_token, app_info, old_app_info)


class AppInfoHandler(TopBaseHandler):
    """
    :description: 小程序信息
    """
    @filter_check_params()
    def get_async(self):
        """
        :description: 小程序信息
        :param 
        :return app_info
        :last_editors: HuangJingCan
        """
        app_id = self.get_param("app_id")
        store_user_nick = self.get_taobao_param().user_nick.split(':')[0]
        if not store_user_nick:
            return self.reponse_json_error("Error", "对不起，请先授权登录")
        open_id = self.get_taobao_param().open_id
        if not open_id:
            return self.reponse_json_error("Error", "对不起，请先登录")
        open_id = self.get_taobao_param().open_id
        main_user_open_id = self.get_param("main_user_open_id")

        app_info_model = AppInfoModel(context=self)
        if app_id:
            app_info = app_info_model.get_entity("app_id=%s", params=app_id)
        else:
            app_info = app_info_model.get_entity("store_user_nick=%s", params=store_user_nick)

        dead_date = self.get_dead_date(store_user_nick)
        login_log = LoginLogModel(context=self).get_entity("open_id=%s", order_by="id desc", params=open_id)
        if app_info:
            access_token = self.get_token()
            if access_token != "":
                app_info.access_token = access_token
            if dead_date != "expire":
                app_info.expiration_date = dead_date
            if app_info.main_user_open_id == "":
                app_info.main_user_open_id = main_user_open_id
            app_info_model.update_entity(app_info)

            app_info.surplus_value = 0
            app_info.user_nick = self.get_taobao_param().user_nick
            app_info.dead_date = dead_date
            if app_info.dead_date != "expire":
                now_timestamp = TimeHelper.datetime_to_timestamp(datetime.datetime.strptime(TimeHelper.get_now_format_time('%Y-%m-%d 00:00:00'), '%Y-%m-%d %H:%M:%S'))
                dead_date_timestamp = TimeHelper.datetime_to_timestamp(datetime.datetime.strptime(app_info.dead_date, '%Y-%m-%d %H:%M:%S'))
                app_info.surplus_day = int(int(abs(dead_date_timestamp - now_timestamp)) / 24 / 3600)

            if login_log:
                app_info.last_login_date = login_log.modify_date
            else:
                app_info.last_login_date = ""

            return self.reponse_json_success(app_info)

        app_info = AppInfo()
        app_info.access_token = self.get_taobao_param().access_token
        base_info = BaseInfoModel(context=self).get_dict()
        app_info.template_ver = base_info["client_ver"]
        app_info.surplus_value = 0
        app_info.user_nick = self.get_taobao_param().user_nick
        app_info.dead_date = dead_date

        if app_info.dead_date != "expire":
            now_timestamp = TimeHelper.datetime_to_timestamp(datetime.datetime.strptime(TimeHelper.get_now_format_time('%Y-%m-%d 00:00:00'), '%Y-%m-%d %H:%M:%S'))
            dead_date_timestamp = TimeHelper.datetime_to_timestamp(datetime.datetime.strptime(app_info.dead_date, '%Y-%m-%d %H:%M:%S'))
            app_info.surplus_day = int(int(abs(dead_date_timestamp - now_timestamp)) / 24 / 3600)

        if login_log:
            app_info.last_login_date = login_log.create_date
        else:
            app_info.last_login_date = ""

        return self.reponse_json_success(app_info)


# class AppInfoUpdateHandler(TopBaseHandler):
#     """
#     :description: 更新appinfo相关信息
#     """
#     @filter_check_params()
#     def get_async(self):
#         """
#         :description: 更新appinfo相关信息
#         :param update_field：需要更新的字段
#         :return str
#         :last_editors: HuangJingCan
#         """
#         update_field = self.get_param("update_field")
#         app_info_model = AppInfoModel(context=self)
#         page_size = 100
#         if update_field == "store_icon":
#             where = "store_icon='' and access_token!=''"
#             record_count = app_info_model.get_total(where)
#             page_count = SevenHelper.get_page_count(page_size, record_count)
#             for page_index in range(0, page_count):
#                 p_list, p_total = app_info_model.get_page_list("*", page_index, page_size, where)
#                 for info in p_list:
#                     shop_info = self.get_shop(info.access_token)
#                     if shop_info:
#                         store_icon = shop_info["shop_seller_get_response"]["shop"]["pic_path"]
#                         if store_icon:
#                             store_icon = "http://logo.taobao.com/shop-logo" + store_icon
#                             app_info_model.update_table("store_icon=%s", "id=%s", [store_icon, info.id])

#         return self.reponse_json_success(self.get_now_datetime())