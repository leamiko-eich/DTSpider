#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:29
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : elasticsearch_model.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
# coding=utf-8
from PatternSpider.models.link_manage import LinkManege


class ESModel:
    CLIENTNAME = ''
    INDEX = ''
    DOC_TYPE = ''

    def __init__(self):
        self.es = LinkManege().get_es_db(self.CLIENTNAME)

    def insert_one(self, es_id, body):
        return self.es.index(index=self.INDEX, doc_type=self.DOC_TYPE, id=es_id, body=body)

    def creat_one(self, es_id, body):
        return self.es.create(index=self.INDEX, doc_type=self.DOC_TYPE, id=es_id, body=body)

    def delete_one(self, es_id):
        return self.es.delete(index=self.INDEX, doc_type=self.DOC_TYPE, id=es_id)

    def delete_by_query(self, query):
        return self.es.delete_by_query(index=self.INDEX, doc_type=self.DOC_TYPE, body=query)

    def search(self, query=None):
        return self.es.search(index=self.INDEX, doc_type=self.DOC_TYPE, body=query)

    def update_one(self, es_id, body):
        if "doc" not in body:
            body = {"doc": body}
        return self.es.update(index=self.INDEX, doc_type=self.DOC_TYPE, id=es_id, body=body)
