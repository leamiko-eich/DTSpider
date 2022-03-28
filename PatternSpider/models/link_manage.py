#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:30
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : link_manage.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved

# -*- coding: UTF-8 -*-
import threading
import pymysql
import redis
from elasticsearch5 import Elasticsearch
from minio import Minio
from pymongo import MongoClient
from scrapy.utils.project import get_project_settings
from dbutils.pooled_db import PooledDB


class LinkManege(object):
    _instance_lock = threading.Lock()
    db_pool = {}
    db_session_pool = {}
    settings = get_project_settings()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            with LinkManege._instance_lock:
                if not hasattr(cls, '_instance'):
                    LinkManege._instance = super().__new__(cls)

        return LinkManege._instance

    # ##################################################基础获取连接方法#####################################################

    # 添加连接缓存对象
    def __set_db_pool(self, group, conn):
        self.db_pool[group] = conn

    # 获取连接缓存
    def __get_db_pool(self, group):
        return self.db_pool[group] if group in self.db_pool else {}

    # #################################################获取redis连接####################################################
    # 获取redis连接池
    def __get_redis_pool(self, client_name):
        db_config = self.settings.get(client_name)
        db = redis.Redis(host=db_config["host"], port=db_config["port"],
                         password=db_config["pwd"], db=db_config["database"])
        self.__set_db_pool(client_name, db)
        return db

    # 获取redis连接
    def get_redis_db(self, client_name):
        db = self.__get_db_pool(client_name)
        if db != {}:
            try:
                db.ping()
            except Exception as e:
                print(e)
                db = self.__get_redis_pool(client_name)
        else:
            db = self.__get_redis_pool(client_name)
        return db

    # #################################################获取mysql连接####################################################
    # mysql连接数据库
    def __get_mysql_connection(self, client_name):
        client_config = self.settings.get(client_name)
        # 重新连接
        pool = PooledDB(
            creator=pymysql,
            mincached=1,
            maxcached=5,
            host=client_config["host"],
            user=client_config["user"],
            passwd=client_config["pwd"],
            db=client_config["database"],
            port=client_config["port"],
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True, read_timeout=60, write_timeout=600, max_allowed_packet=500 * 1024 * 1024
        )
        self.__set_db_pool(client_name, pool)
        return pool

    # mysql获取实例连接
    def get_mysql_db(self, client_name):
        pool = self.__get_db_pool(client_name)
        if pool != {}:
            try:
                conn = pool.connection()
                conn.ping(reconnect=True)
            except Exception as e:
                print(e)
                pool = self.__get_mysql_connection(client_name)
                conn = pool.connection()
        else:
            pool = self.__get_mysql_connection(client_name)
            conn = pool.connection()
        return conn

    # #################################################获取elasticsearch连接#############################################
    def __es_conn(self, client_name):
        db_config = self.settings.get(client_name)
        es_server = Elasticsearch(
            hosts=db_config['hosts'],
            port=db_config['port'],
            http_auth=(db_config['username'], db_config['password']),
            timeout=240,
            max_retries=5,
            retry_on_timeout=True
        )
        self.__set_db_pool(client_name, es_server)
        return es_server

    # 获取elasticsearch服务连接
    def get_es_db(self, client_name):
        es_server = self.__get_db_pool(client_name)
        if es_server != {}:
            return es_server
        else:
            return self.__es_conn(client_name)

    # #################################################获取minio连接#############################################
    def __minio_conn(self, client_name):
        db_config = self.settings.get(client_name)
        minio_server = Minio(
            db_config['host'] + ":" + db_config['port'] + '/',
            access_key=db_config['ak'],
            secret_key=db_config['sk'],
            secure=False  # HTTP is Flase, HTTPS is True
        )
        self.__set_db_pool(client_name, minio_server)
        return minio_server

    # 获取elasticsearch服务连接
    def get_minio_db(self, client_name):
        minio_server = self.__get_db_pool(client_name)
        if minio_server != {}:
            return minio_server
        else:
            return self.__minio_conn(client_name)

    # #################################################获取mongo连接####################################################
    # 获取mongo连接
    def __mongo_client(self, client_name):
        db_config = self.settings.get(client_name)
        mongo_str = "mongodb://%s:%s/" % (db_config["host"], db_config['port'])
        client = MongoClient(mongo_str, connect=False)
        client.admin.authenticate(db_config["user"], db_config["pwd"], mechanism='SCRAM-SHA-1')
        self.__set_db_pool(client_name, client)
        return client

    # 获取mongo连接
    def get_mongo_db(self, client_name):
        client = self.__get_db_pool(client_name)
        if client != {}:
            try:
                client.get_database("admin")
            except Exception as e:
                print(e)
                client = self.__mongo_client(client_name)
        else:
            client = self.__mongo_client(client_name)
        return client


if __name__ == '__main__':
    obj1 = LinkManege()
    obj2 = LinkManege()
    print(obj1, obj2)
