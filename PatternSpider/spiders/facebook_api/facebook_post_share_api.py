#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/4/12 17:53
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : facebook_post_share_api.py
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
from PatternSpider.utils.time_utils import timestamp_to_datetime


class FacebookPostShareApiSpider(RedisSpider):
    name = SpiderNames.facebook_post_share_api
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
        if "graphql" not in dict_data['url']:
            url = bytes_to_str(dict_data['url'], self.redis_encoding)
            return self.make_requests_from_url(url)

        raw = dict_data['raw']
        payload = get_playload_from_spider_name(spider_name=self.name, raw=raw)
        req = FormRequest(url=dict_data['url'], formdata=payload, callback=self.parse_graphql)
        return req

    @ding_alarm("spiders", name, logger)
    def __init__(self):
        # 创建driver
        super(FacebookPostShareApiSpider, self).__init__(name=self.name)
        self.dict_util = DictUtils()
        self.facebook_util = FacebookUtils()

    @staticmethod
    def get_token(page_source):
        re_pattern = '\{"define":.*?"IntlCurrentLocale".*?css.*?\}'
        init_data = re.search(re_pattern, page_source)
        tokens = {i[0]: i[2]['token'] for i in json.loads(init_data.group())['define'] if
                  i[0] == "DTSGInitialData" or i[0] == "LSD"} if init_data else None
        return tokens

    def get_user_info(self, bboxes):
        user_info = {}
        for box in bboxes:
            try:
                person = self.dict_util.get_data_from_field(json.loads(box), '__isProfile', 'User')
                page = self.dict_util.get_data_from_field(json.loads(box), '__isProfile', 'Page')
                user = person if person else page
                if not user:
                    continue
                user_info.update({
                    'viewer_user_id': user['viewer']['actor']['id'],
                    'userid': user['id'],
                    'name': user['name'],
                    'homepage': user['url']
                })
                break
            except Exception as e:
                continue
        return user_info

    def get_page_info(self, bboxes):
        """
        :param bboxes:
        :return: id,
        """
        page_info = {}
        for box in bboxes:
            if 'parent_feedback' not in box:
                continue
            parent_feedback = self.dict_util.get_data_from_field(json.loads(box), 'parent_feedback')
            if not parent_feedback or 'id' not in parent_feedback or 'share_fbid' not in parent_feedback:
                continue
            page_info = {
                'cursor': '',
                'id': parent_feedback['id'],
                'post_id': parent_feedback['share_fbid']
            }

        return page_info

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
        tokens = self.get_token(page_source)

        re_pattern = '\{"__bbox":\{.*?extra_context.*?\}\}'
        bboxes = re.findall(re_pattern, page_source)

        user_info = self.get_user_info(bboxes)
        page_info = self.get_page_info(bboxes)

        if not tokens or not page_info:
            return
        page_info.update({'post_url': response.request.url})
        # 如果要下一页，将任务写道redis
        self.task_manage.write_task_from_spider_name(
            self.name,
            is_first=0,
            other_raw={
                'tokens': tokens,
                'user_info': user_info,
                'page_info': page_info
            }
        )
        print('第一页over')

    def parse_graphql(self, response):
        task = json.loads(response.meta['task'])
        raw = task.get('raw')
        user_info = raw['user_info']
        page_info = raw['page_info']
        tokens = raw['tokens']
        response_json = json.loads(response.text)

        # 解析好友数据
        friends_data, requests_var_cursor, has_next_page = self.parse_share_user(
            response_json, page_info['post_id'], page_info['post_url'])

        # 写入数据库：
        self.logger.info('graphql 入库,{}'.format(task['url']))
        for f in friends_data:
            print(f['username'])
        self.task_manage.del_item("mirror:" + self.name, response.meta['task'])
        # 判断是否进行下一页：
        if not has_next_page:
            return
        page_info['cursor'] = requests_var_cursor
        # 如果要下一页，将任务写道redis
        self.task_manage.write_task_from_spider_name(
            self.name,
            is_first=0,
            other_raw={
                'tokens': tokens,
                'user_info': user_info,
                'page_info': page_info
            }
        )
        print('graphql over')

    def parse_share_user(self, share_data, post_id, post_url):
        # 解析数据相关：
        over_datas = []
        reshares = self.dict_util.get_data_from_field(share_data, 'reshares')
        for edg in reshares['edges']:
            over_data = {}
            comet_sections = self.dict_util.get_data_from_field(edg, 'comet_sections')
            if not comet_sections:
                continue
            user_data = self.dict_util.get_data_from_field(comet_sections['context_layout'], 'comet_sections')
            user = self.dict_util.get_data_from_field(user_data, '__typename', 'User')
            user = user if user else self.dict_util.get_data_from_field(user_data, '__typename', 'Page')
            if not user:
                continue
            creation_time = self.dict_util.get_data_from_field(user_data, 'creation_time')
            over_data.update({
                "post_id": post_id,
                "post_url": post_url,
                "userid": user.get('id', -1),
                "username": user.get('name', ''),
                "homepage": user.get('url', ''),
                "share_time": timestamp_to_datetime(creation_time) if creation_time else timestamp_to_datetime(0),
                "edg": edg
            })
            if over_data['userid'] == -1:
                continue
            over_datas.append(over_data)
        has_next_page = reshares['page_info']['has_next_page']
        requests_var_cursor = reshares['page_info']['end_cursor']
        return over_datas, requests_var_cursor, has_next_page


if __name__ == '__main__':
    from scrapy.cmdline import execute

    execute(('scrapy crawl ' + SpiderNames.facebook_user_friends_api).split())
