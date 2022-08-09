#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/4/11 16:38
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : facebook_api.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.headers import BaseHeaders


class FacebookApiBase(BaseHeaders):
    fb_api_req_friendly_name = ''

    def get_headers(self, **kwargs):
        cookies = {
            'datr': 'FLgNYnyn5--WJqVG9wUSh9os',
            'sb': 'FLgNYnFMWojvh8COCzqxKxMt',
            'c_user': '100069879049118',
            'dpr': '1.5',
            'presence': 'C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1650017919521%2C%22v%22%3A1%7D',
            'xs': '20%3AIWuy4T0oTLyeXg%3A2%3A1649209107%3A-1%3A7613%3A%3AAcWJxF7yhGVzmkRL5Aj8vXgM62qXO2Q5sAcM1PGCsA',
            'fr': '0kFl8fqKia0BnEgFw.AWXMkL2AKBB-7KVE_NISVDs5H9g.BiWUZ-.A_.AAA.0.0.BiWUaB.AWWAeQgDgxY',
        }
        is_api = kwargs.get('is_api')
        if is_api:
            lsd_token = kwargs.get('lsd_token')
            referer = kwargs.get('referer')
            return {
                'authority': 'www.facebook.com',
                'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
                'sec-ch-ua-mobile': '?0',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36',
                'viewport-width': '1280',
                'x-fb-friendly-name': self.fb_api_req_friendly_name,
                'x-fb-lsd': lsd_token,
                'sec-ch-prefers-color-scheme': 'light',
                'sec-ch-ua-platform': '"Windows"',
                'accept': '*/*',
                'origin': 'https://www.facebook.com',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': referer,
                'accept-language': 'zh-CN,zh;q=0.9',
                'cookies': cookies
            }
        return {
            'authority': 'www.facebook.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'viewport-width': '853',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-prefers-color-scheme': 'light',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cookies': cookies
        }


class FacebookUserFriendsApi(FacebookApiBase):
    """
    需要的字段：
        :is_first  是否是第一页
        :username  参数必传
        :

    """
    Uri = 'https://www.facebook.com/{}/friends'
    name = SpiderNames.facebook_user_friends_api
    fb_api_req_friendly_name = 'ProfileCometAppCollectionListRendererPaginationQuery'

    def get_url(self, **kwargs):
        is_first = kwargs.get('is_first')
        if is_first:
            if "profile.php" in kwargs['username']:
                return "https://www.facebook.com/{}&sk=friends".format(kwargs['username'])
            return self.Uri.format(kwargs['username'])
        return 'https://www.facebook.com/api/graphql/'

    def get_payload(self, **kwargs):
        raw = kwargs.get('raw')
        user_info = raw['user_info']
        tokens = raw['tokens']
        page_info = raw['page_info']
        return {
            'av': user_info['viewer_user_id'],
            '__user': user_info['viewer_user_id'],
            '__a': '1',
            '__hs': '19087.HYP:comet_pkg.2.1.0.2.',
            'dpr': '1.5',
            '__rev': '1005298160',
            '__comet_req': '1',
            'fb_dtsg': tokens['DTSGInitialData'],
            'lsd': tokens['LSD'],
            '__spin_r': '1005298160',
            '__spin_b': 'trunk',
            '__spin_t': '1649149771',
            'fb_api_caller_class': 'RelayModern',
            'fb_api_req_friendly_name': self.fb_api_req_friendly_name,
            'variables': '{"count":8,"cursor":"%s","scale":1.5,"search":null,"id":"%s"}' % (
                page_info['cursor'], page_info['id']),
            'server_timestamps': 'true',
            'doc_id': '4416316901802282',
        }


class FacebookPostShareApi(FacebookApiBase):
    """
    :param
        is_frist 是否是第一页
        post_url  必传
        viewer_user_id 拜访者id
        tokens 两个token
        page_info 页面源码信息
    """
    name = SpiderNames.facebook_post_share_api
    fb_api_req_friendly_name = "CometResharesFeedPaginationQuery"

    def get_url(self, **kwargs):
        is_first = kwargs.get('is_first')
        if is_first:
            return kwargs.get('post_url')
        return 'https://www.facebook.com/api/graphql/'

    def get_payload(self, **kwargs):
        raw = kwargs.get('raw')
        user_info = raw['user_info']
        tokens = raw['tokens']
        page_info = raw['page_info']
        return {
            'av': user_info['viewer_user_id'],
            '__user': user_info['viewer_user_id'],
            'fb_dtsg': tokens['DTSGInitialData'],
            'lsd': tokens['LSD'],
            'variables': '{"cursor":"%s","id":"%s","privacySelectorRenderLocation":"COMET_STREAM","scale":1.5,}' % (
                page_info['cursor'], page_info['id']),
            'server_timestamps': 'true',
            'doc_id': '5056909857722188',
        }
