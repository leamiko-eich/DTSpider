#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:21
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : pipelines.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json
import os
import traceback

from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from PatternSpider.models import run
from PatternSpider.settings.spider_names import SpiderTableNames
from scrapy.utils.project import get_project_settings
from PatternSpider.servers.ding_talk_server import DingTalk

settings = get_project_settings()


class DownloadImagesPipeline(ImagesPipeline):
    """
    item必备字段：
        is_download_image  是否要下载图片
        image_urls  图片资源url  类型是列表
        image_name  保存到本地的图片名称，图片路径在settings里面的IMAGES_STORE
    """

    def get_media_requests(self, item, info):
        if item.get("is_download_image", ""):
            for url in item['image_urls']:
                yield Request(url=url, meta={'item': item})

    def file_path(self, request, response=None, info=None):
        # 该方法是在图片将要被存储的时候调用，来获取这个图片存储路径
        image_name = request.meta['item']['image_name']
        image_name = image_name + '.jpg' if '.jpg' not in image_name else image_name
        images_store = settings.get('IMAGES_STORE')
        if not os.path.exists(images_store):
            os.mkdir(images_store)
        image_path = os.path.join(images_store, image_name)
        return image_path

    def item_completed(self, results, item, info):
        if item.get("is_download_image", ""):
            try:
                if results[0][0]:
                    print("下载成功：" + results[0][1]['path'])
                else:
                    print(results)
            except:
                with open('photo_failed_item.text', 'a', encoding='utf-8') as f:
                    f.write(json.dumps(item) + '\n')
        return item


class DataBasePipeline(object):
    def process_item(self, item, spider):
        tables = []
        # if 'mongo' in SpiderTableNames[spider.name]:
        #     tables += SpiderTableNames[spider.name]['mongo']

        if 'mysql' in SpiderTableNames[spider.name]:
            tables += SpiderTableNames[spider.name]['mysql']

        # if 'minio' in SpiderTableNames[spider.name]:
        #     tables += SpiderTableNames[spider.name]['minio']

        for table in tables:
            try:
                run(table, item=item)
            except:
                error = "current spider is：{}\npipeline error info is：\n {}".format(spider.name, traceback.format_exc())
                DingTalk().send_msg(error)
        return item
