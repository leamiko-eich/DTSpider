#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/4/24 16:24
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : country_list.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
import json
from PatternSpider.scrapy_redis.spiders import RedisSpider
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.tasks import TaskManage


class DeagelCountryListSpider(RedisSpider):
    name = SpiderNames.deagel_country_list
    redis_key = "start_urls:" + name
    task_manage = TaskManage()
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
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
        country_data = json.loads(response.text)
        country_list = country_data['items']
        country_data.pop('items')
        for item in country_list:
            item.update(country_data)
            print(item)
            yield item

            self.task_manage.write_task_from_spider_name(
                SpiderNames.deagel_country_detail,
                country_name=item['name']
            )
        # 删除目录任务
        self.task_manage.del_item("mirror:" + self.name, response.meta['task'])
