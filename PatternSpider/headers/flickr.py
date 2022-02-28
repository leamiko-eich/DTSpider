#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:26
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : flickr.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved

# coding=utf-8
from urllib.parse import urlencode
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.headers import BaseHeaders


class FlickrBase(BaseHeaders):
    pass


class FlickrPhoto(FlickrBase):
    Uri = 'https://api.flickr.com/services/rest?'
    name = SpiderNames.flickr_guess

    def get_url(self, *args, **kwargs):
        params_data = {
            'extras': 'count_comments,count_faves,count_views,date_taken,date_upload,description,icon_urls_deep,isfavorite,ispro,license,media,needs_interstitial,owner_name,owner_datecreate,path_alias,perm_print,realname,rotation,safety_level,secret_k,secret_h,url_sq,url_q,url_t,url_s,url_n,url_w,url_m,url_z,url_c,url_l,url_h,url_k,url_3k,url_4k,url_f,url_5k,url_6k,url_o,visibility,visibility_source,o_dims,publiceditability,system_moderation,datecreate,date_activity,eighteenplus,invitation_only,needs_interstitial,non_members_privacy,pool_pending_count,privacy,member_pending_count,icon_urls,date_activity_detail,muted',
            'per_page': kwargs['per_page'],
            'page': kwargs['page'],
            'get_group_info': '0',
            'group_id': '525285@N20',
            'viewerNSID': '',
            'method': 'flickr.groups.pools.getPhotos',
            'csrf': '',
            'format': 'json',
            'hermes': '1',
            'hermesClient': '1',
            'reqId': '9fe905bb-be64-493a-945f-2aa16f8dca0a',
            'api_key': '307710296e5238b4e4dbb23b2af20b20',
        }
        url = self.Uri + urlencode(params_data)
        return url

    def get_headers(self, *args, **kwargs):
        headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cookie': 'xb=438118; localization=zh-hk%3Buk%3Bgb; flrbp=1642733998-68512480bea0d0679251166bd02c00eaf55aae9f; flrbgrp=1642733998-dd9d79b0152c4528d892af8f8adb6c8a20f08cd2; flrbgdrp=1642733998-615155a84bd27f4867448eba3a5b5fd0d84d660e; flrbgmrp=1642733998-f4055bafd2ecf6ee011f21f553275e19a9746f5d; flrbrst=1642733998-4c330449c5aa6439526f2ec79fb61ac38d488d17; flrtags=1642733998-840bf4368199486c03d4b50fa7bb6a6282d20f1c; flrbrp=1642733998-feffa6cce4c09b6dfb4ec594c673e95c901a2f28; _gcl_au=1.1.1211238040.1642734026; __ssid=462307caf305d7204a510835224a6d7; sp=2bd3c254-07cf-4983-b3a3-25e70b52c826; _sp_ses.df80=*; AMCVS_48E815355BFE96970A495CD0%40AdobeOrg=1; AMCV_48E815355BFE96970A495CD0%40AdobeOrg=281789898%7CMCMID%7C88144513298983942961891330330848092312%7CMCAAMLH-1643347594%7C11%7CMCAAMB-1643347594%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1642749994s%7CNONE%7CvVersion%7C4.1.0; s_cc=true; s_ptc=%5B%5BB%5D%5D; ccc=%7B%22needsConsent%22%3Afalse%2C%22managed%22%3A0%2C%22changed%22%3A0%2C%22info%22%3A%7B%22cookieBlock%22%3A%7B%22level%22%3A0%2C%22blockRan%22%3A1%7D%7D%7D; vp=1263%2C150%2C1.5%2C17%2Cfluid-centered%3A1011; s_tp=8661; _sp_id.df80=8630f80a-95f4-46c7-b56b-84d04ca846b4.1642734021.2.1642742855.1642734478.655ba674-3b7b-4081-9c63-5db708f4e9c5; s_ppv=group-pool-page-view%2C92%2C7%2C7960',
            'origin': 'https://www.flickr.com',
            'referer': 'https://www.flickr.com/',
            'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
        }
        return headers


if __name__ == '__main__':
    pass
