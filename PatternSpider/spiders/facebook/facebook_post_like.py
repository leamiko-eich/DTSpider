#!/usr/bin/python3.8
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
import urllib.parse

import scrapy

from PatternSpider.scrapy_redis.spiders import RedisSpider
from PatternSpider.servers.ding_talk_server import ding_alarm
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.tasks import TaskManage
from PatternSpider.selenium_manage.base_chrome import FacebookChrome
from PatternSpider.utils.logger_utils import get_logger
from PatternSpider.utils.dict_utils import DictUtils
from PatternSpider.spiders.facebook import FacebookUtils


class FacebookPostLikeSpider(RedisSpider):
    name = SpiderNames.facebook_post_like
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
        super(FacebookPostLikeSpider, self).__init__(name=self.name)
        self.dict_util = DictUtils()
        self.facebook_util = FacebookUtils()
        self.facebook_chrome = FacebookChrome(logger=self.logger, headless=self.facebook_util.headless)
        login_res, account_status = self.facebook_chrome.login_facebook()
        # 登录失败的话，关闭爬虫
        self.login_data = {
            'login_res': login_res,
            'account_status': account_status
        }
        print(self.login_data)
        time.sleep(self.facebook_util.init_sleep)

    @ding_alarm('spiders', name, logger)
    def parse(self, response):
        task = json.loads(response.meta['task'])
        # 更新当前被采集对象为进行时
        self.facebook_util.update_current_user_status(task, 1)
        f, page_source = self.facebook_chrome.get_page_source_like(task['current_url_index'])
        # 加一个访问当前主页的状态，如果当前页无法访问直接结束
        result = self.facebook_util.check_pagesource(page_source)
        if not result:
            return self.close_current_page(task, 4)
        # 如果访问成功但是没有点赞
        if not f:
            return self.close_current_page(task)


        yield scrapy.Request(
            response.request.url,
            callback=self.parse_graphql,  # 处理响应的回调函数。
            meta={"task": json.dumps(task)},  # 可以在不同的回调函数中传递数据
            dont_filter=True
        )

    @ding_alarm('spiders', name, logger)
    def parse_graphql(self, response):
        task = json.loads(response.meta['task'])
        self.facebook_chrome.get_handle(task['current_url_index'])
        graphql_datas = self.facebook_chrome.get_graphql_data()

        like_datas = []
        for graphql_data in graphql_datas:
            post_data = dict(urllib.parse.parse_qsl(graphql_data['postData'])) if 'postData' in graphql_data else {}
            if post_data:
                if "CometUFIReactionsDialog" in post_data['fb_api_req_friendly_name']:
                    like_datas.append(graphql_data)

        over_datas, request = self.parse_like_user(response, task, like_datas)

        # 数据入库和迭代下次请求
        for over_data in over_datas:
            yield over_data
        yield request if request else self.close_current_page(task)

    @ding_alarm('spiders', name, logger)
    def parse_like_user(self, response, task, like_datas):
        # 解析数据相关：
        over_datas = []
        for like_data in like_datas:
            reactors = self.dict_util.get_data_from_field(like_data, 'reactors')
            if not reactors:
                continue
            for reactor in reactors['edges']:
                node = reactor['node']
                node.update({
                    "post_id": task['raw']['post_id'],
                    "post_url": task['raw']['post_url'],
                    "userid": node['id'],
                    "username": node['name'],
                    "homepage": node['url'],
                    "type": "",
                })
                over_datas.append(node)

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

    def close_current_page(self, task, task_status=2):
        # 关闭当前页
        self.facebook_chrome.driver.close()
        self.facebook_chrome.get_handle(0)
        # 更新当前被采集对象为完成
        self.facebook_util.update_current_user_status(task, task_status)
        orgin_task = {'url': task['url'], 'raw': task['raw']}
        self.task_manage.del_item("mirror:" + self.name, json.dumps(orgin_task, ensure_ascii=False))


if __name__ == '__main__':
    from scrapy.cmdline import execute

    execute(('scrapy crawl ' + SpiderNames.facebook_post_like).split())
