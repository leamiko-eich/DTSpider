#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:24
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : twitter_cookies.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
import json
import re
import requests
from PatternSpider.cookies_manage import RedisCookieModel


def get_infos():
    url = "https://abs.twimg.com/responsive-web/client-web/main.8644ab25.js"
    print('开始获取infos')
    response = requests.get(url, verify=False)
    authorization = "Bearer " + re.search("(AAAAA.*?)\"", response.text).group(1)
    user_tweets = re.search('queryId:\"(.{22})\",operationName:\"UserTweets\",', response.text).group(1)
    user_by_screen_name = re.search('queryId:\"(.{22})\",operationName:\"UserByScreenName\",', response.text).group(
        1)
    gt_headers = {
        'authority': 'api.twitter.com',
        'content-length': '0',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
        'x-twitter-client-language': 'zh-cn',
        'sec-ch-ua-mobile': '?0',
        'authorization': authorization,
        'content-type': 'application/x-www-form-urlencoded',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/97.0.4692.99 Safari/537.36',
        'x-twitter-active-user': 'yes',
        'sec-ch-ua-platform': '"Windows"',
        'accept': '*/*',
        'origin': 'https://twitter.com',
        'sec-fetch-site': 'same-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://twitter.com/',
        'accept-language': 'zh-CN,zh;q=0.9',
    }
    print('开始获取guest_token...')
    response_gt = requests.post('https://api.twitter.com/1.1/guest/activate.json', headers=gt_headers, verify=False)
    return dict(
        guest_token=response_gt.json()['guest_token'],
        authorization=authorization,
        user_tweets=user_tweets,
        user_by_screen_name=user_by_screen_name
    )


class TwitterCookies(RedisCookieModel):
    CLIENTNAME = 'REDIS_DT'
    NAME = 'twitter_tourists'

    # 写cookie
    def write_to_redis(self):
        infos = get_infos()
        return self.hash_set('tourists', json.dumps(infos))

    # 获取cookie
    def get_random_username_cookie(self):
        username = self.get_random_key()
        if not username:
            self.write_to_redis()
            return self.get_random_username_cookie()
        else:
            cookie = self.get_value_from_key(username)
            return {'username': username, 'cookie': cookie}


if __name__ == '__main__':
    TwitterCookies().write_to_redis()
