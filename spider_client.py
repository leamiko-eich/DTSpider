#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/3/1 16:25
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : spider_client.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
import json

from PatternSpider.models.redis_model import OriginSettingsData, DistributedSettings
from PatternSpider.tasks.facebook import FacebookTask
from scrapy.cmdline import execute


class SpiderClient:
    def run_facebook(self, **kwargs):
        mode = kwargs.get('mode', '')
        account_id = kwargs.get('account_id', '')
        code = kwargs.get('code', '')
        group_id = kwargs.get('group_id', '')
        instance_id = kwargs.get('instance_id', '')
        if not (mode and account_id and code and group_id and instance_id):
            return

        # 添加任务
        spider_name = FacebookTask().add_task_from_msyql(mode, account_id, code, group_id, instance_id)
        # 开启爬虫
        execute(('scrapy crawl ' + spider_name).split())

    @staticmethod
    def read_settings_file():
        with open('settings.txt', encoding='utf-8') as f:
            settings = f.read()
        return {kv.replace(' ', '').split('=')[0]: kv.replace(' ', '').split('=')[1] for kv in settings.split('\n')}

    @staticmethod
    def get_settings_from_redis():
        data = DistributedSettings().get_settings_data()
        return json.loads(data)

    def main(self):
        confs = self.read_settings_file()
        # 将配置文件存入本地redis中做缓存
        OriginSettingsData().save_settings_data(confs)
        # 开始启动采集程序
        self.run_facebook(**confs)


if __name__ == '__main__':
    a = SpiderClient().read_settings_file()
    print(a)
