#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/4/22 16:48
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : deagel.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved

from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.tasks import TaskManage


class DeagelTask(TaskManage):

    def add_deagel_equipment_dir_task(self):
        self.write_task_from_spider_name(
            SpiderNames.deagel_equipment_directories,
        )

    def add_deagel_country_list_task(self):
        self.write_task_from_spider_name(
            SpiderNames.deagel_country_list,
        )

    def add_deagel_reports_list_task(self):
        self.write_task_from_spider_name(
            SpiderNames.deagel_reports_list,
        )

    def add_deagel_news_list_task(self):
        self.write_task_from_spider_name(
            SpiderNames.deagel_news_list,
            page=1
        )

    def add_deagel_gallery_list_task(self):
        self.write_task_from_spider_name(
            SpiderNames.deagel_gallery_list,
            page=1
        )


if __name__ == '__main__':
    # DeagelTask().add_deagel_news_list_task()
    DeagelTask().add_deagel_gallery_list_task()
