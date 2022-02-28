#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/28 11:19
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : dvidshub.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.tasks import TaskManage


class DvidshubTask(TaskManage):
    def add_dvidshub_search_task(self):
        self.write_task_from_spider_name(
            SpiderNames.dvidshub_search,
            other_raw={
                "q": "",
                "filter[type]": "image",
                "filter[tags][0]": "coastguardnewswire",
                "view": 'grid',
                "sort": "date",
            },
            page="1",
        )


if __name__ == '__main__':
    DvidshubTask().add_dvidshub_search_task()
