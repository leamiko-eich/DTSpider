#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:18
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : __init__.py.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
import random
from PatternSpider.models.redis_model import RedisModel


class RedisCookieModel(RedisModel):
    CLIENTNAME = ''
    NAME = ''

    # 通用方法
    def get_value_from_key(self, key):
        value = self.db.hget(self.NAME, key)
        if value:
            return value.decode()
        return None

    def get_random_key(self):
        keys = self.db.hkeys(self.NAME)
        if keys:
            return random.choice(keys).decode()
        return None
