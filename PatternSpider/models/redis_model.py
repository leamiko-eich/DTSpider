#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:30
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : redis_model.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
import json
from redis import WatchError
from PatternSpider.models.link_manage import LinkManege


def redis_lock(func):
    def class_function(self, *args, **kwargs):
        res = -1
        while 1:
            try:
                # 监听key
                self.pipeline.watch(self.NAME)
                # 开始事务
                self.pipeline.multi()
                # 执行命令
                res = func(self, *args, **kwargs)
                # 释放锁
                self.pipeline.unwatch()
                break
            except WatchError as e:
                self.pipeline.unwatch()
                continue
        return res

    return class_function


class RedisModel:
    CLIENTNAME = ''
    NAME = ''

    def __init__(self):
        self.db = LinkManege().get_redis_db(self.CLIENTNAME)
        self.pipeline = self.db.pipeline()

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

    def zset_get_all(self, key):
        return self.db.zrange(key, 0, -1)

    def get_count(self, key):
        return self.db.zcard(key)

    # string类型========================================================================================
    def string_set(self, key, value):
        return self.db.set(key, value)

    def string_append(self, key, append_data):
        return self.db.append(key, append_data)

    def string_get(self, key):
        return self.db.get(key)

    # List类型===========================================================================================
    def list_rpush(self, key, *args):
        """
        在插入数据时，如果该键并不存在，Redis将为该键创建一个
        在末尾添加数据（列表右边）
        :param key:
        :param args:
        :return:
        """
        return self.db.rpush(key, *args)

    def list_lpush(self, key, *args):
        """
        在头部添加数据（列表左边）
        :param key:
        :param args:
        :return:
        """
        return self.db.lpush(key, *args)

    def list_get_range(self, key, start, stop):
        """
        查看key的从start到stop的元素
        :param key:
        :param start:
        :param stop:
        :return:
        """
        return self.db.lrange(key, start, stop)

    def list_get_one(self, key, index):
        """
        :param key: key
        :param index: 列表索引
        :return: 指定下标的元素
        """
        return self.db.lindex(key, index)

    def list_rpop(self, key):
        return self.db.rpop(key)

    def list_lpop(self, key):
        return self.db.lpop(key)

    def list_lrem(self, key, count, value):
        """
        :param key:
        :param count: 可以存在多个重复的值，指定value删除的次数
        :param value: 删除的值
        :return: 打印成功删除的个数
        """
        return self.db.lrem(key, count, value)


# 本地存储使用的记录
class OriginSettingsData(RedisModel):
    CLIENTNAME = 'REDIS_DT'
    NAME = 'origin_settings_data'

    def save_settings_data(self, datas: dict):
        return self.string_set(self.NAME, json.dumps(datas))

    def get_settings_data(self):
        return json.loads(self.string_get(self.NAME))


# 分布式加锁获取settings
class DistributedSettings(RedisModel):
    CLIENTNAME = 'REDIS_HUAWEI'
    NAME = 'origin_settings_data'

    @redis_lock
    def save_settings_data(self, datas: dict):
        # 执行命令
        self.pipeline.rpush(self.NAME, json.dumps(datas))
        return self.pipeline.execute()

    @redis_lock
    def get_settings_data(self):
        self.pipeline.lpop(self.NAME)
        return self.pipeline.execute()[0]
