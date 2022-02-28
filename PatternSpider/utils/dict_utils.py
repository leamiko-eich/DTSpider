#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/20 1:09
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : dict_utils.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved

class DictUtils:
    @staticmethod
    def get_data_from_path(data, path_list):
        for i in path_list:
            data = data[int(i)] if i.isdigit() else data[i]
        return data

    def get_field_path(self, data, field, value=None):
        """
        :param data: 超长的字典或者列表数据
        :param field: 想要的字段名称
        :param value: 可选，想要的字段名称的对应的值
        :return: 该字段在字典或者列表中的路径 - 符号分割
        """
        if type(data) == list:
            for index, data in enumerate(data):
                res = self.get_field_path(data, field, value)
                if res:
                    return str(index) + '-' + res
        if type(data) == dict:
            if field in data:
                if value:
                    if data[field] == value:
                        return field
                else:
                    return field
            for i in data:
                res = self.get_field_path(data[i], field, value)
                if res:
                    return i + '-' + res

    def get_data_from_field(self, datas, field, value=None):
        """
        :param datas: 超长的字典或者列表数据
        :param field: 想要的字段名称
        :param value: 可选，想要的字段名称的对应的值
        :return: 想要的key 对应的value
        """
        if not datas:
            return None
        path = self.get_field_path(datas, field, value)
        if not path:
            return None
        if value:
            path_list = path.split('-')[:-1]
        else:
            path_list = path.split('-')
        return self.get_data_from_path(datas, path_list)
