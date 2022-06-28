#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:30
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : mongo_model.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
import datetime
from PatternSpider.models.link_manage import LinkManege


class MongoModel:
    CLIENTNAME = ''
    DATABASE = ''
    COLL = ''
    UNIONFILED = ''
    name = ''

    def __init__(self):
        client = LinkManege().get_mongo_db(self.CLIENTNAME)
        self.db = client[self.DATABASE]
        self.coll = self.db[self.COLL]

    def find(self, query):
        return self.coll.find(query)

    def find_one_data(self, query):
        return self.coll.find_one(query)

    def insert_one(self, data):
        return self.coll.insert_one(data)

    def update_one_data(self, query, update_data):
        if '$set' not in update_data:
            update_data = {'$set': update_data}
        return self.coll.update_one(query, update_data)

    def update_many_data(self, query, update_data):
        if '$set' not in update_data:
            update_data = {'$set': update_data}
        return self.coll.update_many(query, update_data)

    def find_and_insert_one(self, data, check_field):
        if not self.find_one_data({check_field: data[check_field]}):
            return self.insert_one(data)
        return True

    def save_one_item(self, item: dict, filter_coll: dict):
        if '_id' in item:
            del item['_id']
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item['update_time'] = now_time

        if not self.coll.find_one(filter_coll):
            item['create_time'] = now_time
            self.coll.insert_one(item)
        else:
            self.coll.update_one(filter=filter_coll, update={"$set": item})


class MongoTwitterUser(MongoModel):
    CLIENTNAME = 'MONGO_DT'
    DATABASE = 'twitter'
    COLL = 'user'
    UNIONFILED = 'rest_id'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)

    def run(self, item):
        self.save_one_item(item, {self.UNIONFILED: item[self.UNIONFILED]})


class MongoTwitterGuess(MongoModel):
    CLIENTNAME = 'MONGO_DT'
    DATABASE = 'twitter'
    COLL = 'guess'
    UNIONFILED = 'id_str'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)

    def run(self, item):
        self.save_one_item(item, {self.UNIONFILED: item[self.UNIONFILED]})


class MongoFacebookUser(MongoModel):
    CLIENTNAME = 'MONGO_DT'
    DATABASE = 'facebook'
    COLL = 'user'
    UNIONFILED = 'userid'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)

    def run(self, item):
        self.save_one_item(item, {self.UNIONFILED: item[self.UNIONFILED]})


class MongoFacebookFriend(MongoModel):
    CLIENTNAME = 'MONGO_DT'
    DATABASE = 'facebook'
    COLL = 'friends'
    UNIONFILED = 'user_id_and_friend_id'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)

    def run(self, item):
        filter_coll = {
            'source_userid': item['source_userid'],
            'userid': item['userid'],
        }
        self.save_one_item(item, filter_coll)


class MongoFacebookFriendApi(MongoModel):
    CLIENTNAME = 'MONGO_DT'
    DATABASE = 'facebook'
    COLL = 'friends_api'
    UNIONFILED = 'user_id_and_friend_id'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)

    def run(self, item):
        filter_coll = {
            'source_userid': item['source_userid'],
            'userid': item['userid'],
        }
        self.save_one_item(item, filter_coll)


class MongoFacebookGeuss(MongoModel):
    CLIENTNAME = 'MONGO_DT'
    DATABASE = 'facebook'
    COLL = 'guess'
    UNIONFILED = 'post_id'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)

    def run(self, item):
        self.save_one_item(item, {self.UNIONFILED: item[self.UNIONFILED]})


class MongoFacebookPostLike(MongoModel):
    CLIENTNAME = 'MONGO_DT'
    DATABASE = 'facebook'
    COLL = 'post_like_user'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)

    def run(self, item):
        filter_coll = {
            'post_id': item['post_id'],
            'userid': item['userid'],
        }
        self.save_one_item(item, filter_coll)


class MongoFacebookPostShare(MongoModel):
    CLIENTNAME = 'MONGO_DT'
    DATABASE = 'facebook'
    COLL = 'post_share_user'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)

    def run(self, item):
        filter_coll = {
            'post_id': item['post_id'],
            'userid': item['userid'],
        }
        self.save_one_item(item, filter_coll)


class MongoFacebookPostComment(MongoModel):
    CLIENTNAME = 'MONGO_DT'
    DATABASE = 'facebook'
    COLL = 'post_comment'
    UNIONFILED = 'comment_id'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)

    def run(self, item):
        self.save_one_item(item, {self.UNIONFILED: item[self.UNIONFILED]})


