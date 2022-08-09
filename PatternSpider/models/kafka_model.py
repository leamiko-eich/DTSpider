#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/4/19 11:12
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : kafka_model.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
import json
from PatternSpider.models.link_manage import LinkManege


class KafkaModel:
    CLIENTNAME = ''
    TOPIC = ''
    PARTITION = 0

    def __init__(self):
        self.client = LinkManege().get_kafka_client(self.CLIENTNAME)

    def __del__(self):
        try:
            self.client.flush()
        except:
            pass

    @staticmethod
    def clean_data(kafka_data):
        over_data = {}
        for i in kafka_data:
            if kafka_data[i] is None or kafka_data[i] == 'None':
                continue
            over_data[i] = kafka_data[i]
        return json.dumps(over_data).encode()

    def producer_datas(self, data):
        try:
            assert type(data) == dict
            future = self.client.send(self.TOPIC, self.clean_data(data))
            record_metadata = future.get(timeout=2)
            print("future对象:", record_metadata)
            print("======================================================")
            print("接收的topic:", record_metadata.topic)
            print("partition_ID:", record_metadata.partition)
            print("offset:", record_metadata.offset)
            print("==========发送成功============")
        except Exception as e:
            print(e)


class KafkaPatternFBTimelineConsumer(KafkaModel):
    CLIENTNAME = 'KAFKA_HUAWEI_PRODUCER'
    TOPIC = 'lff_pattern_fb_timeline'
    PARTITION = 0
    name = '{}/{}'.format(CLIENTNAME, TOPIC)

    def run(self, item):
        # 插入数据
        data_dict = {
            "created_by": "lff",
            "updated_by": "lff",
            "post_id": item.get('post_id', None),
            "post_url": item.get('post_url', None),
            "title": item.get('title', None),
            "content": item.get('content', None),
            "account": item.get('userid', None),
            "account_homepage": item.get('homepage', None),
            "account_name": item.get('name', None),
            "account_jumpname": item.get('jumpname', None),
            "profile_picture_url": item.get('profile_picture_url', None),
            "share_account": item.get('share_userid', None),
            "share_account_name": item.get('share_username', None),
            "share_account_homepage": item.get('share_user_homepage', None),
            "share_post_title_ranges": item.get('share_post_title_ranges', None),
            "share_post_url": item.get('share_post_url', None),
            "share_post_time": str(item.get('share_post_time', None)),
            "share_post_ranges": item.get('share_post_ranges', None),
            "post_time": str(item.get('post_time', None)),
            "share_title": item.get('share_title', None),
            "share_jump_name": item.get('share_jumpname', None),
            "share_post_attach": item.get('share_post_attach', None),
            "post_ranges": item.get('post_ranges', None),
            "post_title_ranges": item.get('post_title_ranges', None),
            "post_num": "",
            "post_attach": item.get('post_attach', None),
            "share_content": item.get('share_content', None),
            "location": item.get('location', None),
            "longitude": item.get('longitude', None),
            "latitude": item.get('latitude', None),
            "comment_count": item.get('comment_count', None),
            "share_count": item.get('share_count', None),
            "like_count": item.get('like_count', None),
            "is_shared": item.get('is_shared', None),
            "title_cn": item.get('title_cn', None),
            "content_cn": item.get("content_cn", None),
            "share_title_cn": item.get('share_title_cn', None),
            "share_content_cn": item.get('share_content_cn', None),
            "object_number": item.get('object_number', None),
        }
        self.producer_datas(data_dict)
        return True


class KafkaPatternFBUserConsumer(KafkaModel):
    CLIENTNAME = 'KAFKA_HUAWEI_PRODUCER'
    TOPIC = 'lff_pattern_fb_user'
    PARTITION = 0
    name = '{}/{}'.format(CLIENTNAME, TOPIC)

    def run(self, item):
        # 插入数据
        data_dict = {
            "created_by": "lff",
            "updated_by": "lff",
            "account": item.get('userid', None),
            "name": item.get('name', None),
            "jumpname": item.get('jumpname', None),
            "homepage": item.get('homepage', None),
            "register_time": item.get('register_time', None),
            "gender": item.get('gender', None),
            "birthday": item.get('birthday', None),
            "sexual_orientation": item.get('sexual_orientation', None),
            "language": item.get('language', None),
            "marital_status": item.get('relationship', None),
            "hometown": item.get('hometown', None),
            "current_residence": item.get('current_city', None),
            "work_experience": item.get('work', None),
            "edu_experience": item.get('education', None),
            # "family_info": item.get('family_info',None),
            # "life_chronicle": item.get('created_by',None),
            "object_number": item.get('object_number', None),
            "images": item.get('avatar', None),
            "overview": item.get('overview', None),
            "places": item.get('places', None),
            "life_events": item.get('life_events', None),
            "details": item.get('details', None),
            "family_and_relations": item.get('family_and_relations', None),
            "contact_and_basicinfo": item.get('contact_and_basicinfo', None),
            "work_and_edu": item.get('work_and_edu', None),
            # "identity_status": item.get('identity_status',None),
            "object_type": item.get('object_type', None),
        }
        self.producer_datas(data_dict)
        return True


class KafkaPatternFBFriendConsumer(KafkaModel):
    CLIENTNAME = 'KAFKA_HUAWEI_PRODUCER'
    TOPIC = 'lff_pattern_fb_friend'
    PARTITION = 0
    name = '{}/{}'.format(CLIENTNAME, TOPIC)

    def run(self, item):
        # 插入数据
        data_dict = {
            "created_by": "lff",
            "updated_by": "lff",
            "source_account": item.get("source_userid", None),
            "account": item.get("userid", None),
            "name": item.get("name", None),
            "title": item.get("title", None),
            "atname": item.get("atname", None),
            "homepage": item.get("homepage", None),
            "category": item.get("category", None),
            "avatar": item.get("avatar", None)
        }
        self.producer_datas(data_dict)
        return True


class KafkaPatternTestConsumer(KafkaModel):
    CLIENTNAME = 'KAFKA_HUAWEI_PRODUCER'
    TOPIC = 'lff_test'
    PARTITION = 0
    name = '{}/{}'.format(CLIENTNAME, TOPIC)

    def run(self, item):
        # 插入数据
        print(item)
