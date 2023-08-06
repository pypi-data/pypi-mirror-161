# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-06-02 11:08:39
:LastEditTime: 2021-06-02 15:14:51
:LastEditors: HuangJingCan
:description: 订单相关
"""
from seven_cloudapp.handlers.seven_base import *
from seven_cloudapp.libs.customize.oss2help import *

from seven_cloudapp.models.seven_model import *
from seven_cloudapp.models.db_models.pay.pay_order_model import *
from seven_cloudapp.models.db_models.prize.prize_order_model import *
from seven_cloudapp.models.db_models.prize.prize_roster_model import *
from seven_cloudapp.models.db_models.endbox.endbox_order_model import *
from seven_cloudapp.models.db_models.ip.ip_series_model import *


class PayOrderListHandler(SevenBaseHandler):
    """
    :description: 用户购买订单
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 用户购买订单
        :param page_index：页索引
        :param page_size：页大小
        :param act_id：活动id
        :param user_open_id：用户唯一标识
        :param nick_name：用户昵称
        :param pay_date_start：订单支付时间开始
        :param pay_date_end：订单支付时间结束
        :return: 列表
        :last_editors: HuangJingCan
        """
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 10))
        act_id = int(self.get_param("act_id", 0))
        user_open_id = self.get_param("user_open_id")
        user_nick = self.get_param("nick_name")
        pay_date_start = self.get_param("pay_date_start")
        pay_date_end = self.get_param("pay_date_end")

        condition = "act_id=%s"
        params = [act_id]

        if user_open_id:
            condition += " AND open_id=%s"
            params.append(user_open_id)
        if user_nick:
            condition += " AND user_nick=%s"
            params.append(user_nick)
        if pay_date_start:
            condition += " AND pay_date>=%s"
            params.append(pay_date_start)
        if pay_date_end:
            condition += " AND pay_date<=%s"
            params.append(pay_date_end)

        page_list, total = PayOrderModel(context=self).get_dict_page_list("*", page_index, page_size, condition, "", "pay_date desc", params)

        page_info = PageInfo(page_index, page_size, total, page_list)

        return self.reponse_json_success(page_info)


class PrizeOrderListHandler(SevenBaseHandler):
    """
    :description: 用户奖品订单
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 用户奖品订单
        :param page_index：页索引
        :param page_size：页大小
        :param act_id：活动id
        :param order_no：订单号
        :param nick_name：用户昵称
        :param real_name：用户名字
        :param telephone：联系电话
        :param adress：收货地址
        :param order_status：订单状态
        :param create_date_start：订单创建时间开始
        :param create_date_end：订单创建时间结束
        :return: 列表
        :last_editors: HuangJingCan
        """
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 10))
        act_id = int(self.get_param("act_id", 0))
        order_no = self.get_param("order_no")
        user_nick = self.get_param("nick_name")
        real_name = self.get_param("real_name")
        telephone = self.get_param("telephone")
        adress = self.get_param("adress")
        order_status = int(self.get_param("order_status", -1))
        create_date_start = self.get_param("create_date_start")
        create_date_end = self.get_param("create_date_end")

        condition = "act_id=%s"
        params = [act_id]

        if order_no:
            condition += " AND order_no=%s"
            params.append(order_no)
        if user_nick:
            condition += " AND user_nick=%s"
            params.append(user_nick)
        if real_name:
            condition += " AND real_name=%s"
            params.append(real_name)
        if telephone:
            condition += " AND telephone=%s"
            params.append(telephone)
        if adress:
            adress = f"%{adress}%"
            condition += " AND adress LIKE %s"
            params.append(adress)
        if order_status >= 0:
            condition += " AND order_status=%s"
            params.append(order_status)
        if create_date_start:
            condition += " AND create_date>=%s"
            params.append(create_date_start)
        if create_date_end:
            condition += " AND create_date<=%s"
            params.append(create_date_end)

        page_list, total = PrizeOrderModel(context=self).get_dict_page_list("*", page_index, page_size, condition, "", "id desc", params)

        page_info = PageInfo(page_index, page_size, total, page_list)

        return self.reponse_json_success(page_info)


class PrizeRosterListHandler(SevenBaseHandler):
    """
    :description: 用户奖品列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 用户奖品列表
        :param page_index：页索引
        :param page_size：页大小
        :param act_id：活动id
        :param machine_id：机台id
        :param prize_order_id：奖品订单id
        :param prize_type：奖品类型（1实物2店铺商品3优惠券4参与奖5谢谢参与）
        :param nick_name：用户昵称
        :param is_submit：是否提交
        :param order_status：订单状态
        :param create_date_start：订单创建时间开始
        :param create_date_end：订单创建时间结束
        :param user_open_id：用户唯一标识
        :return: list
        :last_editors: HuangJingCan
        """
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 10))
        act_id = int(self.get_param("act_id", 0))
        machine_id = int(self.get_param("machine_id", 0))
        prize_order_id = int(self.get_param("prize_order_id", 0))
        user_nick = self.get_param("nick_name")
        is_submit = self.get_param("is_submit")
        prize_type = int(self.get_param("prize_type", 0))
        order_status = int(self.get_param("order_status", -1))
        create_date_start = self.get_param("create_date_start")
        create_date_end = self.get_param("create_date_end")
        user_open_id = self.get_param("user_open_id")

        condition = "act_id=%s"
        params = [act_id]

        if machine_id > 0:
            condition += " AND machine_id=%s"
            params.append(machine_id)
        if prize_order_id > 0:
            condition += " AND prize_order_id=%s"
            params.append(prize_order_id)
        if prize_type > 0:
            condition += " AND prize_type=%s"
            params.append(prize_type)
        if user_nick:
            condition += " AND user_nick=%s"
            params.append(user_nick)
        if is_submit and is_submit != "-1":
            if is_submit == "0":
                condition += " AND prize_order_id=0"
            else:
                condition += " AND prize_order_id>0"
        if order_status >= 0:
            condition += " AND order_status=%s"
            params.append(order_status)
        if create_date_start:
            condition += " AND create_date>=%s"
            params.append(create_date_start)
        if create_date_end:
            condition += " AND create_date<=%s"
            params.append(create_date_end)
        if user_open_id:
            condition += " AND open_id=%s"
            params.append(user_open_id)

        page_list, total = PrizeRosterModel(context=self).get_dict_page_list("*", page_index, page_size, condition, "", "id desc", params)

        page_info = PageInfo(page_index, page_size, total, page_list)

        return self.reponse_json_success(page_info)


class PrizeOrderStatusHandler(SevenBaseHandler):
    """
    :description: 更新用户奖品订单状态
    """
    @filter_check_params("prize_order_id,order_status")
    def post_async(self):
        """
        :description: 更新用户奖品订单状态
        :param prize_order_id：奖品订单id
        :param order_status：订单状态
        :param express_company：快递公司
        :param express_no：快递单号
        :return: reponse_json_success
        :last_editors: HuangJingCan
        """
        prize_order_id = int(self.get_param("prize_order_id", 0))
        order_status = int(self.get_param("order_status", 0))
        express_company = self.get_param("express_company")
        express_no = self.get_param("express_no")
        now_datetime = self.get_now_datetime()

        prize_order_model = PrizeOrderModel(context=self)
        prize_roster_model = PrizeRosterModel(context=self)

        if order_status == 1:
            update_sql = "order_status=1,express_company=%s,express_no=%s,deliver_date=%s,modify_date=%s"
            params = [express_company, express_no, now_datetime, now_datetime, prize_order_id]
            prize_order_model.update_table(update_sql, "id=%s", params)
            prize_roster_model.update_table("order_status=%s", "prize_order_id=%s", [order_status, prize_order_id])

            return self.reponse_json_success({"express_company": express_company, "express_no": express_no, "deliver_date": now_datetime})
        else:
            prize_order_model.update_table("order_status=%s,modify_date=%s", "id=%s", [order_status, now_datetime, prize_order_id])
            prize_roster_model.update_table("order_status=%s", "prize_order_id=%s", [order_status, prize_order_id])

            return self.reponse_json_success()


class PrizeOrderRemarksHandler(SevenBaseHandler):
    """
    :description: 更新用户奖品订单备注
    """
    @filter_check_params("prize_order_id")
    def post_async(self):
        """
        :description: 更新用户奖品订单备注
        :param prize_order_id：奖品订单id
        :param remarks：备注
        :return: 
        :last_editors: HuangJingCan
        """
        prize_order_id = int(self.get_param("prize_order_id", 0))
        remarks = self.get_param("remarks")

        PrizeOrderModel(context=self).update_table("remarks=%s", "id=%s", [remarks, prize_order_id])

        return self.reponse_json_success()


class PrizeOrderExportHandler(SevenBaseHandler):
    """
    :description: 导出订单
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 导出订单
        :param page_index：页索引
        :param page_size：页大小
        :param act_id：活动id
        :param order_no：订单号
        :param order_status：订单状态
        :param nick_name：用户昵称
        :param is_machine：是否机台
        :return str
        :last_editors: HuangJingCan
        """
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 500))
        act_id = int(self.get_param("act_id", 0))
        order_no = self.get_param("order_no")
        order_status = int(self.get_param("order_status", -1))
        user_nick = self.get_param("nick_name")
        real_name = self.get_param("real_name")
        # 0-没关联机台或者价格挡位，1-关联机台，2-关联价格挡位
        is_machine_gear = config.get_value("is_machine_gear", 0)

        condition = "act_id=%s"
        params = [act_id]

        if order_no != "":
            params.append(order_no)
            condition += " AND order_no=%s"
        if user_nick != "":
            params.append(user_nick)
            condition += " AND user_nick=%s"
        if real_name:
            condition += " AND real_name=%s"
            params.append(real_name)
        if order_status >= 0:
            params.append(order_status)
            condition += " AND order_status=%s"

        #奖品订单
        prize_order_list_dict, total = PrizeOrderModel(context=self).get_dict_page_list("*", page_index, page_size, condition, "", "create_date desc", params)

        result_data = []
        if len(prize_order_list_dict) > 0:
            prize_order_id_list = [prize_order["id"] for prize_order in prize_order_list_dict]
            prize_order_ids = str(prize_order_id_list).strip('[').strip(']')
            #订单奖品
            prize_roster_list = PrizeRosterModel(context=self).get_dict_list("prize_order_id in (" + prize_order_ids + ")", order_by="id desc")

            for prize_order in prize_order_list_dict:
                prize_roster_list_filter = [prize_roster for prize_roster in prize_roster_list if prize_roster["prize_order_id"] == prize_order["id"]]
                for prize_roster in prize_roster_list_filter:
                    data_row = {}
                    data_row["小程序订单号"] = prize_order["order_no"]
                    data_row["淘宝子订单号"] = prize_roster["order_no"]
                    data_row["淘宝名"] = prize_order["user_nick"]
                    if is_machine_gear in (1, 2):
                        data_row["盒子名称"] = prize_roster["machine_name"]
                        data_row["盒子价格"] = str(prize_roster["machine_price"])
                    data_row["奖品名称"] = prize_roster["prize_name"]
                    data_row["商家编码"] = prize_roster["goods_code"]
                    data_row["姓名"] = prize_order["real_name"]
                    data_row["手机号"] = prize_order["telephone"]
                    data_row["省份"] = prize_order["province"]
                    data_row["城市"] = prize_order["city"]
                    data_row["区县"] = prize_order["county"]
                    data_row["街道"] = prize_order["street"]
                    data_row["收货地址"] = prize_order["adress"]
                    data_row["物流单号"] = prize_order["express_no"]
                    data_row["物流公司"] = prize_order["express_company"]
                    if str(prize_order["deliver_date"]) == "1900-01-01 00:00:00":
                        data_row["发货时间"] = ""
                    else:
                        data_row["发货时间"] = str(prize_order["deliver_date"])
                    data_row["订单状态"] = self.get_status_name(prize_order["order_status"])
                    data_row["奖品价值"] = str(prize_roster["prize_price"])
                    data_row["奖品规格"] = prize_roster["properties_name"]
                    data_row["备注"] = prize_order["remarks"]

                    result_data.append(data_row)

        resource_path = ""
        if result_data:
            # if not os.path.exists("temp"):
            #     os.makedirs("temp")
            path = "temp/" + UUIDHelper.get_uuid() + ".xlsx"
            ExcelHelper.export(result_data, path)

            resource_path = OSS2Helper().upload("", path, "test", False)

            os.remove(path)

        return self.reponse_json_success(resource_path)


class PrizeOrderImportHandler(SevenBaseHandler):
    """
    :description: 订单导入
    """
    @filter_check_params("content,act_id")
    def post_async(self):
        """
        :description: 
        :param content：base64加密后的excel内容
        :param act_id：活动id
        :return 
        :last_editors: HuangJingCan
        """
        content = self.get_param("content")
        act_id = int(self.get_param("act_id", 0))

        if act_id <= 0:
            return self.reponse_json_error("NoAct", "对不起，无效活动，无法导入订单")

        # with open('E:\Project\Tandy\gao7\web\git\TaoBaoCloud\ppmt_ykmw\content.txt', 'r') as f:
        #     content = f.read()

        # 读取内容保存到本地
        # if not os.path.exists("temp"):
        #     os.makedirs("temp")
        # data = CryptoHelper.base64_decode(content)
        data = base64.decodebytes(content.encode())
        path = "temp/" + UUIDHelper.get_uuid() + ".xlsx"
        with open(path, 'ba') as f:
            buf = bytearray(data)
            f.write(buf)
        f.close()

        order_no_index = -1
        express_no_index = -1
        express_company_index = -1

        data = ExcelHelper.input(path)
        data_total = len(data)
        # 表格头部
        if data_total > 0:
            title_list = data[0]
            if "小程序订单号" in title_list:
                order_no_index = title_list.index("小程序订单号")
            if "物流单号" in title_list:
                express_no_index = title_list.index("物流单号")
            if "物流公司" in title_list:
                express_company_index = title_list.index("物流公司")

        if order_no_index == -1 or express_no_index == -1 or express_company_index == -1:
            return self.reponse_json_error("NoTitle", "对不起,缺少必要字段，无法导入订单")

        # 数据导入
        for i in range(1, data_total):
            row = data[i]
            order_no = row[order_no_index]
            express_no = row[express_no_index]
            express_company = row[express_company_index]

            if order_no and express_no and express_company:
                update_sql = "express_no=%s, express_company=%s, order_status=1, deliver_date=%s"
                params = [express_no, express_company, self.get_now_datetime(), order_no]
                # print(order_no + express_company)
                PrizeOrderModel(context=self).update_table(update_sql, "order_no=%s", params)
                PrizeRosterModel(context=self).update_table("order_status=1", "prize_order_no=%s", [order_no])

        os.remove(path)

        # self.logging_link_info(a)
        return self.reponse_json_success()


class PrizeRosterExportHandler(SevenBaseHandler):
    """
    :description: 批量奖品列表导出
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 批量奖品列表导出
        :param page_index：页索引
        :param page_size：页大小
        :param act_id：活动id
        :param order_no：订单号
        :param order_status：订单状态
        :param nick_name：用户昵称
        :param is_machine：是否机台
        :return str
        :last_editors: HuangJingCan
        """
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 500))
        act_id = self.get_param("act_id")
        order_no = self.get_param("order_no")
        order_status = int(self.get_param("order_status", -1))
        user_nick = self.get_param("nick_name")
        prize_type = int(self.get_param("prize_type", 0))
        # 0-没关联机台或者价格挡位，1-关联机台，2-关联价格挡位
        is_machine_gear = config.get_value("is_machine_gear", 0)

        condition = "act_id=%s"
        params = [act_id]

        if order_no != "":
            params.append(order_no)
            condition += " AND order_no=%s"
        if user_nick != "":
            params.append(user_nick)
            condition += " AND user_nick=%s"
        if order_status >= 0:
            params.append(order_status)
            condition += " AND order_status=%s"
        if prize_type > 0:
            params.append(prize_type)
            condition += " AND prize_type=%s"

        #奖品订单
        prize_roster_list, total = PrizeRosterModel(context=self).get_dict_page_list("*", page_index, page_size, condition, order_by="id desc", params=params)

        #订单奖品
        result_data = []
        for prize_roster in prize_roster_list:
            data_row = {}
            data_row["行为编号"] = prize_roster["id"]
            data_row["淘宝子订单号"] = prize_roster["order_no"]
            data_row["淘宝名"] = prize_roster["user_nick"]
            if is_machine_gear in (1, 2):
                data_row["盒子名称"] = prize_roster["machine_name"]
                data_row["盒子价格"] = str(prize_roster["machine_price"])
            data_row["奖品名称"] = prize_roster["prize_name"]
            data_row["奖品价值"] = str(prize_roster["prize_price"])
            data_row["SKU"] = prize_roster["properties_name"]
            data_row["获得时间"] = prize_roster["create_date"]
            if prize_roster["prize_order_id"] == 0:
                data_row["状态"] = "未下单"
            else:
                data_row["状态"] = "已下单"

            result_data.append(data_row)

        resource_path = ""
        if result_data:
            path = "temp/" + UUIDHelper.get_uuid() + ".xlsx"
            ExcelHelper.export(result_data, path)

            resource_path = OSS2Helper().upload("", path, config.get_value("oss_folder"), False)

            os.remove(path)

        return self.reponse_json_success(resource_path)


class EndBoxOrderListHandler(SevenBaseHandler):
    """
    :description: 端盒订单列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 端盒订单列表
        :param act_id：活动id
        :param order_no：订单编号
        :param nick_name：淘宝名称
        :param create_date_start：开始时间
        :param create_date_end：结束时间
        :return: 
        :last_editors: HuangJianYi
        """
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 10))
        act_id = int(self.get_param("act_id", 0))
        order_no = self.get_param("order_no")
        user_nick = self.get_param("nick_name")
        create_date_start = self.get_param("create_date_start")
        create_date_end = self.get_param("create_date_end")

        condition = "act_id=%s"
        params = [act_id]

        if user_nick:
            condition += " AND user_nick=%s"
            params.append(user_nick)
        if create_date_start:
            condition += " AND create_date>=%s"
            params.append(create_date_start)
        if create_date_end:
            condition += " AND create_date<=%s"
            params.append(create_date_end)

        page_list, total = EndboxOrderModel(context=self).get_dict_page_list("*", page_index, page_size, condition, order_by="id desc", params=params)

        if page_list:
            ip_series_dict_list = IpSeriesModel(context=self).get_dict_list(SevenHelper.get_condition_by_id_list("id", [i['series_id'] for i in page_list]))
            new_dict_list = SevenHelper.merge_dict_list(page_list, "series_id", ip_series_dict_list, "id", "series_name")
            page_info = PageInfo(page_index, page_size, total, new_dict_list)
            return self.reponse_json_success(page_info)
        else:
            return self.reponse_json_success(PageInfo(page_index, page_size, total, page_list))