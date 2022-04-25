#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/4/24 17:24
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : news_list.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
import json
from PatternSpider.scrapy_redis.spiders import RedisSpider
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.tasks import TaskManage


class DeagelNewsListSpider(RedisSpider):
    name = SpiderNames.deagel_news_list
    redis_key = "start_urls:" + name
    task_manage = TaskManage()
    custom_settings = {
        'CONCURRENT_REQUESTS': 6,
        'DOWNLOADER_MIDDLEWARES': {
            'PatternSpider.middlewares.middlewares.RandomUserAgentMiddleware': 543,
        },
        "EXTENSIONS": {
            # 'PatternSpider.extensions.RedisSpiderSmartIdleClosedExensions': 100,
        },
        "ITEM_PIPELINES": {
            # 'PatternSpider.pipelines.DownloadImagesPipeline': 1,
            'PatternSpider.pipelines.MongoPipeline': 100,
            # 'PatternSpider.pipelines.Neo4jPipeline': 500,
        }
    }

    def parse(self, response):
        raw = json.loads(response.meta['task'])['raw']
        news_datas = json.loads(response.text)
        news_items = news_datas['items']
        date_data = {}
        for news_item in news_items:
            if news_item['date']:
                date_data = news_item
                continue
            if news_item['id']:
                news_item.update({
                    "date": date_data['date'],
                    "day": date_data['day'],
                })
                print(news_item)
                yield news_item
                self.task_manage.write_task_from_spider_name(
                    SpiderNames.deagel_news_detail,
                    id=news_item['id']
                )
        if raw['page'] == 1:
            pager = news_datas['pager']
            for i in range(2, pager['maxPage'] + 1):
                self.task_manage.write_task_from_spider_name(
                    self.name,
                    page=i
                )
        # 删除目录任务
        self.task_manage.del_item("mirror:" + self.name, response.meta['task'])
