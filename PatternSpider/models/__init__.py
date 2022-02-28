#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:19
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : __init__.py.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
from os.path import dirname
from glob import glob
from keyword import iskeyword
from os.path import join, split, splitext
import inspect


def get_class_from_spider_table_name(spider_table_name):
    for name in glob(join(dirname(__file__), '*.py')):
        module = splitext(split(name)[-1])[0]
        if not module.startswith('_') and \
                module.isidentifier() and \
                not iskeyword(module):
            __import__(__name__ + '.' + module)
            clsmembers = inspect.getmembers(eval(module), inspect.isclass)
            for (name, class_) in clsmembers:
                if not hasattr(class_, 'name'):
                    continue
                if class_.name == spider_table_name:
                    return class_
    return None


def run(spider_table_name, *args, **kwargs):
    class_ = get_class_from_spider_table_name(spider_table_name)
    return class_().run(*args, **kwargs)
