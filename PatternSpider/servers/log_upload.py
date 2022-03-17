#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/3/16 17:45
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : log_upload.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
import requests


def log_upload(task_code, group_id, log_name="test"):
    url = "http://10.168.160.152:8888/api/v1.0/admin/log/upload"

    files = [('file', (log_name+".log", open('./log/{}.log'.format(log_name), 'rb'), 'log'))]
    upload_data = {
        "task_code": task_code,
        "group_id": group_id
    }
    return requests.post(url, data=upload_data, files=files)
