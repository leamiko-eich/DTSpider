#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/28 11:19
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : facebook.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
from PatternSpider.tasks import TaskManage
from PatternSpider.settings.spider_names import SpiderNames


class FacebookTask(TaskManage):

    def add_facebook_user_task(self, user_names):
        """
        参数解释：
        user_names，facebook用户列表
        """
        for username in user_names:
            self.write_task_from_spider_name(
                SpiderNames.facebook_user,
                username=username,
            )

    def add_facebook_user_friends_task(self, user_infos):
        """
        参数解释：
        user_names，facebook用户列表
        """
        for user_info in user_infos:
            self.write_task_from_spider_name(
                SpiderNames.facebook_user_friends,
                source_userid=user_info['source_userid'],
                source_homepage=user_info['source_homepage'],
                username=user_info['username'],
                limit_count=50,
            )

    def add_facebook_user_guess_task(self, facebook_user_guess):
        """
        参数解释：
        user_names，facebook用户列表
        """
        for guess in facebook_user_guess:
            self.write_task_from_spider_name(
                SpiderNames.facebook_user_guess,
                username=guess['username'],
                name=guess['name'],
                userid=guess['userid'],
                homepage=guess['homepage'],
                jumpname=guess['jumpname'],
                limit_count=20,
            )

    def add_facebook_post_like(self, posts):
        """
        参数解释：
        user_names，facebook用户列表
        """
        for post in posts:
            self.write_task_from_spider_name(
                SpiderNames.facebook_post_like,
                post_url="https://www.facebook.com/marvelcommunitty/posts/3205863366402624",
                post_id="3205863366402624",
                limit_count=100
            )

    def add_facebook_post_share(self, posts):
        """
        参数解释：
        user_names，facebook用户列表
        """
        for post in posts:
            self.write_task_from_spider_name(
                SpiderNames.facebook_post_share,
                post_url="https://www.facebook.com/marvelcommunitty/posts/3205863366402624",
                post_id="3205863366402624",
                limit_count=100
            )

    def add_facebook_post_comment(self, posts):
        """
        参数解释：
        user_names，facebook用户列表
        """
        for post in posts:
            self.write_task_from_spider_name(
                SpiderNames.facebook_post_comment,
                post_url="https://www.facebook.com/brennen.sanders.3/posts/4365887843438494",
                post_id="4365887843438494",
                limit_count=100
            )
