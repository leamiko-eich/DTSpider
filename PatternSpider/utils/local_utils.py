#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:37
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : local_utils.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved

# coding=utf-8
import socket
from urllib.request import urlopen
from json import load


def get_inner_host_ip():
    """
    get host ip address
    获取本机IP地址

    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


def get_outer_host_ip():
    try:
        my_ip = load(urlopen('http://jsonip.com'))['ip']
        return my_ip
    except:
        pass

    try:
        my_ip = load(urlopen('http://httpbin.org/ip'))['origin']
        return my_ip
    except:
        pass

    try:
        my_ip = load(urlopen('https://api.ipify.org/?format=json'))['ip']
        return my_ip
    except:
        pass
    return None


def is_port_used(ip, port):
    """
    check whether the port is used by other program
    检测端口是否被占用

    :param ip:
    :param port:
    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, port))
        return True
    except OSError:
        return False
    finally:
        s.close()


if __name__ == '__main__':
    print(get_inner_host_ip())
    print(get_outer_host_ip())
