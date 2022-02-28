#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:34
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : dvidshub_search.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
# coding=utf-8
import json
from PatternSpider.scrapy_redis.spiders import RedisSpider
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.tasks import TaskManage


class DvidshubSearchSpider(RedisSpider):
    name = SpiderNames.dvidshub_search
    redis_key = "start_urls:" + name
    task_manage = TaskManage()

    def parse(self, response):
        raw = json.loads(response.meta['task'])['raw']
        self.logger.info("当前爬取的列表页：{}".format(response.url))

        url_data = response.xpath('//div[@class="mobile-search-info"]/a/@href').extract()
        if url_data:
            self.logger.warning("获取到数据条数：{}".format(len(url_data)))
            for url in url_data:
                self.task_manage.write_task_from_spider_name(
                    SpiderNames.dvidshub_detail,
                    path=url
                )
        # 提取下一页的url
        next_url = response.xpath('//*[@id="pagination-load-more"]/@href').extract_first()
        # 回调下一页的url
        if not next_url:
            self.logger.info("没有下一页的数据了")
        else:
            self.logger.info("抓取下一页")
            self.task_manage.write_task_from_spider_name(
                self.name,
                page=int(raw['page']) + 1,
            )

        self.task_manage.del_item("mirror:" + self.name, response.meta['task'])


if __name__ == '__main__':
    from scrapy.cmdline import execute
    execute(('scrapy crawl ' + SpiderNames.dvidshub_search).split())
