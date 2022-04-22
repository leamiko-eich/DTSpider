#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/4/11 16:15
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : facebook_user_friends_api.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
import json
import re
from scrapy import FormRequest

from PatternSpider.headers import get_playload_from_spider_name
from PatternSpider.scrapy_redis.spiders import RedisSpider
from PatternSpider.scrapy_redis.utils import bytes_to_str
from PatternSpider.servers.ding_talk_server import ding_alarm
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.tasks import TaskManage
from PatternSpider.utils.dict_utils import DictUtils
from PatternSpider.utils.logger_utils import get_logger
from PatternSpider.spiders.facebook import FacebookUtils


class FacebookUserFriendsApiSpider(RedisSpider):
    name = SpiderNames.facebook_user_friends_api
    redis_key = "start_urls:" + name
    logger = get_logger(name)
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
            'PatternSpider.pipelines.DataBasePipeline': 500,
        }
    }

    def make_request_from_data(self, dict_data):
        """
        :type dict_data: dict
        :return: 一个FormRequest对象
    　　"""
        # data是url地址，将参数解析出来
        if 'friend' in dict_data['url']:
            url = bytes_to_str(dict_data['url'], self.redis_encoding)
            return self.make_requests_from_url(url)

        raw = dict_data['raw']
        payload = get_playload_from_spider_name(spider_name=self.name, raw=raw)
        req = FormRequest(url=dict_data['url'], formdata=payload, callback=self.parse_graphql)
        return req

    @ding_alarm("spiders", name, logger)
    def __init__(self):
        # 创建driver
        super(FacebookUserFriendsApiSpider, self).__init__(name=self.name)
        self.dict_util = DictUtils()
        self.facebook_util = FacebookUtils()

    @ding_alarm("spiders", name, logger)
    def parse(self, response):
        task = json.loads(response.meta['task'])
        self.logger.info('第一次响应解析,{}'.format(task['url']))
        # 开始解析
        page_source = response.text
        # 判读如果访问失败就直接返回
        result = self.facebook_util.check_pagesource(page_source)
        if not result:
            return

        # 解析首页内的数据：
        user_info = self.get_user_info(page_source)
        tokens = self.get_token(page_source)

        re_pattern = '\{"__bbox":\{.*?extra_context.*?\}\}'
        bboxes = re.findall(re_pattern, page_source)
        if not bboxes:
            return
        # 解析第一页的好友数据:
        bboxes_dicts = [json.loads(box) for box in bboxes]
        friends_data, requests_var_id, requests_var_cursor, has_next_page = self.parse_friends(
            bboxes_dicts, user_info['userid'], user_info['homepage'])

        # 写入数据库：
        self.logger.info('第一次 入库,{}'.format(task['url']))
        for f in friends_data:
            yield f
        self.task_manage.del_item("mirror:" + self.name, response.meta['task'])
        # 判断是否进行下一页：
        if not has_next_page:
            return
        # 如果要下一页，将任务写道redis
        self.task_manage.write_task_from_spider_name(
            self.name,
            is_first=0,
            username=task['raw']['username'],
            other_raw={
                'user_info': user_info,
                'tokens': tokens,
                'page_info': {'cursor': requests_var_cursor, 'id': requests_var_id}
            }
        )

    def parse_graphql(self, response):
        task = json.loads(response.meta['task'])
        raw = task.get('raw')
        user_info = raw['user_info']
        tokens = raw['tokens']
        response_json = json.loads(response.text)

        # 解析好友数据
        friends_data, requests_var_id, requests_var_cursor, has_next_page = self.parse_friends(
            [response_json], user_info['userid'], user_info['homepage'])
        # 写入数据库：
        self.logger.info('graphql 入库,{}'.format(task['url']))
        for f in friends_data:
            yield f
        self.task_manage.del_item("mirror:" + self.name, response.meta['task'])
        # 判断是否进行下一页：
        if not has_next_page:
            return
        # 如果要下一页，将任务写道redis
        self.task_manage.write_task_from_spider_name(
            self.name,
            is_first=0,
            username=task['raw']['username'],
            other_raw={
                'user_info': user_info,
                'tokens': tokens,
                'page_info': {'cursor': requests_var_cursor, 'id': requests_var_id}
            }
        )

    def get_user_info(self, page_source):
        re_pattern = '\{"__bbox":\{.*?extra_context.*?\}\}'
        bboxes = re.findall(re_pattern, page_source)
        user_info = {}
        for box in bboxes:
            if 'profile_social_context' in box:
                user = self.dict_util.get_data_from_field(json.loads(box), '__isProfile', 'User')
                friends_count = self.dict_util.get_data_from_field(user['profile_social_context'], 'text')
                friends_count = friends_count['text'] if type(friends_count) == dict else friends_count
                user_info.update({
                    'viewer_user_id': user['viewer']['actor']['id'],
                    'userid': user['id'],
                    'name': user['name'],
                    'homepage': user['url'],
                    'avatar': user['profilePicLarge']['uri'],
                    'gender': user['gender'],
                    'friends_count': friends_count,
                })
        return user_info

    @staticmethod
    def get_token(page_source):
        re_pattern = '\{"define":.*?"IntlCurrentLocale".*?css.*?\}'
        init_data = re.search(re_pattern, page_source)
        tokens = {i[0]: i[2]['token'] for i in json.loads(init_data.group())['define'] if
                  i[0] == "DTSGInitialData" or i[0] == "LSD"} if init_data else None
        return tokens

    def parse_friends(self, datas, source_userid, source_homepage):
        # 数据解析：
        over_datas = []
        requests_var_id = ""
        requests_var_cursor = ""
        has_next_page = False
        for data in datas:
            page_items = self.dict_util.get_data_from_field(data, 'pageItems')
            if not page_items:
                continue
            requests_var_id = self.dict_util.get_data_from_field(data, 'pageItems', page_items)['id']
            requests_var_cursor = page_items['page_info']['end_cursor']
            has_next_page = page_items['page_info']['has_next_page']
            for friend in page_items['edges']:
                node = friend['node']
                user_id = node['node']['id'] if 'node' in node and 'id' in node['node'] else ''
                if not user_id:
                    continue
                friend.update({
                    "source_userid": source_userid,
                    "source_homepage": source_homepage,
                    'userid': user_id,
                    'homepage': node['url'] if 'url' in node else '',
                    'name': node['title']['text'] if 'title' in node and 'text' in node['title'] else '',
                    'avatar': node['image']['uri'] if 'image' in node else '',
                    'subname': node['subtitle_text'] if 'subtitle_text' in node else ''
                })
                over_datas.append(friend)
        return over_datas, requests_var_id, requests_var_cursor, has_next_page


if __name__ == '__main__':
    from scrapy.cmdline import execute

    execute(('scrapy crawl ' + SpiderNames.facebook_user_friends_api).split())
