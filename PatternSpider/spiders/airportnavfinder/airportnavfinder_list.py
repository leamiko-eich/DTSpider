#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:34
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : airportnavfinder_list.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved

# coding=utf-8
import json
from PatternSpider.scrapy_redis.spiders import RedisSpider
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.tasks import TaskManage


class DvidshubSearchSpider(RedisSpider):
    name = SpiderNames.airportnavfinder_list
    redis_key = "start_urls:" + name
    task_manage = TaskManage()

    def parse(self, response):
        raw = json.loads(response.meta['task'])['raw']
        self.logger.info("当前爬取的列表页：{}".format(response.url))
        url_data = response.xpath('//div[@class="aplist-row"]/div[1]/div[2]/a/@href').extract()
        if url_data:
            # 列表下页：
            self.task_manage.write_task_from_spider_name(
                self.name,
                page=int(raw['page']) + 1
            )
            # 详情页：
            airport_abbr_list = response.xpath('//div[@class="aplist-row"]/div[1]/div[1]/a/text()').extract()  # 机场缩写
            airport_name_list = response.xpath('//div[@class="aplist-row"]/div[1]/div[2]/a/text()').extract()  # 机场名
            country_list = response.xpath('//div[@class="aplist-row"]/div[2]/div[2]')  # 国家
            state_data = response.xpath('//div[@class="aplist-row"]/div[2]/div[1]')  # 城市、州
            for index, path in enumerate(url_data):
                item = {}
                item['airport_abbr'] = airport_abbr_list[index]
                item['airport_name'] = airport_name_list[index]
                item['country'] = country_list[index].xpath('./span/text()').extract_first()
                item['state'] = state_data[index].xpath('./span[2]/text()').extract_first()
                item['city'] = state_data[index].xpath('./span[1]/text()').extract_first()
                item['city'] = item['city'].replace(',', '').strip() if item['city'] else ''
                item['airport_url'] = "https://airportnavfinder.com" + path
                self.task_manage.write_task_from_spider_name(
                    SpiderNames.airportnavfinder_detail,
                    path=path,
                    other_raw=item
                )
        else:
            self.logger.warning("爬取完成")
        self.task_manage.del_item("mirror:" + self.name, response.meta['task'])


if __name__ == '__main__':
    from scrapy.cmdline import execute

    execute(('scrapy crawl ' + SpiderNames.dvidshub_search).split())
