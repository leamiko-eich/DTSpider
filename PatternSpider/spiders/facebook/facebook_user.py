#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 18:39
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : facebook_user.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
import json
import re
import time

from PatternSpider.scrapy_redis.spiders import RedisSpider
from PatternSpider.servers.ding_talk_server import ding_alarm
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.tasks import TaskManage
from PatternSpider.selenium_manage.base_chrome import FacebookChrome
from PatternSpider.utils.logger_utils import get_logger
from PatternSpider.utils.dict_utils import DictUtils
from PatternSpider.spiders.facebook import FacebookUtils


class FacebookUserSpider(RedisSpider):
    name = SpiderNames.facebook_user
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
        super(FacebookUserSpider, self).__init__(name=self.name)
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
        self.logger.info('1 解析响应')
        task = json.loads(response.meta['task'])
        self.facebook_util.update_current_user_status(task, 1)

        # 如果访问超时再加一个状态：
        if not task["middlewares_status"]:
            return self.close_current_task(task, 5)

        page_source = self.facebook_chrome.get_page_source_person(task['current_url_index'])
        result = self.facebook_util.check_pagesource(page_source)
        if not result:
            # 更新当前被采集对象为完成
            self.logger.info('当前页面无法访问')
            return self.close_current_task(task, 4)

        self.logger.info('开始解析数据')
        over_data = {
            'object_type': task['raw']['total_task_infos']['user_info']['object_type'],
            'object_number': task['raw']['total_task_infos']['user_info']['object_number'],
            'homepage': "https://www.facebook.com/{}".format(task['raw']['username']),
            'jumpname': task['raw']['username']

        }
        re_pattern = '\{"__bbox":\{.*?extra_context.*?\}\}'
        bboxes = re.findall(re_pattern, page_source)
        for box in bboxes:
            if 'profile_social_context' in box:
                user = self.dict_util.get_data_from_field(json.loads(box), '__isProfile', 'User')
                friends_count = self.dict_util.get_data_from_field(user['profile_social_context'], 'text')
                friends_count = friends_count['text'] if type(friends_count) == dict else friends_count
                over_data.update({
                    'userid': user['id'],
                    'name': user['name'],
                    'avatar': user['profilePicLarge']['uri'],
                    'gender': user['gender'],
                    'friends_count': friends_count
                })
            if 'field_type' in box:
                profile_fields = self.dict_util.get_data_from_field(json.loads(box), 'profile_fields')
                work = self.dict_util.get_data_from_field(profile_fields, 'field_type', 'work')
                education = self.dict_util.get_data_from_field(profile_fields, 'field_type', 'education')
                current_city = self.dict_util.get_data_from_field(profile_fields, 'field_type', 'current_city')
                hometown = self.dict_util.get_data_from_field(profile_fields, 'field_type', 'hometown')
                relationship = self.dict_util.get_data_from_field(profile_fields, 'field_type', 'relationship')
                relationship_text_content = self.dict_util.get_data_from_field(relationship, 'text_content')
                if relationship_text_content:
                    relationship_text = relationship_text_content['text']
                else:
                    relationship_text = relationship['title']['text'] if relationship else ""

                over_data.update({
                    'work': work['title']['text'] if work else "",
                    'education': education['title']['text'] if education else "",
                    'current_city': current_city['title']['text'] if current_city else "",
                    'hometown': hometown['title']['text'] if hometown else "",
                    'relationship': relationship_text,
                })

        about_pages = [
            ("about_overview", "overview"),
            ("about_work_and_education", "work_and_edu"),
            ("about_places", "places"),
            ("about_contact_and_basic_info", "contact_and_basicinfo"),
            ("about_life_events", "life_events"),
            ("about_family_and_relationships", "family_and_relations"),
            ("about_details", "details")
        ]

        homepage = task['raw']['total_task_infos']['user_info']['homepage']
        for page in about_pages:
            page_url = homepage + '&sk=' + page[0] if "profile.php" in homepage else homepage + '/' + page[0]
            over_data[page[1]] = self.parse_other_page(page_url, task['current_url_index'])

        yield over_data if 'userid' in over_data else None
        task_status = 2 if 'userid' in over_data else 5
        # 更新当前被采集对象为完成
        self.logger.info('当前账号采集正常结束')
        self.close_current_task(task, task_status)

    def parse_other_page(self, page_url, current_url_index):
        self.facebook_chrome.driver.get(page_url)
        self.facebook_chrome.get_page_source_person(current_url_index)
        try:
            div = self.facebook_chrome.driver.find_element_by_xpath(
                "//div[@class='dati1w0a tu1s4ah4 f7vcsfb0 discj3wi']")
            result = div.text.replace("'", "\\'")
        except Exception as e:
            print(e)
            result = ""
        return result

    @ding_alarm("spiders", name, logger)
    def close_current_task(self, task, task_status=2):
        self.logger.info('关闭当前页,{}'.format(task['url']))
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

    execute(('scrapy crawl ' + SpiderNames.facebook_user).split())
