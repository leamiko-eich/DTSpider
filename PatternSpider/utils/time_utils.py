#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:37
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : time_utils.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved

# coding=utf-8
import time
import datetime

from dateutil.parser import parse


def datetime_to_timestamp(datetime_str):
    return int(time.mktime(time.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")))


def us_time_to_timestamp(datetime_str):
    '''
    : datetime_str  美式日期格式  “Thu Jan 27 00:31:59 +0000 2022”  星期 月份 日期 时间 时区 年份
    : return 时间戳
    '''
    return datetime.datetime.timestamp(parse(datetime_str))


def get_now_day():
    return datetime.datetime.now().strftime('%Y-%m-%d')


def timestamp_to_datetime(timestamp):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(timestamp)))


if __name__ == '__main__':
    print(timestamp_to_datetime("0"))
