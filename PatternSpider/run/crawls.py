#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/3/27 21:23
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : crawls.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
import time

from scrapy.commands import ScrapyCommand


class Command(ScrapyCommand):
    requires_project = True

    def syntax(self):
        return '[options]'

    def short_desc(self):
        return 'A crawler runs multiple times'

    def run(self, args, opts):
        spname = args[0]
        for i in range(2):
            self.crawler_process.crawl(spname)
        self.crawler_process.start()
