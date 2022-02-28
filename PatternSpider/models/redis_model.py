#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:30
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : redis_model.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved

# -*- coding: UTF-8 -*-
import json
from PatternSpider.models.link_manage import LinkManege


class RedisModel:
    CLIENTNAME = ''
    NAME = ''

    def __init__(self):
        self.db = LinkManege().get_redis_db(self.CLIENTNAME)

    # hash类型=============================================================================
    def count_cookies(self):
        return self.db.hlen(self.NAME)

    def get_all(self):
        return self.db.hgetall(self.NAME)

    def set(self, key, value):
        return self.db.hset(self.NAME, key, value)

    def del_cookie(self, key):
        return self.db.hdel(self.NAME, key)

    # zset类型===============================================================================
    def del_item(self, key, data_str):
        try:
            self.db.zrem(key, data_str)
        except BaseException as e:
            print("add redis %s" % e)

    def write_item_to_redis(self, key, score, data_dict):
        # 向redis中写入数据
        try:
            self.db.zadd(key, {json.dumps(data_dict, ensure_ascii=False): score})
        except BaseException as e:
            print("add redis %s" % e)

    def get_count(self, key):
        return self.db.zcard(key)


if __name__ == '__main__':
    pass
