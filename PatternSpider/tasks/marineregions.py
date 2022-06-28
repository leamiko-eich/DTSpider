#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/4/28 9:57
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : marineregions.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
import pymongo

from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.tasks import TaskManage


class MarineregionsTask(TaskManage):
    def add_marineregions_list_task(self):
        self.write_task_from_spider_name(
            SpiderNames.marineregions_list,
        )

    def add_marineregions_detail_task(self):
        marineregions = pymongo.MongoClient()['marineregions']
        marineregions_list = marineregions['list']
        datas = marineregions_list.find({})
        for data in datas:
            self.write_task_from_spider_name(
                SpiderNames.marineregions_detail,
                path_url=data['href'],
                id=data['id']
            )


if __name__ == '__main__':
    MarineregionsTask().add_marineregions_detail_task()
