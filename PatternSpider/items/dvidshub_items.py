#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:28
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : dvidshub_items.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
from scrapy import Item, Field


class SpiderDivdshubItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # image_table
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
    # df = Field()
    # created_by = Field()
    # updated_by = Feild()
    created_time = Field()
    updated_time = Field()

    image_urls = Field()
    images = Field()
    image_name = Field()
    is_download_image = Field()

    # tag_table
    tag_name = Field()
