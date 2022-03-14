#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:30
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : mysql_model.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
# -*- coding: UTF-8 -*-
import datetime
import json
from PatternSpider.models.link_manage import *
from PatternSpider.utils.utils import md5_digest
from scrapy.utils.project import get_project_settings
from PatternSpider.utils.time_utils import timestamp_to_datetime

settings = get_project_settings()


class MysqlModel:
    CLIENTNAME = ''
    COLL = ''
    DATABASE = ''
    UNIONFILED = ''
    name = ''

    def __init__(self):
        self.db = LinkManege().get_mysql_db(self.CLIENTNAME)
        self.cursor = self.db.cursor(cursor=pymysql.cursors.DictCursor)

    def find_from_sql(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def find(self, data_dict, limit=None):
        sql = '''select * from {} where %s;'''.format(self.COLL)
        where_list = []
        for k, v in data_dict.items():
            where_list.append('%s="%s"' % (k, v))
        sql %= ' and '.join(where_list)
        self.cursor.execute(sql)
        if limit == 1:
            return self.cursor.fetchone()
        elif limit:
            return self.cursor.fetchmany(limit)
        else:
            return self.cursor.fetchall()

    def insert_one(self, data_dict):
        sql = '''insert into {}(%s) value(%s)'''.format(self.COLL)
        key_list = []
        value_list = []
        for k, v in data_dict.items():
            key_list.append(k)
            value_list.append('%%(%s)s' % k)
        sql = sql % (','.join(key_list), ','.join(value_list))
        try:
            self.cursor.execute(sql, data_dict)
        except Exception as e:
            raise Exception(sql + '\n 这个sql有语法错误 \n' + json.dumps(data_dict) + "\n" + str(e))
        last_id = self.cursor.lastrowid
        self.db.commit()
        return last_id

    def update_one(self, query, data_dict):
        sql = '''update {} set %s where %s'''.format(self.COLL)
        where_list = []
        set_list = []
        for k, v in query.items():
            where_list.append('%s="%s"' % (k, v))
        for k, v in data_dict.items():
            if type(v) == str and '"' in v:
                v = v.replace('"', '')
            set_list.append('%s="%s"' % (k, v))
        sql = sql % (','.join(set_list), ' and '.join(where_list))
        try:
            self.cursor.execute(sql)
        except Exception as e:
            raise Exception(sql + '\n 这个sql有语法错误\n' + str(e))
        self.db.commit()
        return True

    def insert_many(self, sql, data_list):
        try:
            self.cursor.executemany(sql, data_list)
        except Exception as e:
            raise Exception(sql + '\n 这个sql有语法错误\n' + str(e))
        self.db.commit()
        pass

    def is_exists(self, **kwargs):
        query = kwargs.get('query', '')
        if query and type(query) == dict:
            return self.find(query, 1)
        return self.find({self.UNIONFILED: kwargs['item'][self.UNIONFILED]}, 1)


class TableImage(MysqlModel):
    CLIENTNAME = 'MYSQL_BT_RESOURCE'
    DATABASE = 'bt-resource'
    COLL = 'image'
    UNIONFILED = 'url'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)

    def run(self, item):
        # 插入数据
        minio_set = settings.get('MINIO_DVIDS_IMAGE')
        data_dict = {
            "photo_source": item['photo_source'],
            "photo_id": item['photo_id'],
            "photo_url": item['photo_url'],
            "url": item['url'],
            "title": item['title'],
            "content": item['content'],
            "location_up": item['location_up'],
            "photo_date": item['photo_date'],
            "photo_by": item['photo_by'],
            "the_unit": item['the_unit'],
            "date_taken": item['date_taken'],
            "date_posted": item['date_posted'],
            "virin": item['virin'],
            "resolution": item['resolution'],
            "size": item['size'],
            "location": item['location'],
            "keywords": item['keywords'],
            "df": 0,
            "created_by": "wsp",
            "updated_by": "wsp",
            "md5_value": md5_digest(item['url']),
            "local_photo_url": "{}:{}/{}/{}.jpg".format(
                minio_set['host'],
                minio_set['port'],
                minio_set['bucket'],
                item['photo_id']),
            "loc_url": "/home/data1/{}/{}.jpg".format(minio_set['bucket'], item['photo_id']),
        }
        res = self.is_exists(item=item)
        if not res:
            self.insert_one(data_dict=data_dict)
        else:
            self.update_one(query={self.UNIONFILED: item[self.UNIONFILED]}, data_dict=data_dict)
        return True


