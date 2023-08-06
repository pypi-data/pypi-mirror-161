# -*- coding: utf-8 -*-
"""
:Author: CaiYouBin
:Date: 2020-05-26 17:38:03
@LastEditTime: 2021-06-29 18:20:31
@LastEditors: WangQiang
:description: 主题皮肤相关
"""
from seven_cloudapp.handlers.seven_base import *

from seven_cloudapp.models.db_models.theme.theme_info_model import *
from seven_cloudapp.models.db_models.theme.theme_ver_model import *
from seven_cloudapp.models.db_models.skin.skin_info_model import *
from seven_cloudapp.models.db_models.act.act_info_model import *


class ThemeInfoHandler(SevenBaseHandler):
    """
    :description: 获取主题（皮肤）信息
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 获取主题（皮肤）信息
        :param act_id：活动id
        :param ver_no：客户端版本号
        :return 主题信息
        :last_editors: HuangJingCan
        """
        act_id = int(self.get_param("act_id", 0))
        ver_no = self.get_param("ver_no")
        act_info_model = ActInfoModel(context=self)
        theme_info_model = ThemeInfoModel(context=self)

        act_dict = act_info_model.get_dict_by_id(act_id)
        if not act_dict:
            return self.reponse_json_error("NoAct", "对不起，找不到该活动")

        theme_id = act_dict["theme_id"]
        theme_info = theme_info_model.get_dict("id=%s", params=theme_id)
        if not theme_info:
            return self.reponse_json_error("NoTheme", "对不起，找不到该主题")

        out_id = theme_info["out_id"]
        if ver_no:
            theme_ver = ThemeVerModel(context=self).get_entity("out_id=%s and ver_no=%s", params=[out_id, ver_no])
            if theme_ver and theme_ver.client_json != "":
                theme_info["client_json"] = theme_ver.client_json

        skin_info_list = SkinInfoModel(context=self).get_dict_list("theme_id=%s", params=theme_id)

        theme_info["skin_list"] = skin_info_list

        return self.reponse_json_success(theme_info)


class ThemeSaveHandler(SevenBaseHandler):
    """
    :description: 保存主题
    """
    @filter_check_params("out_id")
    def post_async(self):
        """
        :description: 保存主题
        :param app_id：app_id
        :param theme_name：主题名称
        :param client_json：客户端内容json
        :param server_json：服务端内容json
        :param out_id：外部id
        :param ver_no：客户端版本号
        :return: 
        :last_editors: HuangJingCan
        """
        app_id = self.get_param("app_id")
        theme_name = self.get_param("theme_name")
        client_json = self.get_param("client_json")
        server_json = self.get_param("server_json")
        out_id = self.get_param("out_id")
        ver_no = self.get_param("ver_no")

        theme_info_model = ThemeInfoModel(context=self)
        theme_ver_model = ThemeVerModel(context=self)
        theme_info = theme_info_model.get_entity("out_id=%s", params=out_id)
        if theme_info:
            if client_json:
                if ver_no:
                    theme_ver = theme_ver_model.get_entity('out_id=%s and ver_no=%s', params=[out_id, ver_no])
                    if theme_ver:
                        theme_ver_model.update_table('client_json=%s', 'out_id=%s and ver_no=%s', params=[client_json, out_id, ver_no])
                    else:
                        theme_ver = ThemeVer()
                        theme_ver.app_id = theme_info.app_id
                        theme_ver.out_id = out_id
                        theme_ver.theme_id = theme_info.id
                        theme_ver.client_json = client_json
                        theme_ver.ver_no = ver_no
                        theme_ver.create_date = theme_info.create_date
                        theme_ver_model.add_entity(theme_ver)
                else:
                    theme_info_model.update_table('client_json=%s', 'out_id=%s', params=[client_json, out_id])
            if server_json:
                theme_info_model.update_table('server_json=%s', 'out_id=%s', params=[server_json, out_id])
        else:
            theme_total = theme_info_model.get_total()
            if not theme_name:
                return self.reponse_json_error("NoThemeName", "对不起，请输入主题名称")
            theme_info = ThemeInfo()
            theme_info.theme_name = theme_name
            theme_info.client_json = client_json
            theme_info.server_json = server_json
            theme_info.out_id = out_id
            if app_id != "":
                theme_info.app_id = app_id
                theme_info.is_private = 1
            theme_info.sort_index = int(theme_total) + 1
            theme_info.is_release = 1
            theme_info.create_date = self.get_now_datetime()
            theme_id = theme_info_model.add_entity(theme_info)
            if ver_no:
                theme_ver = ThemeVer()
                theme_ver.app_id = theme_info.app_id
                theme_ver.out_id = out_id
                theme_ver.theme_id = theme_id
                theme_ver.client_json = client_json
                theme_ver.ver_no = ver_no
                theme_ver.create_date = theme_info.create_date
                theme_ver_model.add_entity(theme_ver)

        return self.reponse_json_success()


