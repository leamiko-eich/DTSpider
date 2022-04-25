#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/4/24 17:25
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : gallery_list.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
import json
from PatternSpider.scrapy_redis.spiders import RedisSpider
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.tasks import TaskManage


class DeagelGalleryListSpider(RedisSpider):
    name = SpiderNames.deagel_gallery_list
    redis_key = "start_urls:" + name
    task_manage = TaskManage()
    custom_settings = {
        'CONCURRENT_REQUESTS': 16,
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
        photos_datas = json.loads(response.text)
        photos_items = photos_datas['items']
        date_data = {}
        for photos_item in photos_items:
            if photos_item['date']:
                date_data = photos_item
                continue
            if photos_item['id']:
                photos_item.update({
                    "date": date_data['date'],
                })
                print(photos_item)
                yield photos_item
                self.task_manage.write_task_from_spider_name(
                    SpiderNames.deagel_gallery_detail,
                    id=photos_item['id']
                )
        if raw['page'] == 1:
            pager = photos_datas['pager']
            for i in range(2, pager['maxPage'] + 1):
                self.task_manage.write_task_from_spider_name(
                    self.name,
                    page=i
                )
        # 删除任务
        self.task_manage.del_item("mirror:" + self.name, response.meta['task'])