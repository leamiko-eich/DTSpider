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
import time

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
        self.dict_util = DictUtils()
        self.facebook_util = FacebookUtils()
        self.facebook_chrome = FacebookChrome(logger=self.logger, headless=self.facebook_util.headless)

        login_res, account_status = self.facebook_chrome.login_facebook()
        # 登录失败的话，关闭爬虫
        self.login_data = {
            'login_res': login_res,
            'account_status': account_status
        }
        self.logger.info(self.login_data)
        time.sleep(self.facebook_util.init_sleep)

    @ding_alarm('spiders', name, logger)
    def parse(self, response):
        task = json.loads(response.meta['task'])
        self.logger.info('1 解析响应,{}'.format(task['url']))
        # 更新当前被采集对象为进行时
        self.facebook_util.update_current_user_status(task, 1)
        f, page_source = self.facebook_chrome.get_page_source_share(task['current_url_index'])
        # 加一个访问当前主页的状态，如果当前页无法访问直接结束
        result = self.facebook_util.check_pagesource(page_source)
        if not result:
            return self.close_current_page(task, 4)

        if not f:
            return self.close_current_page(task)

        self.logger.info('开始下次请求,{}'.format(task['url']))
        task['need_tab'] = 2
        yield scrapy.Request(
            response.request.url,
            callback=self.parse_graphql,  # 处理响应的回调函数。
            meta={"task": json.dumps(task)},  # 可以在 不同的回调函数中传递数据
            dont_filter=True
        )

    @ding_alarm('spiders', name, logger)
    def parse_graphql(self, response):
        task = json.loads(response.meta['task'])
        self.logger.info('开始获取接口数据,{}'.format(task['url']))
        self.facebook_chrome.get_handle(task['current_url_index'])
        time.sleep(3)
        graphql_datas = self.facebook_chrome.get_graphql_data()

        share_datas = []
        for graphql_data in graphql_datas:
            reshares = self.dict_util.get_data_from_field(graphql_data, 'reshares')
            share_datas.append(graphql_data) if reshares else None
        self.logger.info('解析数据,{}'.format(task['url']))
        over_datas, request = self.parse_share_user(response, task, share_datas)
        # 数据入库和迭代下次请求
        self.logger.info('入库,{}'.format(task['url']))
        for over_data in over_datas:
            yield over_data
        self.logger.info('开始下次请求,{}'.format(task['url']))
        yield request if request else self.close_current_page(task)

    @ding_alarm('spiders', name, logger)
    def parse_share_user(self, response, task, share_datas):
        # 解析数据相关：
        over_datas = []
        for share_data in share_datas:
            share_data = json.loads(json.dumps(share_data).replace('.', ''))
            reshares = self.dict_util.get_data_from_field(share_data, 'reshares')
            comet_sections = self.dict_util.get_data_from_field(reshares, 'comet_sections')
            if not comet_sections:
                continue
            user_data = self.dict_util.get_data_from_field(comet_sections['context_layout'], 'comet_sections')
            user = self.dict_util.get_data_from_field(user_data, '__typename', 'User')
            user = user if user else self.dict_util.get_data_from_field(user_data, '__typename', 'Page')
            if not user:
                continue

            creation_time = self.dict_util.get_data_from_field(user_data, 'creation_time')
            share_data.update({
                "post_id": task['raw']['post_id'],
                "post_url": task['raw']['post_url'],
                "userid": user.get('id', -1),
                "username": user.get('name', ''),
                "homepage": user.get('url', ''),
                "share_time": timestamp_to_datetime(creation_time) if creation_time else timestamp_to_datetime(0),
            })
            if share_data['userid'] == -1:
                continue
            over_datas.append(share_data)

        # 分析下一次请求相关：
        if 'need_tab' in task:
            del task['need_tab']
        # 判断是否进行下一次请求
        is_next, task = self.facebook_util.is_next_request(task, len(over_datas))
        self.logger.info('spider name:{},the number I have collected is {}'.format(task['url'], task['had_count']))
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

    def close_current_page(self, task, task_status=2):
        # 关闭当前页
        self.logger.info('关闭当前页,{}'.format(task['url']))
        self.facebook_chrome.driver.close()
        self.facebook_chrome.get_handle(0)
        # 更新当前被采集对象为完成
        self.facebook_util.update_current_user_status(task, task_status)
        orgin_task = {'url': task['url'], 'raw': task['raw']}
        self.task_manage.del_item("mirror:" + self.name, json.dumps(orgin_task, ensure_ascii=False))


if __name__ == '__main__':
    from scrapy.cmdline import execute

    execute(('scrapy crawl ' + SpiderNames.facebook_post_share).split())