class MongoDeagelEquipmentDir(MongoModel):
    CLIENTNAME = 'MONGO_DT'
    DATABASE = 'deagel'
    COLL = 'equipment_directories'
    UNIONFILED = 'id'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)

    def run(self, item):
        self.save_one_item(item, {self.UNIONFILED: item[self.UNIONFILED]})


class MongoDeagelEquipmentList(MongoModel):
    CLIENTNAME = 'MONGO_DT'
    DATABASE = 'deagel'
    COLL = 'equipment_list'
    UNIONFILED = 'id'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)

    def run(self, item):
        self.save_one_item(item, {self.UNIONFILED: item[self.UNIONFILED]})


class MongoDeagelEquipmentDetail(MongoModel):
    CLIENTNAME = 'MONGO_DT'
    DATABASE = 'deagel'
    COLL = 'equipment_detail'
    UNIONFILED = 'id'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)

    def run(self, item):
        self.save_one_item(item, {self.UNIONFILED: item[self.UNIONFILED]})


class MongoDeagelCountryList(MongoModel):
    CLIENTNAME = 'MONGO_DT'
    DATABASE = 'deagel'
    COLL = 'country_list'
    UNIONFILED = 'id'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)

    def run(self, item):
        self.save_one_item(item, {self.UNIONFILED: item[self.UNIONFILED]})


class MongoDeagelCountryDetail(MongoModel):
    CLIENTNAME = 'MONGO_DT'
    DATABASE = 'deagel'
    COLL = 'country_detail'
    UNIONFILED = 'id'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)

    def run(self, item):
        self.save_one_item(item, {self.UNIONFILED: item[self.UNIONFILED]})


class MongoDeagelReportsList(MongoModel):
    CLIENTNAME = 'MONGO_DT'
    DATABASE = 'deagel'
    COLL = 'reports_list'
    UNIONFILED = 'id'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)

    def run(self, item):
        self.save_one_item(item, {self.UNIONFILED: item[self.UNIONFILED]})


class MongoDeagelReportsDetail(MongoModel):
    CLIENTNAME = 'MONGO_DT'
    DATABASE = 'deagel'
    COLL = 'reports_detail'
    UNIONFILED = 'id'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)

    def run(self, item):
        self.save_one_item(item, {self.UNIONFILED: item[self.UNIONFILED]})


class MongoDeagelNewsList(MongoModel):
    CLIENTNAME = 'MONGO_DT'
    DATABASE = 'deagel'
    COLL = 'news_list'
    UNIONFILED = 'id'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)

    def run(self, item):
        self.save_one_item(item, {self.UNIONFILED: item[self.UNIONFILED]})


class MongoDeagelNewsDetail(MongoModel):
    CLIENTNAME = 'MONGO_DT'
    DATABASE = 'deagel'
    COLL = 'news_detail'
    UNIONFILED = 'id'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)

    def run(self, item):
        self.save_one_item(item, {self.UNIONFILED: item[self.UNIONFILED]})


class MongoDeagelGalleryList(MongoModel):
    CLIENTNAME = 'MONGO_DT'
    DATABASE = 'deagel'
    COLL = 'gallery_list'
    UNIONFILED = 'id'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)

    def run(self, item):
        self.save_one_item(item, {self.UNIONFILED: item[self.UNIONFILED]})


class MongoDeagelGalleryDetail(MongoModel):
    CLIENTNAME = 'MONGO_DT'
    DATABASE = 'deagel'
    COLL = 'gallery_detail'
    UNIONFILED = 'id'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)

    def run(self, item):
        self.save_one_item(item, {self.UNIONFILED: item[self.UNIONFILED]})


class MongoMarineregionsList(MongoModel):
    CLIENTNAME = 'MONGO_DT'
    DATABASE = 'marineregions'
    COLL = 'list'
    UNIONFILED = 'id'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)

    def run(self, item):
        self.save_one_item(item, {self.UNIONFILED: item[self.UNIONFILED]})


class MongoMarineregionsDetail(MongoModel):
    CLIENTNAME = 'MONGO_DT'
    DATABASE = 'marineregions'
    COLL = 'detail'
    UNIONFILED = 'id'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)

    def run(self, item):
        self.save_one_item(item, {self.UNIONFILED: item[self.UNIONFILED]})


class MongoENDBCity(MongoModel):
    CLIENTNAME = 'MONGO_DT'
    DATABASE = 'endbcity'
    COLL = 'list'
    UNIONFILED = 'request_url'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)

    def run(self, item):
        self.save_one_item(item, {self.UNIONFILED: item[self.UNIONFILED]})