#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:35
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : twitter_guess.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
# coding=utf-8
import json
import time

from PatternSpider.scrapy_redis.spiders import RedisSpider
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.tasks import TaskManage
from PatternSpider.utils.time_utils import us_time_to_timestamp


class TwitterGuessSpider(RedisSpider):
    name = SpiderNames.twitter_guess
    redis_key = "start_urls:" + name
    task_manage = TaskManage()

    def parse(self, response):
        # 响应解析
        last_guess = {}
        raw: dict = json.loads(response.meta['task'])['raw']
        raw.pop('cursor') if 'cursor' in raw else None

        response_json = json.loads(response.text)
        entries = response_json['data']['user']['result']['timeline']['timeline']['instructions'][0]['entries']
        guesses = entries[:-2]
        cursors = entries[len(entries) - 2:]

        for guess in guesses:
            item = {}
            result = guess['content']['itemContent']['tweet_results']['result']
            card = result['card'] if 'card' in result else ''
            legacy = result['legacy']
            item.update(legacy)
            item.update({'card': card})
            last_guess = item
            yield item

        # 判断是否进行下一页
        if self.is_continue(guesses, last_guess, raw):
            self.task_manage.write_task_from_spider_name(
                SpiderNames.twitter_guess,
                userId=raw['userId'],
                count=40,
                cursor=cursors[-1]['content']['value'],
                other_raw=raw,
            )
        self.task_manage.del_item("mirror:" + self.name, response.meta['task'])

    @staticmethod
    def is_continue(guesses, last_guess, raw):
        # 如果该站点已不返回数据，说明已采集结束
        if not guesses:
            return False
        # 时间限制，采集过去一天或者一段时间，如果没有声明，则全量采集
        time_limit_second = raw.get('time_limit_second', 0)
        if not time_limit_second:
            return True
        # 如果有声明，则根据时间段采集
        created_timestamp = us_time_to_timestamp(last_guess['created_at'])
        if time.time() - int(created_timestamp) < int(time_limit_second):
            return True
        return False


if __name__ == '__main__':
    from scrapy.cmdline import execute

    execute(('scrapy crawl ' + SpiderNames.twitter_guess).split())
