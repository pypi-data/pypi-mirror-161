# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-04-22 14:32:40
:LastEditTime: 2021-03-03 14:10:59
:LastEditors: HuangJingCan
:description: 常用帮助类
"""
import random
import hashlib
import datetime


class SevenHelper:
    """
    :description: 常用帮助类
    """
    @classmethod
    def merge_dict_list(self, source_dict_list, source_key, merge_dict_list, merge_key, merge_columns_names):
        """
        :description: 两个字典列表合并
        :param source_dict_list：源字典表
        :param source_key：源表用来关联的字段
        :param merge_dict_list：需要合并的字典表
        :param merge_key：需要合并的字典表用来关联的字段
        :param merge_columns_names：需要合并的字典表中需要展示的字段
        :return: 
        :last_editors: HuangJingCan
        """
        result = []
        for source_dict in source_dict_list:
            info_list = [i for i in merge_dict_list if source_dict[source_key] != "" and i[merge_key] == source_dict[source_key]]
            if info_list:
                list_key = list(merge_columns_names.split(","))
                source_dict = dict(source_dict, **dict.fromkeys(list_key))
                for item in list_key:
                    source_dict[item] = info_list[0].get(item)
            else:
                list1 = list(merge_columns_names.split(","))
                source_dict = dict(source_dict, **dict.fromkeys(list1))
            result.append(source_dict)
        return result

    @classmethod
    def auto_mapper(self, s_model, map_dict=None):
        '''
        :description: 对象映射（把map_dict值赋值到实体s_model中）
        :param s_model：需要映射的实体对象
        :param map_dict：被映射的实体字典
        :return: obj
        :last_editors: HuangJingCan
        '''
        if map_dict:
            field_list = s_model.get_field_list()
            for filed in field_list:
                if filed in map_dict:
                    setattr(s_model, filed, map_dict[filed])
        return s_model

    @classmethod
    def get_condition_by_id_list(self, primary_key, id_list=None):
        '''
        :description: 根据id_list返回查询条件
        :param primary_key：主键
        :param id_list：id：列表
        :return: str
        :last_editors: HuangJingCan
        '''
        if not id_list:
            return ""
        id_list_str = str(id_list).strip('[').strip(']')
        return f"{primary_key} IN({id_list_str})"

    @classmethod
    def get_random_switch_string(self, random_str, split_chars=","):
        """
        :description: 随机取得字符串
        :param trimChars：根据什么符号进行分割
        :return: str
        :last_editors: HuangJingCan
        """
        if random_str == "":
            return ""
        random_list = [i for i in random_str.split(split_chars) if i != ""]
        return random.choice(random_list)

    @classmethod
    def to_file_size(self, size):
        """
        :description: 文件大小格式化
        :param size：文件大小
        :return: str
        :last_editors: HuangJingCan
        """
        if size < 1000:
            return '%i' % size + 'size'
        elif 1024 <= size < 1048576:
            return '%.2f' % float(size / 1024) + 'KB'
        elif 1048576 <= size < 1073741824:
            return '%.2f' % float(size / 1048576) + 'MB'
        elif 1073741824 <= size < 1000000000000:
            return '%.2f' % float(size / 1073741824) + 'GB'
        elif 1000000000000 <= size:
            return '%.2f' % float(size / 1000000000000) + 'TB'

    @classmethod
    def get_random(self, num, many):
        """
        :description: 获取随机数
        :param num：位数
        :param many：个数
        :return: str
        :last_editors: CaiYouBin
        """
        result = ""
        for x in range(many):
            s = ""
            for i in range(num):
                # n=1 生成数字  n=2 生成字母
                n = random.randint(1, 2)
                if n == 1:
                    numb = random.randint(0, 9)
                    s += str(numb)
                else:
                    nn = random.randint(1, 2)
                    cc = random.randint(1, 26)
                    if nn == 1:
                        numb = chr(64 + cc)
                        s += numb
                    else:
                        numb = chr(96 + cc)
                        s += numb
            result += s
        return result

    @classmethod
    def get_now_day_int(self, hours=0):
        """
        :description: 获取整形的天20200506
        :param hours: 需要增加的小时数
        :return: int（20200506）
        :last_editors: HuangJingCan
        """
        now_date = (datetime.datetime.now() + datetime.timedelta(hours=hours))
        now_day = int(now_date.strftime("%Y%m%d"))
        return now_day

    @classmethod
    def get_now_month_int(self, hours=0):
        """
        :description: 获取整形的月202005
        :param hours: 需要增加的小时数
        :return: int（202005）
        :last_editors: HuangJingCan
        """
        now_date = (datetime.datetime.now() + datetime.timedelta(hours=hours))
        now_month = int(now_date.strftime("%Y%m"))
        return now_month

    @classmethod
    def get_page_count(self, page_size, record_count):
        """
        @description: 计算页数
        @param page_size：页大小
        @param record_count：总记录数
        @return: 页数
        @last_editors: HuangJingCan
        """
        page_count = record_count / page_size + 1
        if page_size == 0:
            page_count = 0
        if record_count % page_size == 0:
            page_count = record_count / page_size
        page_count = int(page_count)
        return page_count