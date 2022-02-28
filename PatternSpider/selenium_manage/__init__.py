#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:56
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : __init__.py.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
from selenium import webdriver


class BaseSelenium:
    driver: webdriver.Chrome
    clear_cache_status = True

    def __del__(self):
        """
        对象被销毁时关闭已打开的浏览器
        """
        pass

    def clear_cache_driver(self):
        """
        清除缓存
        """
        pass

    @staticmethod
    def get_log_options(headless):
        """
        :param headless: 获取打开浏览器的各个参数
        :return: 参数集合
        """
        pass

    @staticmethod
    def get_caps():
        """
        :return: 日志配置
        """
        pass

    def get_new_chrome(self, headless=True):
        """
        :param headless: 是否是有头浏览器，默认无头
        :return: 新的浏览器
        """
        pass

    def get_handle(self, handle_index):
        """
        :param handle_index: 标签页的索引
        :return: 打开指定标签页
        """
        pass

    def get_page_source(self, handle_index):
        """
        :param handle_index: 标签页索引
        :return: 标签页的网页源码
        """
        pass
