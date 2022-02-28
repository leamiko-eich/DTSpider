#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:36
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : file_utils.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved

# coding=utf-8
import os
import shutil
from scrapy.utils.project import get_project_settings
import csv
import datetime


def get_log_path(spider_name):
    settings = get_project_settings()
    env = settings.get('ENV')
    today = datetime.datetime.now()
    if env == 'produce':
        LOG_FILE = "/mnt/logs/scrapy_redis/{}_{}_{}_{}.log".format(today.year, today.month, today.day, spider_name)
    else:
        LOG_FILE = "D:/logs/scrapy_redis/{}_{}_{}_{}.log".format(today.year, today.month, today.day, spider_name)
    return LOG_FILE


def write_to_csv(csv_file_name, header, datas):
    f = open(csv_file_name, 'a', encoding='utf-8', newline='')
    # 2. 基于文件对象构建 csv写入对象
    csv_writer = csv.writer(f)
    # 3. 构建列表头
    # csv_writer.writerow(header)
    for data in datas:
        # 4. 写入csv文件内容
        if type(data) == dict:
            data = list(data.values())
        csv_writer.writerow(data)
    f.close()


def operation():
    base_dir = 'C:\\Users\\admin\\Desktop\\images\\dvidshub\\'
    for i in range(1, 38):
        os.mkdir(base_dir + str(i))
        new_dir = base_dir + str(i) + '\\'
        files = [f for r, _, fs in os.walk(base_dir) for f in fs][:2000]
        for file in files:
            mew_name = new_dir + file
            old_name = base_dir + file
            shutil.move(old_name, mew_name)
            print(file)


def key_is_exists(base_dir, key):
    ds = [d for r, ds, fs in os.walk(base_dir) for d in ds]
    for dir in ds:
        abs_psth = os.path.join(os.path.join(base_dir, dir), key)
        if os.path.exists(abs_psth):
            return abs_psth.replace('C:\\Users\\admin\\Desktop\\', '').replace('\\', '/')
    with open('nosuchphoto.text', 'a', encoding='utf-8') as f:
        f.write(key + '\n')
    return False


class FileOperation():
    def __init__(self):
        pass

    def creat_dir(self, dir, *args):
        new_path = os.path.join(dir, *args)
        if os.path.exists(new_path):
            os.makedirs(new_path)
        return new_path

    def file_is_exists(self,dir):
        pass
