# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-06-02 13:44:17
:LastEditTime: 2021-04-16 15:48:43
:LastEditors: HuangJingCan
:description: 奖品相关
"""
from seven_cloudapp.handlers.seven_base import *

from seven_cloudapp.models.enum import OperationType
from seven_cloudapp.models.seven_model import PageInfo
from seven_cloudapp.models.throw_model import *
from seven_cloudapp.models.db_models.act.act_info_model import *
from seven_cloudapp.models.db_models.act.act_prize_model import *
from seven_cloudapp.models.db_models.prize.prize_roster_model import *
from seven_cloudapp.models.db_models.throw.throw_goods_model import *


class PrizeListHandler(SevenBaseHandler):
    """
    :description: 奖品列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 奖品列表
        :param page_index：页索引
        :param page_size：页大小
        :param act_id：活动id
        :param ascription_type：奖品归属（0-活动奖品1-任务奖品）
        :return: PageInfo
        :last_editors: HuangJingCan
        """
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 10))
        act_id = int(self.get_param("act_id", 0))
        ascription_type = int(self.get_param("ascription_type", 0))

        condition = "act_id=%s AND ascription_type=%s"
        order_by = "sort_index desc"
        params = [act_id, ascription_type]

        if act_id <= 0:
            return self.reponse_json_error_params()

        act_prize_model = ActPrizeModel(context=self)

        prize_all_count = 0
        prize_surplus_count = 0
        prize_lottery_count = 0
        prize_release_count = 0
        sum_probability = {'probability': 0}

        if ascription_type == 0:
            # 奖品总件数
            prize_all_count = act_prize_model.get_total(condition, params=params)
            # 库存不足奖品件数
            prize_surplus_count = act_prize_model.get_total(condition + " AND surplus=0", params=params)
            # 可被抽中奖品件数
            prize_lottery_count = act_prize_model.get_total(condition + " AND probability>0 AND surplus>0 AND is_release=1", params=params)
            # 上架奖品件数
            prize_release_count = act_prize_model.get_total(condition + " AND is_release=1", params=params)
            #奖品总权重
            sum_probability = act_prize_model.get_dict(condition + " AND is_release=1", field="sum(probability) as probability", params=params)

        page_list, total = act_prize_model.get_dict_page_list("*", page_index, page_size, condition, "", order_by, params)

        if ascription_type == 0:
            #强制命中信息
            must_prize_list = [must_prize for must_prize in page_list if must_prize["force_count"] > 0]
            prize_roster_model = PrizeRosterModel(context=self)
            prize_roster_total = prize_roster_model.get_total("act_id=%s", params=act_id)
            for must_item in must_prize_list:
                page_total = int(prize_roster_total / must_item["force_count"])
                prize_roster_after_list = prize_roster_model.get_dict_list("act_id=%s", "", "id asc", str(page_total * must_item["force_count"]) + "," + str((page_total * must_item["force_count"]) + must_item["force_count"]), params=act_id)
                area_must_count = must_item["force_count"]
                is_exist = 0
                if (len(prize_roster_after_list) > 0):
                    prize_roster_after_list.reverse()
                    for roster_after_item in prize_roster_after_list:
                        if roster_after_item["prize_id"] == must_item["id"]:
                            is_exist = 1
                            area_must_count = must_item["force_count"] - len(prize_roster_after_list)
                            sum_probability["probability"] = int(sum_probability["probability"]) - must_item["probability"]
                            break
                        else:
                            area_must_count += -1
                must_item["area_must_count"] = area_must_count
                must_item["is_area_selected"] = is_exist
            page_list = SevenHelper.merge_dict_list(page_list, "id", must_prize_list, "id", "area_must_count,is_area_selected")

        for page in page_list:
            # page["prize_detail"] = ast.literal_eval(page["prize_detail"]) if page["prize_detail"] else []
            page["prize_detail"] = self.json_loads(page["prize_detail"]) if page["prize_detail"] else []
            page["goods_code_list"] = self.json_loads(page["goods_code_list"]) if page["goods_code_list"] else []
            page["sku_detail"] = self.json_loads(page["sku_detail"]) if page["sku_detail"] else []

        page_info = PageInfo(page_index, page_size, total, page_list)

        page_info.prize_all_count = prize_all_count
        page_info.prize_surplus_count = prize_surplus_count
        page_info.prize_lottery_count = prize_lottery_count
        page_info.prize_release_count = prize_release_count
        page_info.prize_sum_probability = int(sum_probability["probability"]) if sum_probability["probability"] else 0

        return self.reponse_json_success(page_info)


class PrizeHandler(SevenBaseHandler):
    """
    :description: 奖品保存
    """
    @filter_check_params("app_id,act_id")
    def post_async(self):
        """
        :description: 奖品保存
        :param prize_id：奖品id
        :param prize_type 奖品类型（1实物2店铺商品3优惠券4参与奖）
        :return: reponse_json_success
        :last_editors: LaiKaiXiang
        """
        prize_id = int(self.get_param("prize_id", 0))
        act_id = int(self.get_param("act_id", 0))
        award_id = self.get_param("award_id")
        app_id = self.get_param("app_id")
        owner_open_id = self.get_param("owner_open_id")
        machine_id = int(self.get_param("machine_id", 0))
        ascription_type = int(self.get_param("ascription_type", 0))
        prize_name = self.get_param("prize_name")
        prize_title = self.get_param("prize_title")
        prize_pic = self.get_param("prize_pic")
        prize_detail = self.get_param("prize_detail")
        goods_id = int(self.get_param("goods_id", 0))
        goods_code = self.get_param("goods_code")
        goods_code_list = self.get_param("goods_code_list")
        coupon_type = int(self.get_param("coupon_type", 0))
        right_ename = self.get_param("right_ename")
        pool_id = self.get_param("pool_id")
        coupon_start_date = self.get_param("coupon_start_date")
        coupon_end_date = self.get_param("coupon_end_date")
        prize_type = int(self.get_param("prize_type", 0))
        prize_price = self.get_param("prize_price")
        probability = int(self.get_param("probability", 0))
        surplus = int(self.get_param("surplus", 0))
        is_surplus = int(self.get_param("is_surplus", 0))
        is_prize_notice = int(self.get_param("is_prize_notice", 1))
        prize_limit = int(self.get_param("prize_limit", 0))
        prize_total = int(self.get_param("prize_total", 0))
        lottery_type = int(self.get_param("lottery_type", 1))
        force_count = int(self.get_param("force_count", 0))
        tag_name = self.get_param("tag_name")
        tag_id = int(self.get_param("tag_id", 0))
        # hand_out = int(self.get_param("hand_out", 0))
        is_sku = int(self.get_param("is_sku", 0))
        sort_index = int(self.get_param("sort_index", 0))
        is_release = int(self.get_param("is_release", 1))
        sku_detail = self.get_param("sku_detail")
        lottery_sum = int(self.get_param("lottery_sum", 0))

        # self.logging_link_info(self.request.uri + "-PrizeHandler-保存奖品" + str(self.request_params))
        if act_id <= 0:
            return self.reponse_json_error_params()

        act_prize_model = ActPrizeModel(context=self)
        act_prize = None
        if prize_id > 0:
            act_prize = act_prize_model.get_entity_by_id(prize_id)

        if not act_prize:
            act_prize = ActPrize()

        old_act_prize = deepcopy(act_prize)

        act_prize.act_id = act_id
        act_prize.award_id = award_id
        act_prize.app_id = app_id
        act_prize.owner_open_id = owner_open_id
        act_prize.machine_id = machine_id
        act_prize.ascription_type = ascription_type
        act_prize.prize_name = prize_name
        act_prize.prize_title = prize_title
        act_prize.prize_pic = prize_pic
        act_prize.prize_detail = prize_detail if prize_detail != "" else []
        act_prize.goods_id = goods_id
        act_prize.goods_code = goods_code
        act_prize.goods_code_list = goods_code_list if goods_code_list != "" else []
        # 奖品类型为优惠券时
        if prize_type == 3:
            act_prize.coupon_type = coupon_type
            act_prize.right_ename = right_ename
            act_prize.pool_id = pool_id
            act_prize.coupon_start_date = coupon_start_date if coupon_start_date else "1900-01-01 00:00:00"
            act_prize.coupon_end_date = coupon_end_date if coupon_end_date else "2900-01-01 00:00:00"
        act_prize.prize_type = prize_type
        act_prize.prize_price = prize_price
        act_prize.probability = probability
        act_prize.is_surplus = is_surplus
        act_prize.is_prize_notice = is_prize_notice
        act_prize.prize_limit = prize_limit
        act_prize.lottery_type = lottery_type
        act_prize.force_count = force_count
        act_prize.tag_name = tag_name
        act_prize.tag_id = tag_id
        # act_prize.hand_out = hand_out
        act_prize.is_sku = is_sku
        act_prize.sort_index = sort_index
        act_prize.is_release = is_release
        act_prize.sku_detail = sku_detail if sku_detail != "" else {}
        act_prize.lottery_sum = lottery_sum
        act_prize.modify_date = self.get_now_datetime()

        # 奖品类型为参与奖时
        surplus = 9999 if prize_type == 4 else surplus
        prize_total = 9999 if prize_type == 4 else prize_total

        if prize_id > 0:
            if surplus > 0:
                act_prize.surplus = surplus
            self.create_operation_log(OperationType.update.value, "act_prize_tb", "PrizeHandler", None, act_prize)
            act_prize_model.update_entity(act_prize)
            if surplus == 0:
                operate_num = prize_total - act_prize.prize_total
                act_prize_model.update_table(f"surplus=surplus+{operate_num},prize_total=prize_total+{operate_num}", "id=%s", act_prize.id)
            # ThrowModel(context=self).throw_goods_add(prize_id, act_prize.app_id, act_prize.act_id, act_prize.goods_id, old_act_prize.act_id, old_act_prize.goods_id, self.get_now_datetime())
        else:
            act_prize.create_date = act_prize.modify_date
            act_prize.surplus = surplus if surplus > 0 else prize_total
            act_prize.prize_total = prize_total
            act_prize.id = act_prize_model.add_entity(act_prize)
            self.create_operation_log(OperationType.add.value, "act_prize_tb", "PrizeHandler", old_act_prize, act_prize)
            # ThrowModel(context=self).throw_goods_add(prize_id, act_prize.app_id, act_prize.act_id, act_prize.goods_id, 0, 0, self.get_now_datetime())

        return self.reponse_json_success(act_prize.id)


class PrizeDelHandler(SevenBaseHandler):
    """
    :description: 删除奖品
    """
    @filter_check_params("prize_id")
    def get_async(self):
        """
        :description: 删除奖品
        :param prize_id：奖品id
        :return: reponse_json_success
        :last_editors: HuangJingCan
        """
        prize_id = int(self.get_param("prize_id", 0))

        if prize_id <= 0:
            return self.reponse_json_error_params()

        ActPrizeModel(context=self).del_entity("id=%s", prize_id)

        self.create_operation_log(OperationType.delete.value, "act_prize_tb", "PrizeDelHandler", None, prize_id)

        return self.reponse_json_success()


class PrizeReleaseHandler(SevenBaseHandler):
    """
    :description: 上下架奖品
    """
    @filter_check_params("prize_id")
    def get_async(self):
        """
        :description: 上下架奖品
        :param prize_id：奖品id
        :param is_release：0-下架，1-上架
        :return: 
        :last_editors: HuangJingCan
        """
        prize_id = int(self.get_param("prize_id", 0))
        is_release = int(self.get_param("is_release", 0))
        modify_date = self.get_now_datetime()

        if prize_id <= 0:
            return self.reponse_json_error_params()

        ActPrizeModel(context=self).update_table("is_release=%s,modify_date=%s", "id=%s", [is_release, modify_date, prize_id])

        return self.reponse_json_success()


class CheckRightEnameHandler(SevenBaseHandler):
    """
    :description: 判断奖品里面有没有添加这张优惠券
    """
    @filter_check_params("right_ename")
    def get_async(self):
        """
        :description: 判断奖品里面有没有添加这张优惠券
        :param right_ename：优惠券标识
        :return reponse_json_success
        :last_editors: HuangJingCan
        """
        right_ename = self.get_param("right_ename")

        count = ActPrizeModel(context=self).get_total("right_ename=%s", params=right_ename)
        if count > 0:
            return self.reponse_json_error()

        return self.reponse_json_success()