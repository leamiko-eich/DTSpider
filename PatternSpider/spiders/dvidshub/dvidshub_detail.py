#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:34
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : dvidshub_detail.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
# coding=utf-8
import datetime
from PatternSpider.scrapy_redis.spiders import RedisSpider
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.tasks import TaskManage
from PatternSpider.items.dvidshub_items import SpiderDivdshubItem


class DvidshubDetailSpider(RedisSpider):
    name = SpiderNames.dvidshub_detail
    redis_key = "start_urls:" + name
    task_manage = TaskManage()

    def parse(self, response):
        self.logger.info("开始解析详情页" + response.url)
        item = SpiderDivdshubItem()
        item['photo_id'] = response.xpath(
            '//table[@class="uk-table image_info_table asset_info_table"]/tbody/tr[3]/td[2]/text()').extract_first()
        item['photo_url'] = response.xpath('//div[@class="large_image_display"]/img/@src').extract_first()
        item['url'] = response.url
        item['title'] = response.xpath('//div/h1[@class="asset-title"]/text()').extract_first()
        item['content'] = "".join(
            [i for i in response.xpath('//*[@id="body_content"]/div[1]/div[2]/div[1]/p/text()').extract()]).replace(
            '\n', '').replace('\r', '').strip()
        item['location_up'] = response.xpath(
            '//*[@id="body_content"]/div[1]/div[2]/div[1]/div[3]/div[1]/h3[1]/text()').extract_first()
        photo_date = response.xpath(
            '//*[@id="body_content"]/div[1]/div[2]/div[1]/div[3]/div[1]/h3[2]/text()').extract_first()
        # 序列化日期
        m, d, y = photo_date.split('.')
        item['photo_date'] = datetime.datetime.strptime(y + "-" + m + "-" + d, "%Y-%m-%d")
        item['photo_by'] = response.xpath(
            '//*[@id="body_content"]/div[1]/div[2]/div[1]/div[3]/div[1]/h3[3]/a[1]/text()').extract_first()
        item['the_unit'] = response.xpath('//h3[@class="the_unit"]/a[1]/text()').extract_first()
        date_taken = response.xpath(
            '//div[@class="image_info_container asset_info_container"]/table[1]/tbody/tr[1]/td[2]/text()').extract_first()
        # 序列化日期
        m, d, y = date_taken.split('.')
        item['date_taken'] = datetime.datetime.strptime(y + "-" + m + "-" + d, "%Y-%m-%d")
        date_posted = response.xpath(
            '//div[@class="image_info_container asset_info_container"]/table[1]/tbody/tr[2]/td[2]/text()').extract_first()
        # 序列化日期
        ymd, hms = date_posted.split(' ')
        m, d, y = ymd.split('.')
        item['date_posted'] = datetime.datetime.strptime(y + "-" + m + "-" + d + " " + hms, "%Y-%m-%d %H:%M")
        item['virin'] = response.xpath('//div[@class="image_info_container asset_info_container"]/table[1]/tbody/tr[4]'
                                       '/td[2]/text()').extract_first()
        item['resolution'] = response.xpath('//div[@class="image_info_container asset_info_container"]/table[1]/tbody'
                                            '/tr[5]/td[2]/text()').extract_first()
        item['size'] = response.xpath('//div[@class="image_info_container asset_info_container"]/table[1]/tbody/tr[6]'
                                      '/td[2]/text()').extract_first()
        item['location'] = response.xpath('//div[@class="image_info_container asset_info_container"]/table[1]/tbody/'
                                          'tr[7]/td[2]/text()').extract_first()
        keywords = response.xpath('//div[@class="tags tags-public"][1]/div/p/i/text()').extract_first()
        # 判断keywords是否有值
        item['keywords'] = None if keywords == 'No keywords found.' else keywords
        item['tag_name'] = response.xpath('//div[@class="readonly"]/a/text()').extract()
        # 如果要下载图片到本地，以下三个字段必填
        item['image_name'] = item['photo_id']
        item['image_urls'] = [item['photo_url']]
        item['is_download_image'] = 1
        self.logger.info("将数据送入管道" + item['photo_id'])
        yield item

        self.task_manage.del_item("mirror:" + self.name, response.meta['task'])


if __name__ == '__main__':
    from scrapy.cmdline import execute
    execute(('scrapy crawl ' + SpiderNames.dvidshub_detail).split())
