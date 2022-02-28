#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:37
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : utils.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved

# coding=utf-8
import json
import math
import random
import string
import hashlib
from scrapy.http.cookies import CookieJar


def get_dict_cookie_from_str(cookie):
    if type(cookie) != dict:
        try:
            dict_cookie = json.loads(cookie)
        except Exception as e:
            dict_cookie = {}
            cookie_str_list = cookie.split('; ')
            for i in cookie_str_list:
                i_list = i.split('=', 1)
                dict_cookie[i_list[0]] = i_list[1]
    else:
        dict_cookie = cookie
    return dict_cookie


# 随机生成经纬度
def random_gps(base_log=120.7, base_lat=30, radius=1000000):
    radius_in_degrees = radius / 111300
    u = float(random.uniform(0.0, 1.0))
    v = float(random.uniform(0.0, 1.0))
    w = radius_in_degrees * math.sqrt(u)
    t = 2 * math.pi * v
    x = w * math.cos(t)
    y = w * math.sin(t)
    longitude = y + base_log
    latitude = x + base_lat
    # 这里是想保留6位小数点
    loga = '%.6f' % longitude
    lata = '%.6f' % latitude
    return str(loga), str(lata)


# 随机生成一个imei号
def getImei(N=15):
    part = ''.join(str(random.randrange(0, 9)) for _ in range(N - 1))
    res = sum(sum(divmod(int(d) * (1 + i % 2), 10)) for i, d in enumerate('{}{}'.format(part, 0)[::-1])) % 10
    return '{}{}'.format(part, -res % 10)


# 随机生成一个mac地址
def get_mac():
    hex_num = string.hexdigits
    mac_list = []
    for i in range(6):
        n = random.sample(hex_num, 2)
        mac_list.append(''.join(n).upper())
    return ':'.join(mac_list)


# 获取响应中的cookie并返回字典格式的cookie
def get_response_cookies(response):
    cookie_dict = {}
    cookie_jar = CookieJar()
    cookie_jar.extract_cookies(response, response.request)
    for k, v in cookie_jar._cookies.items():
        for i, j in v.items():
            for m, n in j.items():
                cookie_dict[m] = n.value
    return cookie_dict


# 通用判断是否继续下一页
def is_go_next_page(curr_page, page_limit, has_next):
    curr_page = int(curr_page)
    page_limit = int(page_limit)
    flag = 1
    if page_limit != -1 and page_limit <= curr_page:
        flag = 0
    if not has_next:
        flag = 0
    return flag


# 获取字典中的值，多用于requestsheaders中的get_url参数
def dict_get(dict_data, key, default_value=None, sure=1):
    value = dict_data.get(key, default_value)
    if sure:
        if not value:
            raise Exception("{} 必须有".format(key))
    return value


def md5_digest(msg, encoding='utf-8'):
    md5 = hashlib.md5()
    if isinstance(msg, bytes) or isinstance(msg, bytearray):
        md5.update(msg)
    else:
        md5.update(msg.encode(encoding))

    return md5.hexdigest()


# 重试3次方法装饰器
def retry_function_3(func):
    def wapper(self, *args, **kwargs):
        c = 1
        while 1:
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                print(e)
                c += 1
                if c > 3:
                    break

    return wapper


# 测试方法装饰器
class A:
    @retry_function_3
    def a(self):
        print(1 / 0)
        return 3


if __name__ == '__main__':
    # ok = '_samesite_flag_=true; cookie2=1c3bc1a4593b005724b38118b991d1f5; t=d195a1f8b259963d1f740c02d1fde9d3; _tb_token_=57b8d599b3bbb; cna=dr/YGFeSkF8CAWolsEY5LVLz; sgcookie=E100%2BDkR4k%2B7Igr9j3AMDE8ISbl5z6ckT2Foq8A723rX37r8sX6wGA5DKAUDoyeSARKa1JSrsmO7MXWvXuc1ktzwrg%3D%3D; uc3=id2=UNDXmLre08ztxw%3D%3D&vt3=F8dCuAoqyw5d7YYrpis%3D&nk2=p2NKNTw%2FwjI%3D&lg2=W5iHLLyFOGW7aA%3D%3D; csg=6b663032; lgc=%5Cu58A8%5Cu70B9%5Cu6C5F%5Cu6C34; dnk=%5Cu58A8%5Cu70B9%5Cu6C5F%5Cu6C34; skt=35855c03171c8a11; existShop=MTYxNTk3NDc4OA%3D%3D; uc4=id4=0%40UgcnCSASykqvIQTBlJNeiZzN7EAb&nk4=0%40pVWdS%2FB0Lu%2BWDguqbqla6QkREw%3D%3D; tracknick=%5Cu58A8%5Cu70B9%5Cu6C5F%5Cu6C34; _cc_=W5iHLLyFfA%3D%3D; enc=glxnbpfCSe97ym23iPtQcBCUEqn8chDC8UotQdqB4EBdcimltlU47sQY5fujGAv1tdu12cMe28SunohGJzArLQ%3D%3D; mt=ci=3_1; thw=cn; hng=CN%7Czh-CN%7CCNY%7C156; alitrackid=www.taobao.com; lastalitrackid=www.taobao.com; _m_h5_tk=577e4cd517f1960a3afece7a7d1f1e75_1616130533818; _m_h5_tk_enc=8f29fe2988f96a8bd5e34d851e70ccbb; xlly_s=1; uc1=cookie14=Uoe1hMX05K%2B2OQ%3D%3D&existShop=false&pas=0&cookie21=URm48syIYn73&cookie16=W5iHLLyFPlMGbLDwA%2BdvAGZqLg%3D%3D; JSESSIONID=DB84D3DF0776F8D5DAD0176650331AAC; isg=BDU142ycuaAvIN0ZuHN56QtSRLfvsunErwG4pLdZ_qy1jleAfwDGlkvI3FK4zgF8; l=eBSH61mcjsU4H3ZfBO5anurza77OuQObzsPzaNbMiInca6T1TTgpkNCQeRQM7dtjgt5bVetzcb5yKRFv5kz_8tgKqelyRs5mpwvp8e1..; tfstk=cNWFBj2gOLb1Hzp7Mp9rPaI-SlYdaMIhqA-Xt1xlyMBYGjOBusAjyhxCvh-WkRAh.'
    # print(get_dict_cookie_from_str(ok))
    no = 'guest_id_marketing=v1%3A164266679356523974; guest_id_ads=v1%3A164266679356523974; personalization_id="v1_ljk0z3JkxUrdQ8YvEIXvyg=="; guest_id=v1%3A164266679356523974; ct0=b08293342dfba085262e0c3cbbed1e83; gt=1484078218085036032; _ga=GA1.2.867186316.1642666796; _gid=GA1.2.1092430490.1642666796'
    print(get_dict_cookie_from_str(no))