class TableTag(MysqlModel):
    CLIENTNAME = 'MYSQL_BT_RESOURCE'
    DATABASE = 'bt-resource'
    COLL = 'tag'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)

    def insert_many(self, item, sql=''):
        # insert tag table
        data_list = [(item['photo_id'], i, 'raw', 0, 'wsp', 'wsp') for i in item['tag_name']]
        sql = "insert into {}(photo_id, tag_name, tag_type, df, created_by, updated_by) value (%s, %s, %s, %s, %s, %s)".format(
            self.COLL)
        super(TableTag, self).insert_many(sql=sql, data_list=data_list)

    def run(self, item, spider_name):
        return self.insert_many(item=item)


class TableFBUser(MysqlModel):
    CLIENTNAME = 'MYSQL_DT'
    DATABASE = 'social_data'
    COLL = 'fb_user'
    UNIONFILED = 'userid'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)

    def run(self, item):
        # 插入数据
        data_dict = {
            "userid": item.get("userid", ""),
            "name": item.get("name", ""),
            "jumpname": item.get("jumpname", ""),
            "nickname": item.get("nickname", ""),
            "homepage": item.get("homepage", ""),
            # "register_time": item.get("register_time", ""),
            "gender": item.get("gender", ""),
            # "birthday": item.get("birthday", ""),
            # "sexual_orientation": item.get("sexual_orientation", ""),
            # "language": item.get("language", ""),
            "marital_status": item.get("relationship", ""),
            "hometown": item.get("hometown", ""),
            "current_residence": item.get("current_city", ""),
            "work_experience": item.get("work", ""),
            "edu_experience": item.get("education", ""),
            "images": item.get("avatar", ""),
            # "overview": item.get("overview", ""),
            # "places": item.get("places", ""),
            # "life_events": item.get("life_events", ""),
            # "details": item.get("details", ""),
            # "family_and_relations": item.get("family_and_relations", ""),
            # "contact_and_basicinfo": item.get("contact_and_basicinfo", ""),
            # "work_and_edu": item.get("work_and_edu", ""),
            # "identity_status": item.get("identity_status", ""),
            # "object_type": item.get("object_type", ""),
            # "object_number": item.get("object_number", ""),
            "source": "self_spider",
            "updated_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "updated_by": "lff",
            "df": 0,
        }
        res = self.is_exists(item=item)
        if not res:
            item['created_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['created_by'] = "lff"
            self.insert_one(data_dict=data_dict)
        else:
            self.update_one(query={self.UNIONFILED: item[self.UNIONFILED]}, data_dict=data_dict)
        return True


class TableFBFriend(MysqlModel):
    CLIENTNAME = 'MYSQL_DT'
    DATABASE = 'social_data'
    COLL = 'fb_friend'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)

    def run(self, item):
        # 插入数据
        data_dict = {
            "source_userid": item.get("source_userid", ""),
            "source_homepage": item.get("source_homepage", ""),
            "userid": item.get("userid", ""),
            "name": item.get("name", ""),
            "title": item.get("title", ""),
            "atname": item.get("atname", ""),
            "homepage": item.get("homepage", ""),
            "category": item.get("category", ""),
            "avatar": item.get("avatar", ""),
            "source": "self_spider",
            "updated_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "updated_by": "lff",
            "df": 0,
        }
        query = {
            'source_userid': data_dict['source_userid'],
            'userid': data_dict['userid']
        }
        res = self.is_exists(item=item, query=query)
        if not res:
            item['created_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['created_by'] = "lff"
            self.insert_one(data_dict=data_dict)
        else:
            self.update_one(query=query, data_dict=data_dict)
        return True


class TableFBGuess(MysqlModel):
    CLIENTNAME = 'MYSQL_DT'
    DATABASE = 'social_data'
    COLL = 'fb_timeline'
    UNIONFILED = 'post_id'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)

    def run(self, item):
        # 插入数据
        data_dict = {
            "post_id": item['post_id'],
            "post_url": item.get("post_url", ""),
            "title": item.get("title", ""),
            "content": item.get("content", ""),
            "userid": item.get("userid", 0) if item.get("userid", 0) else 0,
            "homepage": item.get("homepage", ""),
            "name": item.get("name", ""),
            "jumpname": item.get("jumpname", ""),
            "profile_picture_url": item.get("profile_picture_url", ""),
            "post_time": item.get("post_time", ""),
            "post_ranges": item.get("post_ranges", ""),
            "post_title_ranges": item.get("post_title_ranges", ""),
            "post_local_attach": item.get("post_local_attach", ""),
            "post_attach": item.get("post_attach", ""),
            # "location": item.get("location", ""),
            # "longitude": item.get("longitude", ""),
            # "latitude": item.get("latitude", ""),
            # "comment_count": item.get("comment_count", ""),
            # "share_count": item.get("share_count", ""),
            # "like_count": item.get("like_count", ""),
            "is_shared": item.get("is_shared", 0),
            # "title_cn": item.get("title_cn", ""),
            "content_cn": item.get("content_cn", ""),
            # "share_title_cn": item.get("share_title_cn", ""),
            "share_content_cn": item.get("share_content_cn", ""),
            # "object_number": item.get("object_number", ""),
            "source": "self_spider",
            "updated_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "updated_by": "lff",
            "df": 0,
        }
        if data_dict['is_shared']:
            data_dict.update({
                "share_userid": item.get("share_userid", 0) if item.get("share_userid", 0) else 0,
                "share_username": item.get("share_username", ""),
                "share_user_homepage": item.get("share_user_homepage", ""),
                "share_post_title_ranges": item.get("share_post_title_ranges", ""),
                "share_post_url": item.get("share_post_url", ""),
                "share_post_time": item.get("share_post_time", ""),
                "share_post_ranges": item.get("share_post_ranges", ""),
                "share_title": item.get("share_title", ""),
                "share_jumpname": item.get("share_jumpname", ""),
                "share_post_local_attach": item.get("share_post_local_attach", ""),
                "share_post_attach": item.get("share_post_attach", ""),
                "share_content": item.get("share_content", ""),
            })
        res = self.is_exists(item=item)
        if not res:
            item['created_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['created_by'] = "lff"
            self.insert_one(data_dict=data_dict)
        else:
            self.update_one(query={self.UNIONFILED: item[self.UNIONFILED]}, data_dict=data_dict)
        return True


class TableFBPostLike(MysqlModel):
    CLIENTNAME = 'MYSQL_DT'
    DATABASE = 'social_data'
    COLL = 'fb_post_like'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)

    def run(self, item):
        # 插入数据
        data_dict = {
            "post_id": item.get('post_id', 0),
            "post_url": item.get('post_url', ""),
            "userid": item.get("userid", ""),
            "username": item.get('username', ""),
            "homepage": item.get("homepage", ""),
            "updated_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "updated_by": "lff",
            "df": 0,
        }
        query = {
            'post_id': data_dict['post_id'],
            'userid': data_dict['userid']
        }
        res = self.is_exists(item=item, query=query)
        if not res:
            item['created_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['created_by'] = "lff"
            self.insert_one(data_dict=data_dict)
        else:
            self.update_one(query=query, data_dict=data_dict)
        return True


class TableFBPostShare(MysqlModel):
    CLIENTNAME = 'MYSQL_DT'
    DATABASE = 'social_data'
    COLL = 'fb_post_share'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)

    def run(self, item):
        # 插入数据
        data_dict = {
            "post_id": item.get('post_id', 0),
            "post_url": item.get('post_url', ""),
            "userid": item.get("userid", ""),
            "username": item.get('username', ""),
            "homepage": item.get("homepage", ""),
            "share_time": item.get("share_time", "") if item.get("share_time", "") else timestamp_to_datetime(0),
            "updated_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "updated_by": "lff",
            "df": 0,
        }
        query = {
            'post_id': data_dict['post_id'],
            'userid': data_dict['userid']
        }
        res = self.is_exists(item=item, query=query)
        if not res:
            item['created_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['created_by'] = "lff"
            self.insert_one(data_dict=data_dict)
        else:
            self.update_one(query=query, data_dict=data_dict)
        return True


class TableFBComment(MysqlModel):
    CLIENTNAME = 'MYSQL_DT'
    DATABASE = 'social_data'
    COLL = 'fb_comment'
    UNIONFILED = 'comment_id'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)

    def run(self, item):
        # 插入数据
        data_dict = {
            "comment_id": item['comment_id'],
            "post_id": item['post_id'],
            "post_url": item.get("post_url", ""),
            "userid": item.get("userid", 0),
            "homepage": item.get("homepage", ""),
            "content": item.get("content", ""),
            "content_cn": item.get("content_cn", ""),
            "local_attach": item.get("local_attach", ""),
            "comment_attach": item.get("comment_attach", ""),
            "comment_time": item.get("comment_time", "") if item.get("comment_time", "") else timestamp_to_datetime(0),
            "updated_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "updated_by": "lff",
            "df": 0,
        }
        res = self.is_exists(item=item)
        if not res:
            item['created_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['created_by'] = "lff"
            self.insert_one(data_dict=data_dict)
        else:
            self.update_one(query={self.UNIONFILED: item[self.UNIONFILED]}, data_dict=data_dict)
        return True


class TableFBTask(MysqlModel):
    CLIENTNAME = 'MYSQL_DT'
    DATABASE = 'social_data'
    COLL = 'fb_task'
    UNIONFILED = 'code'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)


