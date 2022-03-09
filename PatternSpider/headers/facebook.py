#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:26
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : facebook.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.headers import BaseHeaders


class FacebookBase(BaseHeaders):
    pass


class FacebookUserSpider(FacebookBase):
    Uri = 'https://www.facebook.com/{}/about'
    name = SpiderNames.facebook_user

    def get_url(self, **kwargs):
        if "profile.php" in kwargs['username']:
            return "https://www.facebook.com/{}&sk=about".format(kwargs['username'])
        return self.Uri.format(kwargs['username'])


class FacebookUserFriendsSpider(FacebookBase):
    Uri = 'https://www.facebook.com/{}/friends'
    name = SpiderNames.facebook_user_friends

    def get_url(self, **kwargs):
        if "profile.php" in kwargs['username']:
            return "https://www.facebook.com/{}&sk=friends".format(kwargs['username'])
        return self.Uri.format(kwargs['username'])


class FacebookUserGuessSpider(FacebookBase):
    Uri = 'https://www.facebook.com/{}'
    name = SpiderNames.facebook_user_guess

    def get_url(self, **kwargs):
        return self.Uri.format(kwargs['username'])


class FacebookPostLikeSpider(FacebookBase):
    name = SpiderNames.facebook_post_like

    def get_url(self, **kwargs):
        return kwargs['post_url']


class FacebookPostShareSpider(FacebookBase):
    name = SpiderNames.facebook_post_share

    def get_url(self, **kwargs):
        return kwargs['post_url']


class FacebookPostCommentSpider(FacebookBase):
    name = SpiderNames.facebook_post_comment

    def get_url(self, **kwargs):
        return kwargs['post_url']
