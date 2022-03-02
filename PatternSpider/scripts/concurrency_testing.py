#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/3/2 14:45
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : concurrency_testing.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
import json
import time

import gevent
from gevent import monkey

from PatternSpider.models.redis_model import DistributedSettings

monkey.patch_socket()  # 实现高并发，这个猴子补丁是必须的


def test(i):
    print("{}==".format(i))


def redis_lock_test(i):
    data = DistributedSettings().get_settings_data()
    print("{}=={}=={}".format(i, time.time(), json.loads(data)))


def run():
    n = 3
    """开始运行"""
    workers = [gevent.spawn(test, i) for i in range(n)]  # 传参数i
    gevent.joinall(workers)  # 等所有请求结束后退出，类似线程的join
    print('Done!')


if __name__ == '__main__':
    run()
