#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/3/1 17:58
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : extensions.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
# -*- coding: utf-8 -*-

# Define here the models for your scraped Extensions
from scrapy import signals
from scrapy.exceptions import NotConfigured
from PatternSpider.models.redis_model import OriginSettingsData
from PatternSpider.models.mysql_model import TableFBInstance


class RedisSpiderSmartIdleClosedExensions(object):

    def __init__(self, idle_number, crawler):
        self.crawler = crawler
        self.idle_number = idle_number
        self.idle_list = []
        self.idle_count = 0
        self.origin_settings_data = OriginSettingsData()
        self.fb_instance = TableFBInstance()

    @classmethod
    def from_crawler(cls, crawler):
        # first check if the extension should be enabled and raise

        # NotConfigured otherwise

        if not crawler.settings.getbool('MYEXT_ENABLED'):
            raise NotConfigured

        if not 'redis_key' in crawler.spidercls.__dict__.keys():
            raise NotConfigured('Only supports RedisSpider')

        # get the number of items from settings

        idle_number = crawler.settings.getint('IDLE_NUMBER', 360)

        # instantiate the extension object

        ext = cls(idle_number, crawler)

        # connect the extension object to signals

        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)

        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)

        crawler.signals.connect(ext.spider_idle, signal=signals.spider_idle)

        return ext

    def spider_opened(self, spider):
        spider.logger.info("opened spider {}, Allow waiting time:{} second".format(spider.name, self.idle_number * 5))

    def spider_closed(self, spider):
        spider.logger.info(
            "closed spider {}, Waiting time exceeded {} second".format(spider.name, self.idle_number * 5))

    def spider_idle(self, spider):
        # 程序启动的时候会调用这个方法一次，之后每隔5秒再请求一次
        # 当持续半个小时都没有spider.redis_key，就关闭爬虫
        # 判断是否存在 redis_key
        if not spider.server.exists(spider.redis_key):
            self.idle_count += 1
        else:
            self.idle_count = 0

        if self.idle_count > self.idle_number:
            # 获取当前机器实例id，并更新数据库状态为3
            origin_confs = self.origin_settings_data.get_settings_data()
            instance_id = origin_confs['instance_id']
            self.fb_instance.update_status(instance_id=instance_id, value=3)
            # 关闭当前chrome驱动
            spider.facebook_chrome.driver.quit()
            # 执行关闭爬虫操作
            self.crawler.engine.close_spider(spider, 'Waiting time exceeded')
