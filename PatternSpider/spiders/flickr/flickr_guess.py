#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:35
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : flickr_guess.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved

# coding=utf-8
import json
from PatternSpider.scrapy_redis.spiders import RedisSpider
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.tasks import TaskManage
from PatternSpider.utils.time_utils import timestamp_to_datetime


class FlickrGuessSpider(RedisSpider):
    name = SpiderNames.flickr_guess
    redis_key = "start_urls:" + name
    task_manage = TaskManage()

    def parse(self, response):
        raw = json.loads(response.meta['task'])['raw']
        response_json = json.loads(response.text.replace('jsonFlickrApi(', '')[:-1])
        pics = response_json['photos']['photo']
        for pic in pics:
            item = {}
            item['photo_source'] = 'https://www.flickr.com/'
            item['photo_id'] = pic['id']
            item['photo_url'] = self.select_pic_filed(pic)
            item['url'] = 'https://www.flickr.com/photos/{}/{}/in/pool-navyship/'.format(pic['owner'], pic['id'])
            item['title'] = pic['title']
            item['content'] = pic['description']['_content']
            item['location_up'] = ''
            item['photo_date'] = timestamp_to_datetime(pic['dateupload']).split(' ')[0]
            item['photo_by'] = pic['ownername']
            item['the_unit'] = ''
            item['date_taken'] = pic['datetaken'].split(' ')[0]
            item['date_posted'] = timestamp_to_datetime(pic['dateupload'])
            item['virin'] = ''
            item['resolution'] = ''
            item['size'] = ''
            item['location'] = ''
            item['keywords'] = ''

            # 如果要下载图片到本地，以下三个字段必填
            item['image_name'] = item['photo_id']
            item['image_urls'] = [item['photo_url']]
            item['is_download_image'] = 1 if item['photo_url'] else 0
            self.logger.info("将数据送入管道" + item['photo_id'])
            try:
                yield item
            except Exception as e:
                print(e)

        if raw['page'] < int(response_json['photos']['pages']):
            self.task_manage.write_task_from_spider_name(
                SpiderNames.flickr_guess,
                per_page=100,
                page=int(raw['page']) + 1
            )
        self.task_manage.del_item("mirror:" + self.name, response.meta['task'])

    def select_pic_filed(self, data):
        fileds = ['url_3k_cdn', 'url_k_cdn', 'url_h_cdn', 'url_l_cdn']
        for filed in fileds:
            if filed in data:
                return data[filed]
        return ''


if __name__ == '__main__':
    from scrapy.cmdline import execute

    execute(('scrapy crawl ' + SpiderNames.flickr_guess).split())
