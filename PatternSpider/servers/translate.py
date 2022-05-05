#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/3/14 16:16
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : translate.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
import threading

import requests


# 判断是否是表情包，如果是的话返回True 否则返回False
def is_emoji(content):
    if not content:
        return False
    if u"\U0001F600" <= content <= u"\U0001F64F":
        return True
    elif u"\U0001F300" <= content <= u"\U0001F5FF":
        return True
    elif u"\U0001F680" <= content <= u"\U0001F6FF":
        return True
    elif u"\U0001F1E0" <= content <= u"\U0001F1FF":
        return True
    else:
        return False


class Translate:
    """
    语种代码示例:
        nzh: 中文
        nen: 英文
        nja: 日文
        nru: 俄文
        nvi: 越南文
        nbo: 藏语
        nko: 韩语
        nfr: 法语
        nar: 阿拉伯语

        参数说明:
        srcl: 源语言代码
        tgtl: 目标语言代码
        text: 要翻译的文本
    """
    URI = "http://1.119.185.59:8080/translate"
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            with Translate._instance_lock:
                if not hasattr(cls, '_instance'):
                    Translate._instance = super().__new__(cls)
        return Translate._instance

    def en_to_zh(self, text):
        # 如果是空字符串，直接返回
        if not text:
            return text

        # 如果是纯表情包直接返回
        flag = False
        for i in text:
            flag = is_emoji(i)
            if not flag:
                break
        if flag:
            return text
        # return ""
        # 如果有文本，翻译
        data = {
            "srcl": "nen",
            "tgtl": "nzh",
            "text": text
        }
        try:
            response = requests.post(self.URI, json=data, timeout=5)
            return response.json()['translation'][0]['translated'][0]['text']
        except Exception as e:
            print(e)
            return ""


if __name__ == '__main__':
    print(Translate().en_to_zh("i love you"))
