#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:32
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : __init__.py.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
import threading
import time
from PatternSpider.utils.dict_utils import DictUtils
from PatternSpider.utils.time_utils import datetime_to_timestamp


class FacebookUtils:
    _instance_lock = threading.Lock()

    def __init__(self):
        self.dict_util = DictUtils()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            with FacebookUtils._instance_lock:
                if not hasattr(cls, '_instance'):
                    FacebookUtils._instance = super().__new__(cls)

        return FacebookUtils._instance

    @staticmethod
    def is_next_request(task, over_datas_num, **kwargs):
        # 获取需要的参数
        limit_count = int(task['raw'].get('limit_count', -1))
        limit_day = int(task['raw'].get('limit_day', -1))
        had_count = int(task.get('had_count', 0))
        task['had_count'] = had_count + int(over_datas_num)

        # 被采集信息的总量 如果采集数量大于等于被采集信息的总量，那就终止采集：
        feed_count = kwargs.get('feed_count', -1)
        if feed_count != -1 and task['had_count'] >= int(feed_count):
            return False, task

        # 增加自定义限制，默认-1 全部采集
        if limit_count != -1 and limit_count < task['had_count']:
            return False, task

        # 增加时间限制
        creation_time = kwargs.get('creation_time', -1)
        if creation_time != -1:
            creation_stamp = datetime_to_timestamp(creation_time)
            if int(time.time()) - creation_stamp > limit_day * 24 * 60 * 60:
                return False, task

        # 三次判断是否不再出现数据 因为网络的原因，即便滚动条到底部，也不一定真的采集结束：
        should_finish_count = task.get('should_finish_count', 0)
        if should_finish_count > 3:
            return False, task

        # 判断是否滑动至底部
        if over_datas_num:
            task['should_finish_count'] = 0
        else:
            time.sleep(5)
            task['should_finish_count'] = should_finish_count + 1
        return True, task

    def parse_attache(self, attachment):
        if type(attachment) == list:
            attachment = attachment[0]
        attach_list = []
        if not attachment:
            return attach_list
        if "all_subattachments" in attachment:
            nodes = attachment["all_subattachments"]["nodes"]
            for attach in nodes:
                typename = attach["media"]["__typename"]
                uri = self.dict_util.get_data_from_field(attach, 'uri')
                caption = self.dict_util.get_data_from_field(attach, 'accessibility_caption')
                attach_list.append({
                    "typename": typename,
                    "uri": uri.replace('\\', '') if uri else '',
                    "caption": caption if caption else ''
                })
        if "media" in attachment:
            if not attachment['media']:
                return attach_list
            typename = attachment["media"]["__typename"]
            if typename == "Photo":
                uri = self.dict_util.get_data_from_field(attachment, 'uri')
                caption = self.dict_util.get_data_from_field(attachment, 'accessibility_caption')
                attach_list.append({
                    "typename": typename,
                    "uri": uri.replace('\\', '') if uri else '',
                    "caption": caption if caption else ''
                })
            elif typename == "Video":
                uri = self.dict_util.get_data_from_field(attachment, 'playable_url')
                thumbnail = self.dict_util.get_data_from_field(attachment, 'uri')
                publish_time = self.dict_util.get_data_from_field(attachment, 'publish_time')
                duration = self.dict_util.get_data_from_field(attachment, 'playable_duration_in_ms')
                attach_list.append({
                    "typename": typename,
                    "uri": uri.replace('\\', '') if uri else '',
                    "caption": '',
                    "thumbnail": thumbnail.replace('\\', '') if thumbnail else '',
                    "publish_time": publish_time if publish_time else '',
                    "duration": duration if duration else ''
                })
            elif typename == 'Sticker':
                uri = self.dict_util.get_data_from_field(attachment, 'uri')
                caption = self.dict_util.get_data_from_field(attachment, 'name')
                attach_list.append({
                    "typename": typename,
                    "uri": uri.replace('\\', '') if uri else '',
                    "caption": caption if caption else ''
                })
        return attach_list
