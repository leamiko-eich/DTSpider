#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/3/1 16:25
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : spider_client.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
from PatternSpider.tasks.facebook import FacebookTask
from scrapy.cmdline import execute


class SpiderClient:
    def run_facebook(self, mode, account_id, code, group_id):
        # 添加任务
        spider_name = FacebookTask().add_task_from_msyql(mode, account_id, code, group_id)
        # 开启爬虫
        execute(('scrapy crawl ' + spider_name).split())

    @staticmethod
    def read_settings_file():
        with open('settings.txt', encoding='utf-8') as f:
            settings = f.read()
        return {kv.replace(' ', '').split('=')[0]: kv.replace(' ', '').split('=')[1] for kv in settings.split('\n')}

    def main(self):
        confs = self.read_settings_file()
        self.run_facebook(**confs)


if __name__ == '__main__':
    SpiderClient().main()
