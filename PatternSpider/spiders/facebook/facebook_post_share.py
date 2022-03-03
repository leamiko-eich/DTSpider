#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/22 9:14
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : facebook_post_share.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved

# !/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/22 9:13
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : facebook_post_like.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
import json
import scrapy

from PatternSpider.scrapy_redis.spiders import RedisSpider
from PatternSpider.servers.ding_talk_server import ding_alarm
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.spiders.facebook import FacebookUtils
from PatternSpider.tasks import TaskManage
from PatternSpider.selenium_manage.base_chrome import FacebookChrome
from PatternSpider.utils.logger_utils import get_logger
from PatternSpider.utils.dict_utils import DictUtils
from PatternSpider.utils.time_utils import timestamp_to_datetime


class FacebookPostShareSpider(RedisSpider):
    name = SpiderNames.facebook_post_share
    redis_key = "start_urls:" + name
    logger = get_logger(name)
    task_manage = TaskManage()
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOADER_MIDDLEWARES': {
            'PatternSpider.middlewares.middlewares.SeleniumMiddleware': 543,
        }
    }

    @ding_alarm('spiders', name, logger)
    def __init__(self):
        # 创建driver
        super(FacebookPostShareSpider, self).__init__(name=self.name)
        self.facebook_chrome = FacebookChrome(logger=self.logger, headless=False)
        self.facebook_chrome.login_facebook()
        self.dict_util = DictUtils()
        self.facebook_util = FacebookUtils()

    @ding_alarm('spiders', name, logger)
    def parse(self, response):
        task = json.loads(response.meta['task'])
        # 更新当前被采集对象为进行时
        self.facebook_util.update_current_user_status(task, 1)
        self.facebook_chrome.get_page_source_share(task['current_url_index'])
        task['need_tab'] = 2
        # 聚焦弹窗
        yield scrapy.Request(
            response.request.url,
            callback=self.parse_graphql,  # 处理响应的回调函数。
            meta={"task": json.dumps(task)},  # 可以在 不同的回调函数中传递数据
            dont_filter=True
        )

    @ding_alarm('spiders', name, logger)
    def parse_graphql(self, response):
        task = json.loads(response.meta['task'])
        self.facebook_chrome.get_handle(task['current_url_index'])
        graphql_datas = self.facebook_chrome.get_graphql_data()

        share_datas = []
        for graphql_data in graphql_datas:
            reshares = self.dict_util.get_data_from_field(graphql_data, 'reshares')
            share_datas.append(graphql_data) if reshares else None

        over_datas, request = self.parse_share_user(response, task, share_datas)
        # 数据入库和迭代下次请求
        for over_data in over_datas:
            yield over_data

        yield request if request else self.close_current_page(task)

    def parse_share_user(self, response, task, share_datas):
        # 解析数据相关：
        over_datas = []
        for share_data in share_datas:
            reshares = self.dict_util.get_data_from_field(share_data, 'reshares')
            comet_sections = self.dict_util.get_data_from_field(reshares, 'comet_sections')
            user_data = self.dict_util.get_data_from_field(comet_sections['context_layout'], 'comet_sections')
            user = self.dict_util.get_data_from_field(user_data, '__typename', 'User')
            creation_time = self.dict_util.get_data_from_field(user_data, 'creation_time')
            if not user:
                continue

            user.update({
                "post_id": task['raw']['post_id'],
                "post_url": task['raw']['post_url'],
                "userid": user.get('id', 0),
                "username": user.get('name', ''),
                "homepage": user.get('url', ''),
                "share_time": timestamp_to_datetime(creation_time) if creation_time else timestamp_to_datetime(0),

            })
            over_datas.append(user)

        # 分析下一次请求相关：
        if 'need_tab' in task:
            del task['need_tab']
        # 判断是否进行下一次请求
        is_next, task = self.facebook_util.is_next_request(task, len(over_datas))
        self.logger.info('spider name:{},the number I have collected is {}'.format(self.name, task['had_count']))
        if is_next:
            request = scrapy.Request(
                response.request.url,
                callback=self.parse_graphql,
                meta={"task": json.dumps(task)},
                dont_filter=True
            )
        else:
            request = None
        return over_datas, request

    def close_current_page(self, task):
        # 关闭当前页
        self.facebook_chrome.driver.close()
        self.facebook_chrome.get_handle(0)
        # 更新当前被采集对象为完成
        self.facebook_util.update_current_user_status(task, 2)
        del task['current_url_index']
        self.task_manage.del_item("mirror:" + self.name, json.dumps(task))


if __name__ == '__main__':
    from scrapy.cmdline import execute

    execute(('scrapy crawl ' + SpiderNames.facebook_post_share).split())
