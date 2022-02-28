#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/28 11:19
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : twitter.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.tasks import TaskManage
from PatternSpider.models.mongo_model import MongoTwitterUser


class TwitterTask(TaskManage):

    def add_twitter_user_task(self, user_names, spider_type=1, time_limit_second=86400):
        """
        参数解释：
        user_names，twitter用户名列表
        spider_type, 默认 1   (0:只采集用户信息，1：用户信息+帖子，....)
        """
        mongo_twitter_user = MongoTwitterUser()
        for username in user_names:
            user_data = mongo_twitter_user.find_one_data({'username': username})
            if not user_data:
                self.write_task_from_spider_name(
                    SpiderNames.twitter_user,
                    username=username,
                    spider_type=spider_type
                )

        for username in user_names:
            self.write_task_from_spider_name(
                SpiderNames.twitter_user,
                username=username,
                spider_type=spider_type,
                time_limit_second=time_limit_second,
            )
