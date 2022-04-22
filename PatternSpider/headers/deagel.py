#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/4/19 10:08
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : deagel.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
import json
import requests
from urllib.parse import urlencode
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.headers import BaseHeaders


class DeagelBase(BaseHeaders):

    def get_headers(self, **kwargs):
        return {
            'authority': 'deagel.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'referer': 'https://deagel.com/',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'
        }


class EquipmentDirectories(DeagelBase):
    Uri = 'https://deagel.com/api/directories'
    name = SpiderNames.deagel_equipment_directories


class EquipmentList(DeagelBase):
    Uri = 'https://deagel.com/api/directoryContent/{}'
    name = SpiderNames.deagel_equipment_list


class Equipment(DeagelBase):
    Uri = 'https://deagel.com/api/equipment/{}'
    name = SpiderNames.deagel_equipment

    def get_url(self, **kwargs):
        equipment_id = kwargs['equipment_id']
        return self.Uri.format(equipment_id)



class Countries(DeagelBase):
    Uri = 'https://twitter.com/i/api/graphql/{}/UserTweets?'
    name = SpiderNames.deagel_countries

    def get_url(self, **kwargs):
        variables = {
            "userId": kwargs['userId'],
            "count": kwargs['count'] if 'conut' in kwargs else 40,
            "includePromotedContent": "true",
            "withQuickPromoteEligibilityTweetFields": "true",
            "withSuperFollowsUserFields": "true",
            "withBirdwatchPivots": "false",
            "withDownvotePerspective": "false",
            "withReactionsMetadata": "false",
            "withReactionsPerspective": "false",
            "withSuperFollowsTweetFields": "true",
            "withVoice": "true",
            "withV2Timeline": "false",
            "__fs_interactive_text": "false",
            "__fs_dont_mention_me_view_api_enabled": "false"
        }
        if 'cursor' in kwargs:
            variables.update({'cursor': kwargs['cursor']})
        params_data = {"variables": json.dumps(variables)}
        url = self.Uri.format(self.infos['user_tweets']) + urlencode(params_data)
        return url


class Reports(DeagelBase):
    Uri = 'https://twitter.com/i/api/graphql/{}/UserTweets?'
    name = SpiderNames.deagel_reports


class News(DeagelBase):
    Uri = 'https://twitter.com/i/api/graphql/{}/UserTweets?'
    name = SpiderNames.deagel_news


class Gallery(DeagelBase):
    Uri = 'https://twitter.com/i/api/graphql/{}/UserTweets?'
    name = SpiderNames.deagel_gallery
