#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:37
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : logger_utils.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved

import logging


def get_logger(logger_name, logfile=None):
    # 第一步，创建一个logger
    logger = logging.getLogger(logger_name)
    # Log等级总开关  此时是INFO
    logger.setLevel(logging.INFO)

    # 第二步，创建一个handler，用于写入日志文件
    logfile = logfile if logfile else './{}.log'.format(logger_name)
    fh = logging.FileHandler(logfile, mode='a', encoding='UTF-8')
    fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关

    # 第三步，再创建一个handler，用于输出到控制台
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)  # 输出到console的log等级的开关

    # 第四步，定义handler的输出格式（时间，文件，行数，错误级别，错误提示）
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # 第五步，将logger添加到handler里面
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
