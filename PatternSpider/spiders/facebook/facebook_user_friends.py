#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 18:41
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : facebook_user_friends.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
import json
import re
import time
import traceback

import scrapy

from PatternSpider.scrapy_redis.spiders import RedisSpider
from PatternSpider.servers.ding_talk_server import ding_alarm
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.tasks import TaskManage
from PatternSpider.selenium_manage.base_chrome import FacebookChrome
from PatternSpider.utils.dict_utils import DictUtils
from PatternSpider.utils.logger_utils import get_logger
from PatternSpider.spiders.facebook import FacebookUtils


class FacebookUserFriendsSpider(RedisSpider):
    name = SpiderNames.facebook_user_friends
    redis_key = "start_urls:" + name
    logger = get_logger(name)
    task_manage = TaskManage()
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOADER_MIDDLEWARES': {
            'PatternSpider.middlewares.middlewares.SeleniumMiddleware': 543,
        }
    }

    @ding_alarm("spiders", name, logger)
    def __init__(self):
        # 创建driver
        super(FacebookUserFriendsSpider, self).__init__(name=self.name)
        self.dict_util = DictUtils()
        self.facebook_util = FacebookUtils()
        self.facebook_chrome = FacebookChrome(logger=self.logger, headless=self.facebook_util.headless)
        login_res, account_status = self.facebook_chrome.login_facebook()
        # 登录失败的话，关闭爬虫
        self.login_data = {
            'login_res': login_res,
            'account_status': account_status
        }
        self.logger.info(str(self.login_data) + ' sleep 60s')
        time.sleep(self.facebook_util.init_sleep)

    @ding_alarm("spiders", name, logger)
    def parse(self, response):
        task = json.loads(response.meta['task'])
        self.logger.info('第一次响应解析,{}'.format(task['url']))
        self.facebook_util.update_current_user_status(task, 1)
        # 解析数据
        page_source = self.facebook_chrome.get_page_source_person(task['current_url_index'])
        # 加一个访问当前主页的状态，如果当前页无法访问直接结束
        result = self.facebook_util.check_pagesource(page_source)
        if not result:
            return self.close_current_task(task, 4)
        re_pattern = '\{"__bbox":\{.*?extra_context.*?\}\}'
        bboxes = re.findall(re_pattern, page_source)
        if bboxes:
            bboxes_dicts = [json.loads(box) for box in bboxes]
            friends_data, request = self.parse_friends(response, bboxes_dicts, task)
            self.logger.info('第一次 入库,{}'.format(task['url']))
            for f in friends_data:
                yield f
            self.logger.info('开始第二次请求,{}'.format(task['url']))
            yield request if request else self.close_current_task(task)
        else:
            self.close_current_task(task)

    @ding_alarm("spiders", name, logger)
    def parse_graphql(self, response):
        task = json.loads(response.meta['task'])
        self.logger.info('开始捕获接口数据,{}'.format(task['url']))
        self.facebook_chrome.get_page_source_person(task['current_url_index'])
        graphql_data_list = self.facebook_chrome.get_graphql_data()

        # 获取指定响应:
        friend_datas = []
        for need_data in graphql_data_list:
            friend_data = self.dict_util.get_data_from_field(need_data, '__typename', 'TimelineAppCollection')
            friend_datas.append(friend_data) if friend_data else None

        # 开始解析数据
        self.logger.info('解析数据,{}'.format(task['url']))
        friends_data, request = self.parse_friends(response, friend_datas, task)
        self.logger.info('入库,{}'.format(task['url']))
        for fr in friends_data:
            yield fr
        self.logger.info('开始下一次请求,{}'.format(task['url']))
        yield request if request else self.close_current_task(task)

    @ding_alarm('spiders', name, logger)
    def parse_friends(self, response, datas, task):
        # 数据解析：
        over_datas = []
        for data in datas:
            page_items = self.dict_util.get_data_from_field(data, 'pageItems')
            if not page_items:
                continue
            for friend in page_items['edges']:
                node = friend['node']
                user_id = node['node']['id'] if 'node' in node and 'id' in node['node'] else ''
                if not user_id:
                    continue
                friend.update({
                    "source_userid": task['raw'].get("source_userid", ""),
                    "source_homepage": task['raw'].get("source_homepage", ""),
                    'userid': user_id,
                    'homepage': node['url'] if 'url' in node else '',
                    'name': node['title']['text'] if 'title' in node and 'text' in node['title'] else '',
                    'avatar': node['image']['uri'] if 'image' in node else '',
                    'subname': node['subtitle_text'] if 'subtitle_text' in node else ''
                })
                over_datas.append(friend)

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

    @ding_alarm("spiders", name, logger)
    def close_current_task(self, task, task_status=2):
        self.logger.info('关闭当前页,{}'.format(task['url']))
        # 更新当前被采集对象为完成
        self.facebook_util.update_current_user_status(task, task_status)
        # 关闭当前页
        self.facebook_chrome.driver.close()
        self.facebook_chrome.get_handle(0)
        orgin_task = {'url': task['url'], 'raw': task['raw']}
        self.task_manage.del_item("mirror:" + self.name, json.dumps(orgin_task, ensure_ascii=False))


if __name__ == '__main__':
    from scrapy.cmdline import execute

    execute(('scrapy crawl ' + SpiderNames.facebook_user_friends).split())
