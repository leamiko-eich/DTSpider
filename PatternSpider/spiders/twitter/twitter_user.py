#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:35
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : twitter_user.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved

# coding=utf-8
import json
from PatternSpider.scrapy_redis.spiders import RedisSpider
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.tasks import TaskManage


class TwitterUserSpider(RedisSpider):
    name = SpiderNames.twitter_user
    redis_key = "start_urls:" + name
    task_manage = TaskManage()

    def parse(self, response):
        raw = json.loads(response.meta['task'])['raw']
        result = json.loads(response.text)['data']['user']['result']
        user_item = {'rest_id': result['rest_id']}
        user_item.update(raw)
        user_item.update(result['legacy'])
        if raw['spider_type'] == 1:
            self.task_manage.write_task_from_spider_name(
                SpiderNames.twitter_guess,
                userId=result['rest_id'],
                count=40,
                other_raw=raw
            )
        yield user_item
        self.task_manage.del_item("mirror:" + self.name, response.meta['task'])


if __name__ == '__main__':
    from scrapy.cmdline import execute

    execute(('scrapy crawl ' + SpiderNames.twitter_user).split())
