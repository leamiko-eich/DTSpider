#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/22 9:14
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : facebook_post_comment.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
import json
import re
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
from PatternSpider.servers.translate import Translate


class FacebookPostCommentSpider(RedisSpider):
    name = SpiderNames.facebook_post_comment
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
        super(FacebookPostCommentSpider, self).__init__(name=self.name)
        self.dict_util = DictUtils()
        self.facebook_util = FacebookUtils()
        self.facebook_chrome = FacebookChrome(logger=self.logger, headless=self.facebook_util.headless)
        login_res, account_status = self.facebook_chrome.login_facebook()
        # 登录失败的话，关闭爬虫
        self.login_data = {
            'login_res': login_res,
            'account_status': account_status
        }
        self.logger.info(json.dumps(self.login_data))
        time.sleep(self.facebook_util.init_sleep)

    @ding_alarm('spiders', name, logger)
    def parse(self, response):
        task = json.loads(response.meta['task'])
        self.logger.info('1 解析响应 {}'.format(task['url']))
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

        task['down_num'] = 0
        # 解析页面源码中本身中带的评论
        request = None
        re_pattern = '\{"__bbox":\{.*?extra_context.*?\}\}'
        bboxes = re.findall(re_pattern, page_source)
        if bboxes:
            bboxes_dicts = [json.loads(box) for box in bboxes]
            commments_datas, request = self.parse_comment(response, bboxes_dicts, task)
            self.logger.info('1 入库')
            for commments_data in commments_datas:
                yield commments_data
        # 开始系列点击:
        self.logger.info('开始系列点击,{}'.format(task['url']))
        first = self.go_comments_first()
        if not first:
            return self.close_current_task(task)
        time.sleep(3)
        more = self.get_comments_more()
        if not more:
            return self.close_current_task(task)
        self.logger.info('开始下次请求,{}'.format(task['url']))
        yield request if request else self.close_current_task(task)

    @ding_alarm('spiders', name, logger)
    def parse_graphql(self, response):
        task = json.loads(response.meta['task'])
        self.logger.info('开始捕获接口数据,{}'.format(task['url']))
        # 切换到标签页
        self.facebook_chrome.get_page_source_person(task['current_url_index'])
        # 点击查看更多
        more = self.get_comments_more()
        if not more:
            return self.close_current_task(task)
        time.sleep(3)
        # 获取该标签页的graphql接口数据
        graphql_data_list = self.facebook_chrome.get_graphql_data()

        guess_nodes = []
        # 获取想要的帖子 graphql 接口内容
        for comments_data in graphql_data_list:
            display_comments = self.dict_util.get_data_from_field(comments_data, 'display_comments')
            if not display_comments:
                continue
            guess_nodes.append(comments_data)
        # 获取指定响应:
        self.logger.info('解析评论,{}'.format(task['url']))
        guesses_data, request = self.parse_comment(response, guess_nodes, task)
        self.logger.info('入库,{}'.format(task['url']))
        for guess in guesses_data:
            yield guess
        self.logger.info('开始下次请求,{}'.format(task['url']))
        yield request if request else self.close_current_task(task)

    @ding_alarm('spiders', name, logger)
    def parse_comment(self, response, comments_datas, task):
        comments_count = -1
        # 解析数据
        over_datas = []
        comment_date = -1
        for comments_data in comments_datas:
            display_comments = self.dict_util.get_data_from_field(comments_data, 'display_comments')
            if not display_comments:
                continue
            comments = display_comments['edges']
            comments_count = display_comments['count']
            for comment in comments:
                node = comment['node']
                user = node['author']
                attachment = self.dict_util.get_data_from_field(node['attachments'], 'attachment')
                attach_list = self.facebook_util.parse_attache(attachment) if attachment else ""
                content = node['body']['text'] if node['body'] else ""
                node.update({
                    "comment_id": node['legacy_fbid'],
                    "comment_name": node['author']['short_name'],
                    "post_id": task['raw']['post_id'],
                    "post_url": task['raw']['post_url'],
                    "userid": user['id'],
                    "homepage": user['url'],
                    "content": content,
                    "content_cn": Translate().en_to_zh(content),
                    "comment_attach": json.dumps(attach_list) if attach_list else "",
                    "local_attach": "",
                    "comment_time": timestamp_to_datetime(node['created_time']) if node[
                        'created_time'] else timestamp_to_datetime(0),
                })
                over_datas.append(node)
                comment_date = node['comment_time'] if node['comment_time'] != timestamp_to_datetime(0) else -1

        # 下一次请求策略
        is_next, task = self.facebook_util.is_next_request(
            task, len(over_datas), feed_count=comments_count, creation_time=comment_date
        )
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
    def go_comments_first(self):
        # 点击最相关：
        flag = False
        spans = self.facebook_chrome.driver.find_elements_by_xpath(
            "//span[@class='d2edcug0 hpfvmrgz qv66sw1b c1et5uql oi732d6d ik7dh3pa ht8s03o8 a8c37x1j fe6kdd0r mau55g9w c8b282yb keod5gw0 nxhoafnm aigsh9s9 d3f4x2em iv3no6db jq4qci2q a3bd9o3v lrazzd5p m9osqain']")
        for span in spans:
            if span.text == "最相關" or span.text == "最相关":
                flag = True
                span.click()
                break
        if not flag:
            return False

        # 点击所有评论
        all_comment_spans = self.facebook_chrome.driver.find_elements_by_xpath(
            "//span[@class='d2edcug0 hpfvmrgz qv66sw1b c1et5uql oi732d6d ik7dh3pa ht8s03o8 a8c37x1j fe6kdd0r mau55g9w c8b282yb keod5gw0 nxhoafnm aigsh9s9 d3f4x2em iv3no6db jq4qci2q a3bd9o3v ekzkrbhg oo9gr5id hzawbc8m']")
        for all_comment in all_comment_spans:
            if all_comment.text == "所有留言":
                all_comment.click()
                return True
        return False

    @ding_alarm('spiders', name, logger)
    def get_comments_more(self):
        # 点击查看更多
        look_mores = self.facebook_chrome.driver.find_elements_by_xpath(
            "//span[@class='d2edcug0 hpfvmrgz qv66sw1b c1et5uql oi732d6d ik7dh3pa ht8s03o8 a8c37x1j fe6kdd0r mau55g9w c8b282yb keod5gw0 nxhoafnm aigsh9s9 d3f4x2em iv3no6db jq4qci2q a3bd9o3v lrazzd5p m9osqain']")
        print(look_mores)
        for look_more in look_mores:
            if look_more.text == "查看更多留言" or "檢視另" in look_more.text:
                self.make_element_into_view(look_more)
                look_more.click()
                try:
                    comment_position = self.facebook_chrome.driver.find_element_by_xpath(
                        "//div[@class='rj1gh0hx buofh1pr ni8dbmo4 stjgntxs hv4rvrfc']")
                    comment_position.click() if comment_position else None
                except:
                    pass
                return True
        return False

    @ding_alarm('spiders', name, logger)
    def make_element_into_view(self, element):
        location_y = element.location_once_scrolled_into_view['y']
        while location_y < 100 or location_y > 500:
            if location_y < 100:
                self.facebook_chrome.scroll_up()
            elif location_y > 500:
                self.facebook_chrome.scroll_down()
            location_y = element.location_once_scrolled_into_view['y']

    def close_current_task(self, task, task_status=2):
        """
        :param task: 请求头中配置的任务参数
        """
        # 关闭当前页
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

    execute(('scrapy crawl ' + SpiderNames.facebook_post_comment).split())