class SkinSaveHandler(SevenBaseHandler):
    """
    :description: 保存皮肤
    """
    @filter_check_params("theme_out_id,skin_out_id")
    def post_async(self):
        """
        :description: 保存皮肤
        :param app_id：app_id
        :param skin_name：皮肤名称
        :param client_json：客户端内容json
        :param server_json：服务端内容json
        :param theme_out_id：样式外部id
        :param skin_out_id：皮肤外部id
        :return: 
        :last_editors: CaiYouBin
        """
        app_id = self.get_param("app_id")
        skin_name = self.get_param("skin_name")
        client_json = self.get_param("client_json")
        server_json = self.get_param("server_json")
        theme_out_id = self.get_param("theme_out_id")
        skin_out_id = self.get_param("skin_out_id")

        skin_info_model = SkinInfoModel(context=self)
        skin_info = skin_info_model.get_entity("out_id=%s", params=skin_out_id)
        if skin_info:
            if client_json:
                skin_info_model.update_table('client_json=%s', 'out_id=%s', params=[client_json, skin_out_id])
            if server_json:
                skin_info_model.update_table('server_json=%s', 'out_id=%s', params=[server_json, skin_out_id])
        else:
            skin_info_total = skin_info_model.get_total('theme_out_id=%s', params=theme_out_id)
            if not skin_name:
                return self.reponse_json_error("NoSkinName", "对不起，请输入皮肤名称")
            skin_info = SkinInfo()
            theme_info_model = ThemeInfoModel(context=self)
            theme_info = theme_info_model.get_entity("out_id=%s", params=theme_out_id)
            if not theme_info:
                return self.reponse_json_error("NoTheme", "没有找到对应主题")

            skin_info.skin_name = skin_name
            skin_info.client_json = client_json
            skin_info.server_json = server_json
            if app_id != "":
                skin_info.app_id = app_id
            skin_info.sort_index = skin_info_total + 1
            skin_info.theme_id = theme_info.id
            skin_info.create_date = self.get_now_datetime()
            skin_info.modify_date = self.get_now_datetime()
            skin_info.out_id = skin_out_id
            skin_info.theme_out_id = theme_out_id
            skin_id = skin_info_model.add_entity(skin_info)

        return self.reponse_json_success()


class ThemeInfoListHandler(SevenBaseHandler):
    """
    :description: 获取主题信息列表（前端工具上传）
    """
    def get_async(self):
        theme_info_model = ThemeInfoModel(context=self)
        theme_info_dict_list = theme_info_model.get_dict_list()
        if theme_info_dict_list:
            for theme_info_dict in theme_info_dict_list:
                if theme_info_dict["client_json"]:
                    theme_info_dict["client_json"] = self.json_loads(theme_info_dict["client_json"])
                if theme_info_dict["server_json"]:
                    theme_info_dict["server_json"] = self.json_loads(theme_info_dict["server_json"])

        return self.reponse_json_success(theme_info_dict_list)


class SkinInfoListHandler(SevenBaseHandler):
    """
    :description: 获取皮肤信息列表（前端工具上传）
    """
    @filter_check_params("theme_out_id")
    def get_async(self):
        theme_out_id = self.get_param("theme_out_id")
        skin_info_model = SkinInfoModel(context=self)
        skin_info_dict_list = skin_info_model.get_dict_list("theme_out_id=%s", params=[theme_out_id])
        if skin_info_dict_list:
            for skin_info_dict in skin_info_dict_list:
                if skin_info_dict["client_json"]:
                    skin_info_dict["client_json"] = self.json_loads(skin_info_dict["client_json"])
                if skin_info_dict["server_json"]:
                    skin_info_dict["server_json"] = self.json_loads(skin_info_dict["server_json"])

        return self.reponse_json_success(skin_info_dict_list)