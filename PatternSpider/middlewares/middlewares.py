#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:29
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : middlewares.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved

# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import json
import traceback
import requests
from scrapy.http import HtmlResponse as Response
from scrapy.utils.project import get_project_settings
from PatternSpider.headers import get_headers_from_spider_name
from PatternSpider.utils.js_utils import JsSentence
from PatternSpider.servers.ding_talk_server import DingTalk

settings = get_project_settings()


class RandomUserAgentMiddleware(object):
    # This middleware mainly modifies the request header of the request
    def process_request(self, request, spider):
        headers = get_headers_from_spider_name(spider.name, request=request)
        for i in headers:
            if i == 'cookies':
                request.cookies = headers[i]
            else:
                request.headers[i] = headers[i]


class RandomProxyMiddleware(object):
    # This middleware mainly modifies the proxy of the request
    def process_request(self, request, spider):
        proxy = settings.get("PROXY")
        h = request.url.split(':')[0]
        if h == 'http':
            request.meta['proxy'] = 'http://' + proxy
        else:
            request.meta['proxy'] = 'https://' + proxy


class RequestsMiddleware(object):
    # When encountering a request that the scrapy request cannot access, use requests to send a request
    def process_request(self, request, spider):
        try:
            method = request.method
            url = request.url
            proxy = request.meta['proxy'] if "proxy" in request.meta else ""
            if proxy:
                ip = proxy.split('://')[1]
                proxies = {
                    'http': 'http://' + ip,
                    'https': 'https://' + ip
                }
            else:
                proxies = {}
            raw = json.loads(request.meta['task'])['raw']
            headers = get_headers_from_spider_name(spider.name, request_url=request.url, raw=raw)

            if 'cookies' in headers:
                cookies = headers.pop('cookies')
                Cookie = ''
                for i in cookies:
                    Cookie += '{}={};'.format(i, cookies[i])
                headers['Cookie'] = Cookie
            body = request.body.decode()
            if method == "POST":
                r = requests.post(url, headers=headers, data=body, proxies=proxies)
            else:
                assert method == "GET"
                r = requests.get(url, headers=headers, proxies=proxies)
            r.encoding = 'utf-8'
            try:
                cookie_username = r.request.headers['cookie_username']
            except:
                cookie_username = ''
            response = Response(url=r.url, status=r.status_code, body=r.content,
                                encoding=request.encoding, headers={'cookie_username': cookie_username},
                                request=r.request)
            return response
        except:
            DingTalk().send_msg('当前爬虫为：' + spider.name + '\n异常信息：\n {}'.format(traceback.format_exc()))


class SeleniumMiddleware(object):
    def process_request(self, request, spider):
        # 获取meta数据，并将当前标签页的索引放入task中，以便于spider的解析
        task = json.loads(request.meta['task'])
        try:
            if 'current_url_index' not in task:
                # 先切换到首页再打开新的窗口，防止其他窗口被关闭后无法执行js语句
                spider.facebook_chrome.get_handle(0)
                # 打开新的标签页
                spider.facebook_chrome.driver.execute_script(JsSentence.open_new_label.format(request.url))
                # 获取当前标签页的索引
                current_url_index = spider.facebook_chrome.driver.window_handles[-1]
            else:
                current_url_index = task['current_url_index']
                # 获取当前窗口
                spider.facebook_chrome.get_handle(current_url_index)
                # 下拉
                spider.facebook_chrome.scroll_by_key(task)
            # 获取首页源代码 防止等待
            origin_code = spider.facebook_chrome.get_page_source(0)
            task['current_url_index'] = current_url_index
            request.meta['task'] = json.dumps(task)
            task["middlewares_status"] = 1
            # 终止下载器下载，直接返回响应
            res = Response(url=request.url, encoding='utf8', body=origin_code, request=request)
        except Exception as e:
            error = "current spider is {}：\n middlewares error info is : {}".format(spider.name, traceback.format_exc())
            DingTalk().send_msg(error)
            task["middlewares_status"] = 0
            request.meta['task'] = json.dumps(task)
            return Response(url=request.url, encoding='utf8', body="", request=request)
        return res
