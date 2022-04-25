#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/4/24 16:42
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : reports_list.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
import json
from PatternSpider.scrapy_redis.spiders import RedisSpider
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.tasks import TaskManage


class DeagelReportsListSpider(RedisSpider):
    name = SpiderNames.deagel_reports_list
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
        reports_data = json.loads(response.text)
        names = reports_data['names']
        names_dict = {i['id']: i['name'] for i in names}

        countries = reports_data['countries']
        for i in countries:
            i['tab'] = 'country'
            yield i
            self.task_manage.write_task_from_spider_name(
                SpiderNames.deagel_reports_detail,
                path="reportsCountry",
                id=names_dict[i['id']],
            )
            print(i)

        equipments = reports_data['equipments']
        for i in equipments:
            i['tab'] = 'equipment'
            yield i
            self.task_manage.write_task_from_spider_name(
                SpiderNames.deagel_reports_detail,
                path="reportsEquipment",
                id=i['id'],
            )
            print(i)

        groups = reports_data['groups']
        for i in groups:
            i['tab'] = 'group'
            yield i
            self.task_manage.write_task_from_spider_name(
                SpiderNames.deagel_reports_detail,
                path="reportsGroup",
                id=names_dict[i['id']],
            )
            print(i)

        # 删除目录任务
        self.task_manage.del_item("mirror:" + self.name, response.meta['task'])
