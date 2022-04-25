#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/3/27 16:27
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : test.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
import os
import time
from concurrent.futures.thread import ThreadPoolExecutor

from PatternSpider.models.redis_model import RedisMainProcess
from PatternSpider.cookies_manage.facebook_cookies import FacebookCookies

# a = RedisMainProcess().save_main_pid(345)
# b = RedisMainProcess().get_main_pid()
# print(a,b)

# FacebookCookies().write_to_redis(123455, [{"a": 123, 'v': 234}])
# FacebookCookies().write_to_redis(123455, [{"a": "wqweqweqd", 'v': 234},{"s":123132}])
from scrapy.cmdline import execute
from PatternSpider.settings.spider_names import SpiderNames
from scrapy.cmdline import execute

# execute(('scrapy crawl ' + SpiderNames.deagel_equipment_directories).split())
# execute(('scrapy crawl ' + SpiderNames.deagel_equipment_list).split())
# execute(('scrapy crawl ' + SpiderNames.deagel_equipment_detail).split())


# execute(('scrapy crawl ' + SpiderNames.deagel_country_list).split())
# execute(('scrapy crawl ' + SpiderNames.deagel_country_detail).split())

# execute(('scrapy crawl ' + SpiderNames.deagel_reports_list).split())
# execute(('scrapy crawl ' + SpiderNames.deagel_reports_detail).split())

# execute(('scrapy crawl ' + SpiderNames.deagel_news_list).split())
# execute(('scrapy crawl ' + SpiderNames.deagel_news_detail).split())

# execute(('scrapy crawl ' + SpiderNames.deagel_gallery_list).split())
execute(('scrapy crawl ' + SpiderNames.deagel_gallery_detail).split())



