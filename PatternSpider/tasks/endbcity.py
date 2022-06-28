#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/4/29 14:18
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : endbcity.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.tasks import TaskManage


class EnDBCityTask(TaskManage):
    def add_endbcity_task(self):
        self.write_task_from_spider_name(
            SpiderNames.endbcity,
        )


if __name__ == '__main__':
    EnDBCityTask().add_endbcity_task()
