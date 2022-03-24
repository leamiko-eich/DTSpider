#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/25 11:10
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : sms.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
from urllib.parse import urlencode

import requests


class Sms:
    def __init__(self):
        self.account = "刘飞凡"
        self.pwd = "liufeifan1206"
        self.token = "bd4f8b0de4e473f491caa2a672b16983"
        self.project_id = 690

    def send_requests(self, url, params):
        full_url = url + urlencode(params)
        response = requests.get(full_url)
        return response.json()

    def get_token(self):
        """
        :return: {"stat":true,"message":"OK","code":0,"data":{"token":"xxxxxxxxxxx"}}
        """
        url = 'http://api1.shm178.net/api/login?user={}&password={}'.format(self.account, self.pwd)
        params = {
            'user': self.account,
            'password': self.pwd
        }
        response = self.send_requests(url, params)
        return response

    def get_phone(self):
        """
        :return: {"stat":true,"message":"OK","code":0,"data":[{"phone":"XXXXXXX","province":"陕西","operator":"联通","city":"渭南"}]}
        """
        url = 'http://api1.shm178.net/api/getPhone?'
        params = {
            'token': self.token,
            'itemId': self.project_id,
        }
        post_data = {
            'assignPhon': '16269455146',
            # 'operator':'移动、联通、电信、虚拟商、非虚拟商（可空）',
            'asEx': 'assign',
            # 'part':'170|172|180等（可空）',
            # 'province':'省份',
            # 'city':'城市',
            # 'num':'数量',
        }
        full_url = url + urlencode(params)
        response = requests.post(full_url, json=post_data)
        # response = self.send_requests(url, params)
        return response

    def get_sms_info(self, phone):
        """
        :return: {"stat":true,"message":"OK","code":0,"data":{"sms":"短信内容123456","smsCode":"123456"}}
        """
        url = 'http://api1.shm178.net/api/getSms?'
        params = {
            'token': self.token,
            'itemId': self.project_id,
            'phone': phone,
        }
        response = self.send_requests(url, params)
        return response

    def send_sms(self, phone, sendSms, sendPhone):
        """
        :return: {"stat":true,"message":"短信发送完成","code":0,"data":null}
        """
        url = 'http://api1.shm178.net/api/sendSms?'
        params = {
            'token': self.token,
            'itemId': self.project_id,
            'phone': phone,
            'sendSms': sendSms,
            'sendPhone': sendPhone,
        }
        response = self.send_requests(url, params)
        return response

    def get_send_sms_result(self, phone):
        """
        :return: {"stat":true,"message":"发送成功","code":0,"data":null}
        """
        url = 'http://api1.shm178.net/api/sendSmsStatus?'
        params = {
            'token': self.token,
            'itemId': self.project_id,
            'phone': phone,
        }
        response = self.send_requests(url, params)
        return response

    def release_phone(self, phone):
        """
        :return: {"stat":true,"message":"OK","code":0,"data":null}
        """
        url = 'http://api1.shm178.net/api/release?'
        params = {
            'token': self.token,
            'itemId': self.project_id,
            'phone': phone,
        }
        response = self.send_requests(url, params)
        return response

    def release_all_phone(self):
        """
        :return: {"stat":true,"message":"OK","code":0,"data":null}
        """
        url = 'http://api1.shm178.net/api/releaseAll?'
        params = {
            'token': self.token
        }
        response = self.send_requests(url, params)
        return response

    def pull_black_phone(self, phone):
        """
        :return: {"stat":true,"message":"OK","code":0,"data":null}
        """
        url = 'http://api1.shm178.net/api/addBlack?'
        params = {
            'token': self.token,
            'itemId': self.project_id,
            'phone': phone,

        }
        response = self.send_requests(url, params)
        return response

    def login_out(self):
        """
        :return: {"stat":true,"message":"OK","code":0,"data":null}
        """
        url = 'http://api1.shm178.net/api/userQuit?'
        params = {
            'token': self.token
        }
        response = self.send_requests(url, params)
        return response

    def get_money(self):
        """
        :return: {"stat":true,"message":"OK","code":0,"data":{"doubi":9923.0}}
        """
        url = 'http://api1.shm178.net/api/userInfo?'
        params = {
            'token': self.token
        }
        response = self.send_requests(url, params)
        return response


if __name__ == '__main__':
    # res = Sms().get_phone()
    res = Sms().get_sms_info("16269456098")
    # sms_info = Sms().release_phone()
    # sms_info = Sms().pull_black_phone()
    # res = Sms().release_all_phone()
    # res = Sms().get_money()
    print(res)
    pass
