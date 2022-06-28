#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/4/19 10:08
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : deagel.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.headers import BaseHeaders


class DeagelBase(BaseHeaders):

    def get_headers(self, **kwargs):
        return {
            'authority': 'deagel.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'referer': 'https://deagel.com/',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'
        }


class EquipmentDirectories(DeagelBase):
    Uri = 'https://deagel.com/api/directories'
    name = SpiderNames.deagel_equipment_directories

    def get_url(self, **kwargs):
        return self.Uri


class EquipmentList(DeagelBase):
    Uri = 'https://deagel.com/api/directoryContent/{}'
    name = SpiderNames.deagel_equipment_list

    def get_url(self, **kwargs):
        return self.Uri.format(kwargs['directory_name'])


class EquipmentDetail(DeagelBase):
    Uri = 'https://deagel.com/api/equipment/{}'
    name = SpiderNames.deagel_equipment_detail

    def get_url(self, **kwargs):
        return self.Uri.format(kwargs['equipment_id'])


class CountryList(DeagelBase):
    Uri = 'https://deagel.com/api/country'
    name = SpiderNames.deagel_country_list

    def get_url(self, **kwargs):
        return self.Uri


class CountryDetail(DeagelBase):
    Uri = 'https://deagel.com/api/countryByName/{}'
    name = SpiderNames.deagel_country_detail

    def get_url(self, **kwargs):
        return self.Uri.format(kwargs['country_name'])


class ReportsList(DeagelBase):
    Uri = 'https://deagel.com/api/reports'
    name = SpiderNames.deagel_reports_list

    def get_url(self, **kwargs):
        return self.Uri


class ReportsDetail(DeagelBase):
    Uri = 'https://deagel.com/api/{}/{}'
    name = SpiderNames.deagel_reports_detail

    def get_url(self, **kwargs):
        return self.Uri.format(kwargs['path'], kwargs['id'])


class NewsList(DeagelBase):
    Uri = 'https://deagel.com/api/newsFilter?keyword=&page={}&year=&type=&country=&corp=&equipment='
    name = SpiderNames.deagel_news_list

    def get_url(self, **kwargs):
        return self.Uri.format(kwargs['page'])


class NewsDetail(DeagelBase):
    Uri = 'https://deagel.com/api/newsDetail/{}'
    name = SpiderNames.deagel_news_detail

    def get_url(self, **kwargs):
        return self.Uri.format(kwargs['id'])


class GalleryList(DeagelBase):
    Uri = 'https://deagel.com/api/photoFilter?keyword=&page={}&year=&country=&equipment='
    name = SpiderNames.deagel_gallery_list

    def get_url(self, **kwargs):
        return self.Uri.format(kwargs['page'])


class GalleryDetail(DeagelBase):
    Uri = 'https://deagel.com/api/photoDetail/{}'
    name = SpiderNames.deagel_gallery_detail

    def get_url(self, **kwargs):
        return self.Uri.format(kwargs['id'])
