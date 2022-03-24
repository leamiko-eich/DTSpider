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
import json

from scrapy import signals
from scrapy.exceptions import NotConfigured
from PatternSpider.models.mysql_model import TableFBInstance, TableFBAccount
from PatternSpider.models.redis_model import OriginSettingsData
from PatternSpider.servers.ding_talk_server import DingTalk
from PatternSpider.utils.local_utils import get_outer_host_ip
from PatternSpider.tasks import TaskManage
from PatternSpider.spiders.facebook import FacebookUtils
from PatternSpider.servers.log_upload import log_upload


class RedisSpiderSmartIdleClosedExensions(object):

    def __init__(self, idle_number, crawler):
        self.crawler = crawler
        self.idle_number = idle_number
        self.idle_list = []
        self.idle_count = 0
        self.fb_instance = TableFBInstance()
        self.fb_account = TableFBAccount()
        self.settings_data = OriginSettingsData()
        self.task = TaskManage()
        self.facebook_util = FacebookUtils()

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

        if self.idle_count > self.idle_number or not spider.login_data['login_res']:
            # 关闭当前chrome驱动
            settings_data = self.settings_data.get_settings_data()
            ding = "关闭采集程序：instance_id:{},allocation_id:{}、采集程序：{}\n".format(
                settings_data['instance_id'], settings_data['allocation_id'],spider.name)

            # 关闭chrome驱动
            spider.facebook_chrome.driver.quit()

            if not spider.login_data['login_res']:
                # 修改账号状态
                self.fb_account.update_one(
                    {'id': settings_data['account_id']},
                    {'status': spider.login_data['account_status'], 'is_using': 0}
                )
                ding += "理由：账号登录失败{}".format(spider.login_data['account_status'])
            else:
                # 账号rank+1,daily_use_count+1
                account_info = self.fb_account.find({'id': settings_data['account_id']}, 1)
                account_info['daily_use_count'] = account_info['daily_use_count'] if account_info[
                    'daily_use_count'] else 0
                account_info['account_rank'] = account_info['account_rank'] if account_info['account_rank'] else 0
                account_rank = account_info['account_rank'] + 1
                daily_use_count = account_info['daily_use_count'] + 1
                self.fb_account.update_one(
                    {'id': settings_data['account_id']},
                    {'account_rank': account_rank, 'daily_use_count': daily_use_count, 'is_using': 0}
                )
                # 失败任务修改任务状态为
                faileds_tasks = self.task.get_mirror_task(spider.name)
                for faileds_task in faileds_tasks:
                    self.facebook_util.update_current_user_status(json.loads(faileds_task), 3)
                ding += "理由：正常结束,失败任务数量:{}".format(len(faileds_tasks))

                # # 上报日志：
                # log_upload(
                #     task_code=settings_data['code'],
                #     group_id=','.join(settings_data['group_id']),
                #     log_name=spider.name
                # )

            # 获取当前机器实例id，并更新数据库状态为3
            self.fb_instance.update_one(
                {'instance_id': settings_data['instance_id'], 'allocation_id': settings_data['allocation_id']},
                {'status': 3}
            )

            DingTalk().send_msg(ding)
            # 执行关闭爬虫操作
            self.crawler.engine.close_spider(spider, 'Waiting time exceeded')
