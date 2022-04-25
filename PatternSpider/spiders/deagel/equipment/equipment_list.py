#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/4/24 14:38
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : equipment_list.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
import json
from PatternSpider.scrapy_redis.spiders import RedisSpider
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.tasks import TaskManage


class DeagelEquipmentListSpider(RedisSpider):
    name = SpiderNames.deagel_equipment_list
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
        equipment_list = json.loads(response.text)
        yield equipment_list
        for equipment in equipment_list['list']:
            self.task_manage.write_task_from_spider_name(
                SpiderNames.deagel_equipment_detail,
                equipment_id=equipment['id'],
            )
        # 删除目录任务
        self.task_manage.del_item("mirror:" + self.name, response.meta['task'])
