#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/4/28 10:00
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : marineregions_detail.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
import json

from PatternSpider.scrapy_redis.spiders import RedisSpider
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.tasks import TaskManage
from lxml import etree


class MarineregionsDetailSpider(RedisSpider):
    name = SpiderNames.marineregions_detail
    redis_key = "start_urls:" + name
    task_manage = TaskManage()
    custom_settings = {
        'CONCURRENT_REQUESTS': 100,
        'DOWNLOADER_MIDDLEWARES': {
            'PatternSpider.middlewares.middlewares.RandomUserAgentMiddleware': 543,
        },
        "EXTENSIONS": {
            # 'PatternSpider.extensions.RedisSpiderSmartIdleClosedExensions': 100,
        },
        "ITEM_PIPELINES": {
            # 'PatternSpider.pipelines.DownloadImagesPipeline': 1,
            'PatternSpider.pipelines.MongoPipeline': 100,
            # 'PatternSpider.pipelines.Neo4jPipeline': 500,
        }
    }

    def replace_str(self, s):
        return s.replace("\n", '').replace("\xa0", "").replace('.', '_').replace(' ', '')

    def parse_tr_table(self, tr):
        child_trs = tr.xpath('td[2]/table/tr')
        child_datas = []
        fileds = child_trs[0].xpath('td//text()')
        for child_tr in child_trs[1:]:
            child_data_dict = {}
            values = child_tr.xpath('td//text()')
            if not values:
                continue
            for filed in fileds:
                if fileds.index(filed) == len(fileds) - 1:
                    child_data_dict[self.replace_str(filed)] = self.replace_str("".join(values[fileds.index(filed):]))
                else:
                    child_data_dict[self.replace_str(filed)] = self.replace_str(values[fileds.index(filed)])
            child_datas.append(child_data_dict)
        value = child_datas if child_datas else self.replace_str("___".join(fileds))
        return value

    def parse_tr_options(self, tr):
        contents = ""
        contents += "__".join([self.replace_str(t) for t in tr.xpath('td/text()')])
        contents += "__".join([self.replace_str(t) for t in tr.xpath('td/b/text()')])
        over_options = []
        options = tr.xpath('td[2]/select/option')
        for option in options:
            over_options.append({'url': option.xpath('@value')[0], 'name': option.text})
        value = {'content': contents, 'options': over_options}
        return value

    def parse(self, response):
        task = json.loads(response.meta['task'])
        response_html = etree.HTML(response.text)
        item = {
            "id": task['raw']['id'],
            "request_url": task['url'],
            "page_datas": {},
        }
        datas = {}
        trs = response_html.xpath('//*[@id="content"]/table/tr')
        for tr in trs:
            key = tr.xpath("td[1]//text()")
            key = self.replace_str(key[0]) if key else ""
            child_trs = tr.xpath('td[2]/table/tr')
            child_option = tr.xpath('td[2]/select/option')
            if child_trs:
                value = self.parse_tr_table(tr)
            elif child_option:
                value = self.parse_tr_options(tr)
            else:
                value = tr.xpath("td[2]//text()")
                value = "___".join([self.replace_str(v) for v in value]) if value else ""
            if not key:
                continue
            datas[key] = value
        if 'Download' in datas:
            item['down_load'] = datas['Download']['options']
        item['page_datas'] = datas
        print(item)
        yield item
        # 删除任务
        self.task_manage.del_item("mirror:" + self.name, response.meta['task'])
