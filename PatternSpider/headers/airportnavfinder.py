#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:25
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : airportnavfinder.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
from urllib.parse import urlencode
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.headers import BaseHeaders


class AirportnavfinderBase(BaseHeaders):
    pass


class AirportnavfinderList(AirportnavfinderBase):
    Uri = 'https://airportnavfinder.com/index.php?'
    name = SpiderNames.airportnavfinder_list

    def get_url(self, *args, **kwargs):
        params_data = {
            "op": "airportlist",
            "o": "t",
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'cookie': 'id=22878aad9fc60077||t=1616384090|et=730|cs=002213fd48c66890efa92c6eab; RUL=EL3r4IIGGL3S5ZEGIogCATZhkOMk9mqbF2N4po5Xz2icmb8IcjcnbijoDlwxm5nKbp97YzyqAmNpFIg8kprdFVb26tFGahdjvrq10LcgQT9HOXnBjQlo12l_JdWnx7kVcHq-Kw98RudGxxBdO9p26PMSOWmls-9KqxPLq778mMiA__XgcQvklv2ZYOLygbRbe9yoStz9rnZPRcayvgvtKbWy_eCbLZmZTZJhJ3z6j2EirL7E0gB_xaaSFgaftxL_m3EWRrBtTtqBws9UoFXqBvCTH1Judcv6-vsvyYj103IJ7oZ5rjbnfdMyOW76D1n91P3-O38qCus7VQIYBjTisdjjGAg1sEnGfW_KG7BOrHlWWbofslxv|cs=AP6Md-U9zs9WSFwTBZP-jpdeBGnd',
        }


class AirportnavfinderDetail(AirportnavfinderBase):
    Uri = 'https://airportnavfinder.com'
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'cookie': 'id=22878aad9fc60077||t=1616384090|et=730|cs=002213fd48c66890efa92c6eab; RUL=EL3r4IIGGL3S5ZEGIogCATZhkOMk9mqbF2N4po5Xz2icmb8IcjcnbijoDlwxm5nKbp97YzyqAmNpFIg8kprdFVb26tFGahdjvrq10LcgQT9HOXnBjQlo12l_JdWnx7kVcHq-Kw98RudGxxBdO9p26PMSOWmls-9KqxPLq778mMiA__XgcQvklv2ZYOLygbRbe9yoStz9rnZPRcayvgvtKbWy_eCbLZmZTZJhJ3z6j2EirL7E0gB_xaaSFgaftxL_m3EWRrBtTtqBws9UoFXqBvCTH1Judcv6-vsvyYj103IJ7oZ5rjbnfdMyOW76D1n91P3-O38qCus7VQIYBjTisdjjGAg1sEnGfW_KG7BOrHlWWbofslxv|cs=AP6Md-U9zs9WSFwTBZP-jpdeBGnd',
        }


if __name__ == '__main__':
    pass
