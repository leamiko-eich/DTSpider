#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/4/28 9:47
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : marineregions.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.headers import BaseHeaders


class MarineregionsBase(BaseHeaders):
    def get_headers(self, **kwargs):
        return {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'
        }


class MarineregionsList(MarineregionsBase):
    Uri = 'https://www.marineregions.org/gazetteer.php?p=browser'
    name = SpiderNames.marineregions_list

    def get_url(self, **kwargs):
        path_url = kwargs['path_url']
        if not path_url:
            return self.Uri
        return self.Uri + path_url


class MarineregionsDetail(MarineregionsBase):
    Uri = 'https://www.marineregions.org/{}'
    name = SpiderNames.marineregions_detail

    def get_url(self, **kwargs):
        return self.Uri.format(kwargs['path_url'])
