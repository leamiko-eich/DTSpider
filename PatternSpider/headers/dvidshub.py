#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:26
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : dvidshub.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
from urllib.parse import urlencode
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.headers import BaseHeaders


class DvidshubBase(BaseHeaders):
    pass


class DvidshubSearch(DvidshubBase):
    Uri = 'https://www.dvidshub.net/search/?'
    name = SpiderNames.dvidshub_search

    def get_url(self, *args, **kwargs):
        params_data = {
            "q": "",
            "filter[type]": "image",
            "filter[tags][0]": "coastguardnewswire",
            "view": 'grid',
            "sort": "date",
            "page": kwargs["page"],
        }
        url = self.Uri + urlencode(params_data)
        return url

    def get_headers(self, *args, **kwargs):
        return {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en',
            'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
            'Referer': 'https://www.dvidshub.net/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/69.0.3497.100 Safari/537.36',
        }


class DvidshubDetail(DvidshubBase):
    Uri = 'https://www.dvidshub.net'
    name = SpiderNames.dvidshub_detail

    def get_url(self, *args, **kwargs):
        url = self.Uri + kwargs['path']
        return url

    def get_headers(self, *args, **kwargs):
        return {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en',
            'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
            'Referer': 'https://www.dvidshub.net/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/69.0.3497.100 Safari/537.36',
        }


if __name__ == '__main__':
    pass
