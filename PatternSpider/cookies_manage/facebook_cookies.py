#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 20:14
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : facebook_cookies.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
import json
from PatternSpider.cookies_manage import RedisCookieModel


class FacebookCookies(RedisCookieModel):
    CLIENTNAME = 'REDIS_DT'
    NAME = 'facebook_cookies'

    # 写cookie
    def write_to_redis(self, account, data: dict):
        return self.hash_set(account, json.dumps(data))

    # 获取cookie
    def get_random_username_cookie(self):
        username = self.get_random_key()
        if not username:
            return {}
        login_result = self.get_value_from_key(username)
        return {'username': username, 'login_result': json.loads(login_result)}


class FacebookAccount(RedisCookieModel):
    CLIENTNAME = 'REDIS_DT'
    NAME = 'facebook_account'

    # 写cookie
    def write_to_redis(self, account, password, key):
        infos = {
            'account': account,
            'password': password,
            'key': key,
        }
        return self.hash_set(account, json.dumps(infos))

    # 获取cookie
    def get_random_username_cookie(self):
        username = self.get_random_key()
        if not username:
            raise Exception('facebook 没有cookie了！！！')
        cookie = self.get_value_from_key(username)
        return {'username': username, 'cookie': cookie}


if __name__ == '__main__':
    # FacebookAccount().write_to_redis('+8616269456098', 'liufeifan1206', 'QWETR6KKWED5LX7A5E3RJ5QT5OJELQO3')
    FacebookAccount().write_to_redis('100069879049118', 'czSlh4rg', 'BFLEDUIK5DGPX7KMWALDBQVWBTZ7FRM3')
