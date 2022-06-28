#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/3/17 9:30
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : spider_test.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
from PatternSpider.selenium_manage.base_chrome import FacebookChrome
from PatternSpider.utils.logger_utils import get_logger
import json
logger = get_logger('test')


def get_handle(driver, handle_index):
    # 获取所有窗口的句柄
    handles = driver.window_handles

    # 切换到指定标签
    if type(handle_index) == int:
        driver.switch_to.window(handles[handle_index])
    else:
        assert type(handle_index) == str
        driver.switch_to.window(handle_index)


facebook_chrome = FacebookChrome(logger=logger, headless=False)
login_res, account_status = facebook_chrome.login_facebook()
print(login_res)
# 打印当前cookies
# 打开新的chorme ，输入cookie，访问Facebook
# new_chrome = FacebookChrome(logger=logger, headless=False)
# new_chrome.login_facebook()
# new_chrome.driver.get("https://www.facebook.com/")
# for i in facebook_chrome.driver.get_cookies():
#     new_chrome.driver.add_cookie(i)
# new_chrome.driver.get("https://www.facebook.com/profile.php?id=100069879049118")

