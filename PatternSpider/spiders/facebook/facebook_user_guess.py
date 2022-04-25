#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 18:41
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : facebook_user_guess.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
import json
import re
import time

import scrapy

from PatternSpider.scrapy_redis.spiders import RedisSpider
from PatternSpider.servers.ding_talk_server import ding_alarm
from PatternSpider.servers.translate import Translate
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.tasks import TaskManage
from PatternSpider.selenium_manage.base_chrome import FacebookChrome
from PatternSpider.utils.logger_utils import get_logger
from PatternSpider.utils.dict_utils import DictUtils
from PatternSpider.utils.time_utils import timestamp_to_datetime
from PatternSpider.spiders.facebook import FacebookUtils


class FacebookUserGuessSpider(RedisSpider):
    name = SpiderNames.facebook_user_guess
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
        super(FacebookUserGuessSpider, self).__init__(name=self.name)
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

    @ding_alarm('spiders', name, logger)
    def parse(self, response):
        time.sleep(self.facebook_util.init_sleep)
        task = json.loads(response.meta['task'])
        self.logger.info('第一次响应解析,{}'.format(task['url']))
        # 更新当前被采集对象为进行时
        self.facebook_util.update_current_user_status(task, 1)

        # 如果访问超时再加一个状态：
        if not task["middlewares_status"]:
            return self.close_current_task(task, 5)

        # 解析数据
        page_source = self.facebook_chrome.get_page_source_person(task['current_url_index'])
        # 加一个访问当前主页的状态，如果当前页无法访问直接结束
        result = self.facebook_util.check_pagesource(page_source)
        if not result:
            return self.close_current_task(task, 4)

        # 如果没有帖子直接返回：
        if "No posts available" in page_source:
            return self.close_current_task(task)

        self.logger.info('第一次数据开始解析,{}'.format(task['url']))
        re_pattern = '\{"__bbox":\{.*?extra_context.*?\}\}'
        bboxes = re.findall(re_pattern, page_source)
        if not bboxes:
            return self.close_current_task(task)

        task['user_info'] = self.facebook_util.get_user_info(bboxes)
        bboxes_dicts = [json.loads(box) for box in bboxes]
        guess_nodes = []
        for bbox in bboxes_dicts:
            # 公共主页
            timeline_feed_units = self.dict_util.get_data_from_field(bbox, 'timeline_feed_units')
            if timeline_feed_units:
                guess_nodes.append(timeline_feed_units['edges'][0]['node'])
            # 个人页
            timeline_list_feed_units = self.dict_util.get_data_from_field(bbox, 'timeline_list_feed_units')
            if timeline_list_feed_units:
                if not timeline_list_feed_units['edges']:
                    continue
                guess_nodes.append(timeline_list_feed_units['edges'][0]['node'])

        guesses_data, request = self.parse_guess(response, guess_nodes, task, True)
        self.logger.info('第一次数据入库,{}'.format(task['url']))
        for guess in guesses_data:
            yield guess
        self.logger.info('第二次请求开始,{}'.format(task['url']))
        yield request if request else self.close_current_task(task)

    @ding_alarm('spiders', name, logger)
    def parse_graphql(self, response):
        task = json.loads(response.meta['task'])
        self.logger.info('开始获取接口数据,{}'.format(task['url']))
        # 切换到标签页
        self.facebook_chrome.get_page_source_person(task['current_url_index'])
        # 获取该标签页的graphql接口数据
        graphql_data_list = self.facebook_chrome.get_graphql_data()

        guess_nodes = []
        # 获取想要的帖子 graphql 接口内容
        for guess_data in graphql_data_list:
            # 个人页
            timeline_list_feed_units = self.dict_util.get_data_from_field(guess_data, 'timeline_list_feed_units')
            if timeline_list_feed_units:
                guess_nodes += timeline_list_feed_units['edges']
            # 公共主页
            timeline_feed_units = self.dict_util.get_data_from_field(guess_data, 'timeline_feed_units')
            if timeline_feed_units:
                guess_nodes += timeline_feed_units['edges']

            if 'label' in guess_data and guess_data['label'] == 'ProfileCometTimelineFeed_user$stream$Pr' \
                                                                'ofileCometTimelineFeed_user_timeline_list_feed_units':
                guess_nodes.append(guess_data['data']['node'])

        # 获取指定响应:
        self.logger.info('开始解析数据,{}'.format(task['url']))
        guesses_data, request = self.parse_guess(response, guess_nodes, task)
        self.logger.info('入库,{}'.format(task['url']))
        for guess in guesses_data:
            yield guess
        self.logger.info('开始下一次请求,{}'.format(task['url']))
        yield request if request else self.close_current_task(task)

    @ding_alarm('spiders', name, logger)
    def parse_guess(self, response, guess_nodes, task, enforce_next=False):
        # 解析数据：
        creation_time = -1
        over_datas = []
        for node in guess_nodes:
            comet_sections = self.dict_util.get_data_from_field(node, 'comet_sections')
            story = comet_sections['content']['story']
            context_layout = comet_sections['context_layout']
            # 帖子网址
            post_url = story['wwwURL']
            # 帖子id：
            datasource = self.dict_util.get_data_from_field(node, 'mentions_datasource_js_constructor_args_json')
            if datasource and type(datasource) == str:
                post_id = self.dict_util.get_data_from_field(json.loads(datasource), 'post_fbid')
            else:
                post_id = None
            post_id = post_id if post_id else post_url.split('/')[-1]
            post_id = str(post_id).split(':')[0]
            # 创建时间
            creation_time = self.dict_util.get_data_from_field(context_layout, 'creation_time')
            creation_time = timestamp_to_datetime(creation_time) if creation_time else timestamp_to_datetime('0')
            # 发帖人头像网址
            profile_pic_dict = self.dict_util.get_data_from_field(comet_sections, 'profile_picture')
            # 帖子内容和附件
            # 内容解析
            content = self.dict_util.get_data_from_field(story['comet_sections']['message'], 'text')
            # 附件解析
            attachment = self.dict_util.get_data_from_field(story['attachments'], 'attachment')
            attach_list = self.facebook_util.parse_attache(attachment)

            # 判断是分享贴
            attached_story_user = story['comet_sections']['attached_story']
            attached_story_attachment = story['attached_story']
            share_guess_data = self.parse_share_guess(attached_story_user, attached_story_attachment)

            node.update({
                "userid": task['user_info'].get("userid", 0),
                "homepage": task['raw'].get("homepage", ""),
                "name": task['user_info'].get("name", ""),
                "jumpname": task['raw'].get("homepage", "").replace("https://www.facebook.com/", ""),
                'object_type': task['raw']['total_task_infos']['user_info']['object_type'],
                'object_number': task['raw']['total_task_infos']['user_info']['object_number'],

                "post_id": post_id,
                "post_url": post_url.replace('\\', '') if post_url else '',
                "location": '',
                "longitude": '',
                "latitude": '',
                "comment_count": '',
                "share_count": '',
                "like_count": '',

                "title": "",
                "content": content if content else '',
                "content_cn": Translate().en_to_zh(content),
                "profile_picture_url": profile_pic_dict.get('uri', '').replace('\\', '') if profile_pic_dict else '',
                "post_time": creation_time if creation_time else '',
                "post_attach": json.dumps(attach_list) if attach_list else '',
                "post_local_attach": '',

                "is_shared": share_guess_data.get('is_shared', 0),
                "share_userid": share_guess_data.get('share_userid', ''),
                "share_username": share_guess_data.get('share_username', ''),
                "share_jumpname": share_guess_data.get('share_jumpname', ''),
                "share_user_homepage": share_guess_data.get('share_user_homepage', '').replace('\\', ''),
                "share_post_url": share_guess_data.get('share_post_url', '').replace('\\', ''),
                "share_post_time": share_guess_data.get('share_post_time', ''),
                "share_title": "",
                "share_content": share_guess_data.get('share_content', ''),
                "share_content_cn": Translate().en_to_zh(share_guess_data.get('share_content', '')),
                "share_post_attach": share_guess_data.get('share_post_attach', ''),
                "share_post_local_attach": '',
            })
            over_datas.append(node)

        # 下一页请求判断
        is_next, task = self.facebook_util.is_next_request(task, len(over_datas), creation_time=creation_time)
        is_next = True if enforce_next else is_next
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

    @ding_alarm('spiders', name, logger)
    def parse_share_guess(self, attached_story_user, attached_story_attachment):
        if attached_story_user and attached_story_attachment:
            user = self.dict_util.get_data_from_field(attached_story_user, '__typename', 'User')
            page = self.dict_util.get_data_from_field(attached_story_user, '__typename', 'Page')
            if not user and not page:
                return {}
            share_user_info = user if user else page
            share_user_homepage = share_user_info['url'] if share_user_info and 'url' in share_user_info else ''
            share_attachment = self.dict_util.get_data_from_field(attached_story_attachment, 'attachment')
            share_content = self.dict_util.get_data_from_field(attached_story_attachment, 'text')
            share_post_attach = self.facebook_util.parse_attache(share_attachment)
            creation_time = self.dict_util.get_data_from_field(attached_story_user, 'creation_time')
            creation_time = timestamp_to_datetime(creation_time) if creation_time else timestamp_to_datetime("0")
            return dict(
                is_shared=1,
                share_userid=share_user_info['id'] if share_user_info and 'id' in share_user_info else 0,
                share_username=share_user_info['name'] if share_user_info and 'name' in share_user_info else '',
                share_user_homepage=share_user_homepage,
                share_jumpname=share_user_homepage.replace('https://www.facebook.com/', ''),
                share_post_url=attached_story_attachment['wwwURL'] if 'wwwURL' in attached_story_attachment else '',
                share_post_time=creation_time,
                share_content=share_content if share_content else '',
                share_post_attach=json.dumps(share_post_attach) if share_post_attach else "",
            )
        return {}

    @ding_alarm('spiders', name, logger)
    def close_current_task(self, task, task_status=2):
        """
        :param task: 请求头中配置的任务参数
        :param task_status: 当前被采集对象的采集结果 2 成功 3 采集失败 4 访问失败 5访问超时
        """
        # 关闭当前页
        self.logger.info('关闭当前页,{},status:{}'.format(task['url'], task_status))
        # 更新当前被采集对象为完成
        self.facebook_util.update_current_user_status(task, task_status)
        orgin_task = {'url': task['url'], 'raw': task['raw']}
        self.task_manage.del_item("mirror:" + self.name, json.dumps(orgin_task, ensure_ascii=False))
        try:
            self.facebook_chrome.get_handle(task['current_url_index'])
            self.facebook_chrome.driver.close()
            self.facebook_chrome.get_handle(0)
        except:
            self.facebook_chrome.get_handle(0)


if __name__ == '__main__':
    from scrapy.cmdline import execute

    execute(('scrapy crawl ' + SpiderNames.facebook_user_guess).split())
