#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/28 11:19
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : flickr.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
from PatternSpider.tasks import TaskManage
from PatternSpider.settings.spider_names import SpiderNames


class FlickrTask(TaskManage):
    def add_flickr_guess_task(self):
        self.write_task_from_spider_name(
            SpiderNames.flickr_guess,
            per_page=100,
            page=69
        )
