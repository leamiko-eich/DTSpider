#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/4/19 11:12
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : neo4j_model.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
from PatternSpider.models.link_manage import LinkManege
from py2neo import Node, Relationship, NodeMatcher, RelationshipMatcher


class Neo4jModel:
    """
        node 的结构：
            {
                node_data:{
                    label:"",
                    query:{},
                    data:{}
                },
                from_data_query:{
                    label:"",
                    query:{},
                    relationship_data:{
                    label:"",
                    data:{}
                }},
                to_data_query:{
                    label:"",
                    query:{},
                    relationship_data:{
                    label:"",
                    data:{}
                }}
            }
        """
    CLIENTNAME = 'NEO4J_LOCAL'

    def __init__(self):
        self.graph = LinkManege().get_neo4j_db(self.CLIENTNAME)
        self.relation_matcher = RelationshipMatcher(self.graph)
        self.node_matcher = NodeMatcher(self.graph)

    def find_node(self, label, query: dict):
        return self.node_matcher.match(label).where(**query).first()

    def __insert_node(self, label, item: dict):
        node = Node(label, **item)
        self.graph.create(node)
        return node

    def find_relationship(self, start_node, end_node, label):
        return self.relation_matcher.match({start_node, end_node}, r_type=label).all()

    def __insert_relationship(self, from_node, relationship_label, to_node, item):
        relationship = Relationship(from_node, relationship_label, to_node, **item)
        self.graph.create(relationship)

    def save_node(self, item):
        node_data = item['node_data']
        # 先创建节点
        node = self.find_node(node_data['label'], node_data['query'])
        if not node:
            print("没有节点，开始创建节点")
            node = self.__insert_node(node_data['label'], node_data['data'])
        else:
            print('节点已存在，不保存节点')

        if "from_data_query" in item and item['from_data_query']:
            print('节点有爸爸，开始建立关系')
            from_data_query = item['from_data_query']
            start_node = self.find_node(from_data_query['label'], from_data_query['query'])
            if start_node:
                relationship_data = from_data_query['relationship_data']
                if not self.find_relationship(start_node, node, relationship_data['label']):
                    print('关系不存在，开始建立关系')
                    self.__insert_relationship(start_node, relationship_data['label'], node, relationship_data['data'])
                else:
                    print('关系已存在，不重复建立关系')
            else:
                print('爸爸不存在，建立关系失败')

        if "to_data_query" in node and node['to_data_query']:
            print('节点有儿子，开始建立关系')
            to_data_query = node['to_data_query']
            end_node = self.find_node(to_data_query['label'], to_data_query['query'])
            if end_node:
                print('有儿子')
                relationship_data = to_data_query['relationship_data']
                if not self.find_relationship(node, end_node, relationship_data['label']):
                    print('不存在关系，开始建立')
                    self.__insert_relationship(node, relationship_data['label'], end_node, relationship_data['data'])
                else:
                    print('已存在关系')
            else:
                print('没儿子')
