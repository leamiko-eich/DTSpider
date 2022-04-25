#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/4/24 14:37
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : equipment_directories.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
import json
from PatternSpider.scrapy_redis.spiders import RedisSpider
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.tasks import TaskManage


class DeagelEquipmentDirectoriesSpider(RedisSpider):
    name = SpiderNames.deagel_equipment_directories
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
        equipment_directories = json.loads(response.text)
        for equipment_directorie in equipment_directories:
            yield equipment_directorie
            # 添加目录下一级，装备列表的任务
            self.task_manage.write_task_from_spider_name(
                SpiderNames.deagel_equipment_list,
                directory_name=equipment_directorie['name']
            )

        # 删除目录任务
        self.task_manage.del_item("mirror:" + self.name, response.meta['task'])


if __name__ == '__main__':
    from scrapy.cmdline import execute

    execute(('scrapy crawl ' + SpiderNames.deagel_equipment_directories).split())
