#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:21
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : __init__.py.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
from PatternSpider.headers import get_url_from_spider_name
from PatternSpider.models.redis_model import RedisModel


class TaskManage(RedisModel):
    CLIENTNAME = 'REDIS_DT'
    NAME = ''

    def write_task(self, url, raw, spider_name, score=1000):
        redis_key = 'start_urls:' + spider_name
        data = dict(
            url=url,
            raw=raw
        )
        self.write_item_to_redis(redis_key, score, data)

    def write_task_from_spider_name(self, spider_name, other_raw=None, **kwargs):
        url = get_url_from_spider_name(
            spider_name,
            **kwargs
        )
        raw = kwargs
        if other_raw:
            assert type(other_raw) == dict
            raw.update(other_raw)
        self.write_task(url=url, raw=raw, spider_name=spider_name, score=kwargs.get('priority', 1000))

    def get_mirror_task(self, spider_name):
        redis_key = 'mirror:' + spider_name
        return self.zset_get_all(redis_key)


if __name__ == '__main__':
    a = TaskManage().get_mirror_task('facebook_user')
    print(a)
