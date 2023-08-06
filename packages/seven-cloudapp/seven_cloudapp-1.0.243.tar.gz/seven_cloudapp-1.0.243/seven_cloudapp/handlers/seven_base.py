# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-05-12 20:11:48
@LastEditTime: 2022-02-22 16:35:16
@LastEditors: HuangJianYi
:description: SevenBaseHandler
"""
import ast
import random
import decimal
from copy import deepcopy
from asq.initiators import query

from seven_framework.redis import *
from seven_framework.web_tornado.base_handler.base_api_handler import *

from seven_cloudapp.libs.customize.seven_helper import *

from seven_cloudapp.models.taobao_model import *
from seven_cloudapp.models.db_models.operation.operation_log_model import *
from seven_cloudapp.models.db_models.user.user_info_model import *
from seven_cloudapp.models.db_models.app.app_info_model import *
from seven_cloudapp.models.db_models.middler.middler_product_model import *
from seven_cloudapp.models.db_models.role.role_power_model import *
from seven_cloudapp.models.db_models.role.role_user_model import *


class SevenBaseHandler(BaseApiHandler):
    """
    :description: SevenBaseHandler
    """
    def prepare(self):
        """
        :Description: 置于任何请求方法前被调用(请勿重写此函数,可重写prepare_ext)
        :last_editors: HuangJingCan
        """
        if self.__class__.__name__ == "IndexHandler":
            return

        dict_par = {}
        dict_par["open_id"] = self.get_taobao_param().open_id
        dict_par["nick_name"] = self.get_taobao_param().user_nick
        dict_par["app_id"] = self.get_param("app_id")
        if not dict_par["app_id"]:
            dict_par["app_id"] = self.get_taobao_param().source_app_id

        # 标记日志请求关联
        self._build_http_log(dict_par)

    def options_async(self):
        self.reponse_json_success()

    def check_xsrf_cookie(self):
        return

    def json_dumps(self, rep_dic):
        """
        :description: 将字典转化为字符串
        :param rep_dic：字典对象
        :return: str
        :last_editors: HuangJingCan
        """
        if isinstance(rep_dic, str):
            rep_dic = ast.literal_eval(rep_dic)
        if hasattr(rep_dic, '__dict__'):
            rep_dic = rep_dic.__dict__
        return json.dumps(rep_dic, ensure_ascii=False, cls=JsonEncoder, default=lambda x: (x.__dict__ if not isinstance(x, datetime.datetime) else datetime.datetime.strftime(x, '%Y-%m-%d %H:%M:%S')) if not isinstance(x, decimal.Decimal) else float(x), sort_keys=False, indent=2)

    def json_loads(self, rep_str):
        """
        :description: 将字符串转化为字典
        :param rep_str：str
        :return: dict
        :last_editors: HuangJingCan
        """
        try:
            return json.loads(rep_str)
        except Exception as ex:
            return json.loads(self.json_dumps(rep_str))

    def reponse_custom(self, rep_dic):
        """
        :description: 输出公共json模型
        :param rep_dic: 字典类型数据
        :return: 将dumps后的数据字符串返回给客户端
        :last_editors: HuangJingCan
        """
        self.http_reponse(self.json_dumps(rep_dic))

    def reponse_common(self, success=True, data=None, error_code="", error_message=""):
        """
        :description: 输出公共json模型
        :param success: 布尔值，表示本次调用是否成功
        :param data: 类型不限，调用成功（success为true）时，服务端返回的数据
        :param errorCode: 字符串，调用失败（success为false）时，服务端返回的错误码
        :param errorMessage: 字符串，调用失败（success为false）时，服务端返回的错误信息
        :return: 将dumps后的数据字符串返回给客户端
        :last_editors: HuangJingCan
        """
        if hasattr(data, '__dict__'):
            data = data.__dict__
        template_value = {}
        template_value['success'] = success
        template_value['data'] = data
        template_value['error_code'] = error_code
        template_value['error_message'] = error_message

        rep_dic = {}
        rep_dic['success'] = True
        rep_dic['data'] = template_value

        log_extra_dict = {}
        log_extra_dict["is_success"] = 1
        if success == False:
            log_extra_dict["is_success"] = 0

        self.http_reponse(self.json_dumps(rep_dic), log_extra_dict)

    def reponse_json_success(self, data=None):
        """
        :description: 通用成功返回json结构
        :param data: 返回结果对象，即为数组，字典
        :return: 将dumps后的数据字符串返回给客户端
        :last_editors: HuangJingCan
        """
        self.reponse_common(data=data)

    def reponse_json_error(self, error_code="", error_message="", data=None, log_type=0):
        """
        :description: 通用错误返回json结构
        :param errorCode: 字符串，调用失败（success为false）时，服务端返回的错误码
        :param errorMessage: 字符串，调用失败（success为false）时，服务端返回的错误信息
        :param data: 返回结果对象，即为数组，字典
        :param log_type: 日志记录类型（0-不记录，1-info，2-error）
        :return: 将dumps后的数据字符串返回给客户端
        :last_editors: HuangJingCan
        """
        if log_type == 1:
            self.logging_link_info(f"{error_code}\n{error_message}\n{data}\n{self.request}")
        elif log_type == 2:
            self.logging_link_error(f"{error_code}\n{error_message}\n{data}\n{self.request}")
        self.reponse_common(False, data, error_code, error_message)

    def reponse_json_error_params(self):
        """
        :description: 通用参数错误返回json结构
        :param desc: 返错误描述
        :return: 将dumps后的数据字符串返回给客户端
        :last_editors: ChenXiaolei
        """
        self.reponse_common(False, None, "params error", "参数错误")

    def return_dict_error(self, error_code="", error_message=""):
        """
        :description: 返回error信息字典模型
        :param errorCode: 字符串，服务端返回的错误码
        :param errorMessage: 字符串，服务端返回的错误信息
        :return: dict
        :last_editors: HuangJingCan
        """
        rep_dic = {}
        rep_dic['error_code'] = error_code
        rep_dic['error_message'] = error_message

        self.logging_link_error(f"{error_code}\n{error_message}\n{self.request}")

        return rep_dic

    def redis_init(self, db=None, config_dict=None, decode_responses=False):
        """
        :description: redis初始化
        :return: redis_cli
        :last_editors: HuangJingCan
        """
        host = config.get_value("redis")["host"]
        port = config.get_value("redis")["port"]
        if not db:
            db = config.get_value("redis")["db"]
        password = config.get_value("redis")["password"]
        redis_cli = RedisHelper.redis_init(host, port, db, password, config_dict, decode_responses)
        return redis_cli

    def get_taobao_param(self):
        """
        :description: 获取淘宝上下文参数
        :return: TaoBaoParam
        :last_editors: HuangJingCan
        """
        app_key = self.get_param("app_key")
        user_nick = self.get_param("user_nick")
        open_id = self.get_param("open_id")
        env = self.get_param("env")
        mini_app_id = self.get_param("mini_app_id")
        access_token = self.get_param("access_token")
        sign = self.get_param("sign")
        mix_nick = self.get_param("mix_nick")
        user_id = self.get_param("user_id")
        main_user_id = self.get_param("main_user_id")
        source_app_id = self.get_param("source_app_id")
        request_id = self.get_param("request_id")

        #region 指定测试账号和小程序,用于在IDE上测试(前端通过source_app_id关联数据,后端通过user_nick关联数据)
        if source_app_id == config.get_value("client_template_id"):
            #前端（在IDE上返回前端模板id，在千牛上返回正确的id）
            source_app_id = config.get_value("test_source_app_id")
        if source_app_id == "":
            #后端（在IDE上返回空，在千牛上返回后端模板ids）
            source_app_id = config.get_value("test_source_app_id")
            user_nick = config.get_value("test_user_nick")
            open_id = config.get_value("test_open_id")
        #endregion

        info = TaoBaoParam()
        info.app_key = app_key
        info.user_nick = user_nick
        info.open_id = open_id
        info.env = env
        info.mini_app_id = mini_app_id
        info.access_token = access_token
        info.sign = sign
        info.mix_nick = mix_nick
        info.user_id = user_id
        info.main_user_id = main_user_id
        info.source_app_id = source_app_id
        info.request_id = request_id

        return info

    def get_app_id(self):
        """
        :description: 获取app_id
        :param self
        :return str
        :last_editors: HuangJingCan
        """
        app_id = self.get_param("app_id")
        if app_id == "":
            user_nick = self.get_taobao_param().user_nick
            if user_nick:
                store_user_nick = user_nick.split(':')[0]
                if store_user_nick:
                    dict_app_id = AppInfoModel(context=self).get_dict("store_user_nick=%s", field="app_id", params=store_user_nick)
                    if dict_app_id:
                        app_id = dict_app_id["app_id"]
        return app_id

    def create_order_id(self, ran=5):
        """
        :description: 生成订单号
        :param ran：随机数位数，默认5位随机数（0-5）
        :return: 25位的订单号
        :last_editors: HuangJingCan
        """
        ran_num = ""
        if ran == 1:
            ran_num = random.randint(0, 9)
        elif ran == 2:
            ran_num = random.randint(10, 99)
        elif ran == 3:
            ran_num = random.randint(100, 999)
        elif ran == 4:
            ran_num = random.randint(1000, 9999)
        elif ran == 5:
            ran_num = random.randint(10000, 99999)
        # cur_time = TimeHelper.get_now_format_time('%Y%m%d%H%M%S%f')
        cur_time = TimeHelper.get_now_timestamp(True)
        order_id = str(cur_time) + str(ran_num)
        return order_id

    def get_now_datetime(self):
        """
        :description: 获取当前时间
        :return: str
        :last_editors: HuangJingCan
        """
        add_hours = config.get_value("add_hours", 0)
        return TimeHelper.add_hours_by_format_time(hour=add_hours)

    def create_operation_log(self, operation_type=1, model_name="", handler_name="", detail=None, update_detail=None):
        """
        :description: 创建操作日志
        :param operation_type：操作类型：1-add，2-update，3-delete
        :param model_name：模块或表名称
        :param handler_name：handler名称
        :param detail：当前信息
        :param update_detail：更新之后的信息
        :return: 
        :last_editors: HuangJingCan
        """
        operation_log = OperationLog()
        operation_log_model = OperationLogModel(context=self)

        operation_log.user_nick = self.get_taobao_param().user_nick
        operation_log.app_id = self.get_taobao_param().source_app_id
        operation_log.act_id = int(self.get_param("act_id", 0))
        operation_log.open_id = self.get_taobao_param().open_id
        operation_log.request_params = self.request_params
        operation_log.method = self.request.method
        operation_log.protocol = self.request.protocol
        operation_log.request_host = self.request.host
        operation_log.request_uri = self.request.uri
        operation_log.remote_ip = self.get_remote_ip()
        operation_log.create_date = TimeHelper.get_now_format_time()
        operation_log.operation_type = operation_type
        operation_log.model_name = model_name
        operation_log.handler_name = handler_name
        operation_log.detail = detail
        operation_log.update_detail = update_detail

        if isinstance(operation_log.request_params, dict):
            operation_log.request_params = self.json_dumps(operation_log.request_params)
        if isinstance(detail, dict):
            operation_log.detail = self.json_dumps(detail)
        if isinstance(update_detail, dict):
            operation_log.update_detail = self.json_dumps(update_detail)

        operation_log_model.add_entity(operation_log)

    def get_is_test(self):
        """
        :description: 判断是否本地测试
        :return: bool
        :last_editors: HuangJianYi
        """
        if self.get_taobao_param().env != "online":
            return True
        return False

    def check_post(self, redis_key, expire=1):
        """
         :description: 请求太频繁校验
         :return: bool
         :last_editors: HuangJianYi
         """
        redis_init = self.redis_init()
        post_value = redis_init.incr(redis_key,1)
        redis_init.expire(redis_key,expire)
        if post_value > 1:
            return False
        return True

    def check_lpush(self, queue_name, value, limitNum=100):
        """
         :description: 入队列校验
         :return: bool
         :last_editors: HuangJianYi
         """
        list_len = self.redis_init().llen(queue_name)
        if int(list_len) >= int(limitNum):
            return False
        self.redis_init().lpush(queue_name, json.dumps(value))
        return True

    def lpop(self, queue_name):
        """
         :description: 出队列
         :param queue_name：队列名称
         :return: 
         :last_editors: HuangJianYi
         """
        result = self.redis_init().lpop(queue_name)
        return result

    def acquire_lock(self, lock_name, acquire_time=10, time_out=10):
        """
        :description: 获取一个分布式锁
        :param lock_name：锁定名称
        :param acquire_time: 客户端等待获取锁的时间
        :param time_out: 锁的超时时间
        :return bool
        :last_editors: HuangJianYi
        """
        identifier = str(uuid.uuid4())
        end = time.time() + acquire_time
        lock = "lock:" + lock_name
        while time.time() < end:
            if self.redis_init().setnx(lock, identifier):
                # 给锁设置超时时间, 防止进程崩溃导致其他进程无法获取锁
                self.redis_init().expire(lock, time_out)
                return identifier
            if self.redis_init().ttl(lock) == -1:
                self.redis_init().expire(lock, time_out)
            time.sleep(0.001)
        return False

    def release_lock(self, lock_name, identifier):
        """
        :description: 释放一个锁
        :param lock_name：锁定名称
        :param identifier: identifier
        :return bool
        :last_editors: HuangJianYi
        """
        lock = "lock:" + lock_name
        pip = self.redis_init().pipeline(True)
        while True:
            try:
                pip.watch(lock)
                lock_value = self.redis_init().get(lock)
                if not lock_value:
                    return True
                if lock_value.decode() == identifier:
                    pip.multi()
                    pip.delete(lock)
                    pip.execute()
                    return True
                pip.unwatch()
                break
            except redis.excetions.WacthcError:
                pass
        return False

    def random_weight(self, random_prize_dict_list):
        """
        :description:  根据权重算法获取商品
        :param random_prize_dict_list：权重列表
        :return: str
        :last_editors: HuangJianYi
        """
        total = sum(random_prize_dict_list.values())  # 权重求和
        ra = random.uniform(0, total)  # 在0与权重和之前获取一个随机数
        curr_sum = 0
        ret = None
        keys = random_prize_dict_list.keys()
        for k in keys:
            curr_sum += random_prize_dict_list[k]  # 在遍历中，累加当前权重值
            if ra <= curr_sum:  # 当随机数<=当前权重和时，返回权重key
                ret = k
                break
        return ret

    def get_status_name(self, status_id):
        """
        :description: 获取状态
        :param status_id：状态id
        :return str
        :last_editors: HuangJingCan
        """
        if status_id == 0:
            return "未发货"
        if status_id == 1:
            return "已发货"
        if status_id == 2:
            return "不予发货"
        if status_id == 3:
            return "订单同步失败"

    def get_date_list(self, start_date, end_date):
        """
        :description: 两个日期之间的日期列表
        :param start_date：开始日期
        :param end_date：结束日期
        :return: list
        :last_editors: CaiYouBin
        """
        if not start_date or not end_date:
            return []

        datestart = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        dateend = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')

        date_list = []

        while datestart < dateend:
            date_list.append(datestart.strftime('%Y-%m-%d'))
            datestart += datetime.timedelta(days=1)
        return date_list

    def get_online_url(self, act_id, app_id, machine_id=""):
        """
        :description: 获取online_url
        :param act_id:活动id
        :param app_id:app_id
        :param machine_id:机台id
        :param page:跳转的首页地址pages/index/index
        :return str
        :last_editors: HuangJingCan
        """
        page_index = ""
        page = config.get_value("page_index")
        if page:
            page_index = "&page=" + CodingHelper.url_encode(page)
        query = CodingHelper.url_encode(f"actid={act_id}")
        if machine_id:
            query = CodingHelper.url_encode(f"actid={act_id}&machine_id={machine_id}")
        online_url = f"https://m.duanqu.com/?_ariver_appid={app_id}{page_index}&query={query}"
        return online_url

    def get_live_url(self, app_id):
        """
        :description: 获取live_url
        :param app_id:app_id
        :return str
        :last_editors: HuangJingCan
        """
        live_url = f"https://market.m.taobao.com/app/taefed/shopping-delivery-wapp/index.html#/putin?mainKey=form&appId={app_id}"
        return live_url

    def get_app_key_secret(self):
        """
        :description: 获取app_key和app_secret
        :param 
        :return app_key, app_secret
        :last_editors: HuangJingCan
        """
        request_app_key = int(self.get_param("app_key", 0))
        app_key = config.get_value("app_key")
        app_secret = config.get_value("app_secret")

        if request_app_key not in (0, app_key):
            dict_product = MiddlerProductModel(context=self).get_dict("app_key=%s", field="app_secret", params=request_app_key)
            if dict_product:
                app_key = request_app_key
                app_secret = dict_product["app_secret"]

        return app_key, app_secret

    def get_currency_type_name(self, currency_type):
        """
        :description: 获取抽奖货币类型名称
        :param currency_type:来源类型：1-购买2-任务3-手动配置4抽奖
        :return str
        :last_editors: HuangJingCan
        """
        currency_type = int(currency_type)
        if currency_type == 1:
            return "抽奖次数"
        if currency_type == 2:
            return "积分"
        if currency_type == 3:
            return "抽奖码"
        if currency_type == 4:
            return "会员积分"
        return ""

    def get_power_menu(self, app_id):
        """
        :description: 获取权限菜单列表
        :param {*}
        :return {*}
        :last_editors: HuangJingCan
        """
        now_datetime = self.get_now_datetime()
        data = []
        if not app_id:
            return data
        role_user_model = RoleUserModel(context=self)
        role_power_model = RolePowerModel(context=self)
        role_user_dict_list = role_user_model.get_dict_list("app_id=%s and is_power=1 and %s>=service_date_start and %s<=service_date_end", params=[app_id, now_datetime, now_datetime])
        if len(role_user_dict_list) <= 0:
            return data
        role_id_list = query(role_user_dict_list).where(lambda x: x["role_id"] > 0).select(lambda x: x["role_id"]).to_list()
        if len(role_id_list) <= 0:
            return data
        data = role_power_model.get_dict_list(SevenHelper.get_condition_by_id_list("role_id", role_id_list))
        if len(data) > 0:
            # data = query(data).select(lambda x: {'role_id': x["role_id"], 'menu_id': x["menu_id"]}).to_list()
            data = query(data).select(lambda x: str(x["menu_id"])).to_list()
            data = list(set(data))
        return data

    def lottery_algorithm_chance(self, prize_list):
        """
        :description: 抽奖算法（概率）
        :param prize_list:奖品列表
        :return: 中奖的奖品
        :last_editors: HuangJianYi
        """
        init_value = 0.00
        probability_list = []
        for prize in prize_list:
            current_prize = prize
            current_prize["start_probability"] = init_value
            current_prize["end_probability"] = init_value + float(prize["chance"])
            probability_list.append(current_prize)
            init_value = init_value + float(prize["chance"])
        prize_index = random.uniform(0.00, init_value)
        for prize in probability_list:
            if (prize["start_probability"] <= prize_index and prize_index < prize["end_probability"]):
                return prize

    def lottery_algorithm(self, prize_list):
        """
        :description: 抽奖算法（权重）
        :param prize_list:奖品列表
        :return: 中奖的奖品
        :last_editors: HuangJianYi
        """
        init_value = 0
        probability_list = []
        for prize in prize_list:
            current_prize = prize
            current_prize["start_probability"] = init_value
            current_prize["end_probability"] = init_value + prize["probability"]
            probability_list.append(current_prize)
            init_value = init_value + prize["probability"]
        prize_index = random.randint(0, init_value - 1)
        for prize in probability_list:
            if (prize["start_probability"] <= prize_index and prize_index < prize["end_probability"]):
                return prize