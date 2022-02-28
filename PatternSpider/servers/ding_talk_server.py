#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/15 18:29
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : ding_talk_server.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
import threading
import traceback

import requests
import json
from urllib.parse import urlencode


class DingTalk:
    _instance_lock = threading.Lock()
    Uri = "https://oapi.dingtalk.com/robot/send?"
    Params = {
        'access_token': 'd38c0aa070caf5a72f83df42d31f10bdd09e1f83377f262b5c2508f8b1c52a7a'
    }

    def __init__(self):
        self.__headers = {'Content-Type': 'application/json;charset=utf-8'}
        self.url = self.Uri + urlencode(self.Params)

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            with DingTalk._instance_lock:
                if not hasattr(cls, '_instance'):
                    DingTalk._instance = super().__new__(cls)

        return DingTalk._instance

    def send_msg(self, text, isatall=False, atmobile=""):
        text = 'error\n' + text
        json_text = {
            "msgtype": "text",
            "text": {
                "content": text
            },
            "at": {
                "atMobiles": [
                    atmobile  # @ 人的手机号
                ],
                "isAtAll": isatall  # 是否@全员
            }
        }
        requests.post(self.url, json.dumps(json_text), headers=self.__headers)

    def send_link(self, text, title="", pic_url="", message_url=""):
        text = 'error' + text
        json_text = {
            "msgtype": "link",
            "link": {
                "text": text,
                "title": title,
                "picUrl": pic_url,
                "messageUrl": message_url
            }
        }
        requests.post(self.url, json.dumps(json_text), headers=self.__headers)

    def send_markdown(self, text, title="", isatall=False, atmobile=""):
        json_text = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": text
            },
            "at": {
                "atMobiles": [
                    atmobile
                ],
                "isAtAll": isatall
            }
        }
        requests.post(self.url, json.dumps(json_text), headers=self.__headers)


def ding_alarm(module, spider_name, logger=None):
    def spiders_ding_alarm(func):
        def class_function(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except:
                error = "current spider is：{}\n{} error info is：\n {}".format(spider_name, module,
                                                                              traceback.format_exc())
                DingTalk().send_msg(error)
                logger.error(error) if logger else print(error)

        return class_function

    return spiders_ding_alarm


if __name__ == '__main__':
    ding = DingTalk()
    ding.send_msg("test", atmobile='18731218157')
