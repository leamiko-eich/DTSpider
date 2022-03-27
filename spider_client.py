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
import os
import time
from PatternSpider.models.redis_model import OriginSettingsData, DistributedSettings
from PatternSpider.tasks.facebook import FacebookTask
from PatternSpider.servers.ding_talk_server import DingTalk
from PatternSpider.utils.local_utils import get_outer_host_ip
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def strat_spiders(spider_name, count=2):
    process = CrawlerProcess(get_project_settings())
    for i in range(count):
        process.crawl(spider_name)
    process.start()


ip = get_outer_host_ip()


class SpiderClient:
    @staticmethod
    def run_facebook(**kwargs):
        mode = kwargs.get('mode', '')
        account_id = kwargs.get('account_id', '')
        code = kwargs.get('code', '')
        group_id = kwargs.get('group_id', '')
        group_id = json.loads(group_id)
        if not (mode and account_id and group_id):
            DingTalk().send_msg("ip:{}、获取的配置文件少参数".format(ip))
            return

        # 添加任务
        spider_name, task_num = FacebookTask().add_task_from_mysql(mode, account_id, code, group_id)
        DingTalk().send_msg("ip:{}、采集程序：{}、任务数量：{}".format(ip, spider_name, task_num))
        # 开启爬虫
        strat_spiders(spider_name)
        # time.sleep(30000)
        DingTalk().send_msg("采集程序结束测试本行代码是否执行，ip:{}、采集程序：{}、任务数量：{}".format(ip, spider_name, task_num))

    @staticmethod
    def read_settings_file():
        if not os.path.exists('settings.txt'):
            return {}
        with open('settings.txt', encoding='utf-8') as f:
            settings = f.read()
        return {kv.replace(' ', '').split('=')[0]: kv.replace(' ', '').split('=')[1] for kv in settings.split('\n')}

    @staticmethod
    def get_settings_from_redis():
        data = DistributedSettings().get_settings_data()
        return json.loads(data)

    def main(self):
        confs = self.read_settings_file()
        # confs = self.get_settings_from_redis()
        if not confs:
            DingTalk().send_msg("ip:{}、获取配置文件失败".format(ip))
            return
        DingTalk().send_msg("ip:{}、获取配置文件成功".format(ip))
        time.sleep(1)
        # 将配置文件存入本地redis中做缓存
        OriginSettingsData().save_settings_data(confs)
        time.sleep(1)
        # 开始启动采集程序
        self.run_facebook(**confs)


if __name__ == '__main__':
    SpiderClient().main()
