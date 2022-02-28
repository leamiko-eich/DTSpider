#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:29
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : flickr_items.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
from scrapy import Item, Field


class SpiderFlickrItem(Item):
    photo_source = Field()
    photo_id = Field()
    photo_url = Field()
    url = Field()
    title = Field()
    content = Field()
    location_up = Field()
    photo_date = Field()
    photo_by = Field()
    the_unit = Field()
    date_taken = Field()
    date_posted = Field()
    virin = Field()
    resolution = Field()
    size = Field()
    location = Field()
    keywords = Field()
    loc_url = Field()
    md5_value = Field()
    created_time = Field()
    updated_time = Field()
    tag_name = Field()

    image_urls = Field()
    images = Field()
    image_name = Field()
    is_download_image = Field()
