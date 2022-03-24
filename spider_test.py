#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/3/17 9:30
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : spider_test.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
from PatternSpider.selenium_manage.base_chrome import BaseChrome


def get_handle(driver, handle_index):
    # 获取所有窗口的句柄
    handles = driver.window_handles

    # 切换到指定标签
    if type(handle_index) == int:
        driver.switch_to.window(handles[handle_index])
    else:
        assert type(handle_index) == str
        driver.switch_to.window(handle_index)


chrome = BaseChrome().get_new_chrome(False)
print(123)

get_handle(chrome, 0)
# 打开新的标签页
baidu = chrome.execute_script('window.open("http://www.baidu.com");')
# 获取当前标签页的索引
baidu_index = chrome.window_handles[-1]
print("baidu", baidu_index)

get_handle(chrome, 0)
# 打开新的标签页
csdn = chrome.execute_script('window.open("https://bbs.csdn.net/topics/394777261");')
# 获取当前标签页的索引
csdn_index = chrome.window_handles[-1]
print("csdn", csdn_index)

get_handle(chrome, 0)
# 打开新的标签页
runoob = chrome.execute_script('window.open("https://www.runoob.com/mysql/mysql-index.html");')
# 获取当前标签页的索引
runoob_index = chrome.window_handles[-1]
print("runoob", runoob_index)

print('debuug')