class TableFBOnceUser(MysqlModel):
    CLIENTNAME = 'MYSQL_DT'
    DATABASE = 'social_data'
    COLL = 'fb_once_user'
    UNIONFILED = 'id'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)


class TableFBOncePublic(MysqlModel):
    CLIENTNAME = 'MYSQL_DT'
    DATABASE = 'social_data'
    COLL = 'fb_once_public'
    UNIONFILED = 'id'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)


class TableFBAccount(MysqlModel):
    CLIENTNAME = 'MYSQL_DT'
    DATABASE = 'social_data'
    COLL = 'fb_account'
    UNIONFILED = 'id'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)


class TableFBDailyPublic(MysqlModel):
    CLIENTNAME = 'MYSQL_DT'
    DATABASE = 'social_data'
    COLL = 'fb_daily_public'
    UNIONFILED = 'id'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)


class TableFBDailyUser(MysqlModel):
    CLIENTNAME = 'MYSQL_DT'
    DATABASE = 'social_data'
    COLL = 'fb_daily_user'
    UNIONFILED = 'id'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)


class TableFBPost(MysqlModel):
    CLIENTNAME = 'MYSQL_DT'
    DATABASE = 'social_data'
    COLL = 'fb_post'
    UNIONFILED = 'id'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)


class TableFBInstance(MysqlModel):
    CLIENTNAME = 'MYSQL_DT'
    DATABASE = 'social_data'
    COLL = 'fb_instance'
    UNIONFILED = 'eip_address'
    name = '{}/{}/{}'.format(CLIENTNAME, DATABASE, COLL)

    def update_status(self, eip_address, value: int):
        return self.update_one({"eip_address": eip_address}, {'status': value})
