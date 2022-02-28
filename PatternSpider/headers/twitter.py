#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:26
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : twitter.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
import json
import requests
from urllib.parse import urlencode
from PatternSpider.cookies_manage.twitter_cookies import TwitterCookies
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.headers import BaseHeaders


class TwitterBase(BaseHeaders):

    def __init__(self):
        self.cookie = TwitterCookies()
        self.cookie_infos = self.cookie.get_random_username_cookie()
        self.infos = json.loads(self.cookie_infos['cookie'])

    def get_headers(self, **kwargs):
        print(kwargs)
        raw = json.loads(kwargs['request'].meta['task'])['raw']
        return {
            'x-guest-token': self.infos['guest_token'],
            'authorization': self.infos['authorization'],
            'authority': 'twitter.com',
            'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
            'x-twitter-client-language': 'zh-cn',
            'sec-ch-ua-mobile': '?0',
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/97.0.4692.99 Safari/537.36',
            'x-twitter-active-user': 'yes',
            'sec-ch-ua-platform': '"Windows"',
            'accept': '*/*',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://twitter.com/'.format(raw['username']),
            'accept-language': 'zh-CN,zh;q=0.9',
        }


class TwitterUserByScreenName(TwitterBase):
    Uri = 'https://twitter.com/i/api/graphql/{}/UserByScreenName?'
    name = SpiderNames.twitter_user

    def get_url(self, **kwargs):
        params_data = {
            "variables": json.dumps({
                "screen_name": kwargs['username'],
                "withSafetyModeUserFields": "true",
                "withSuperFollowsUserFields": "true"
            })
        }
        return self.Uri.format(self.infos['user_by_screen_name']) + urlencode(params_data)


class TwitterGuess(TwitterBase):
    Uri = 'https://twitter.com/i/api/graphql/{}/UserTweets?'
    name = SpiderNames.twitter_guess

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


if __name__ == '__main__':
    username = 'Jim_Jordan'
    get_user_url = TwitterUserByScreenName().get_url(username=username)
    headers = TwitterUserByScreenName().get_headers(username=username)
    user_response = requests.get(url=get_user_url, headers=headers, verify=False)
    print(user_response)
    user_rest_id = user_response.json()['data']['user']['result']['rest_id']
    get_guess_url = TwitterGuess().get_url(userId=user_rest_id)
    get_guess_headers = TwitterGuess().get_headers(username=username)
    guess_response = requests.get(url=get_guess_url, headers=get_guess_headers, verify=False)
    print(guess_response)
