#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:32
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : spider_names.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved

class SpiderNames:
    # 海军图片信息
    dvidshub_search = 'dvidshub_search'
    dvidshub_detail = 'dvidshub_detail'
    # 机场信息
    airportnavfinder_list = 'airportnavfinder_list'
    airportnavfinder_detail = 'airportnavfinder_detail'

    # 推特：
    twitter_guess = 'twitter_guess'
    twitter_user = 'twitter_user'

    # flickr
    flickr_guess = 'flickr_guess'

    # facebook
    facebook_user = 'facebook_user'
    facebook_user_friends = 'facebook_user_friends'
    facebook_user_guess = 'facebook_user_guess'

    facebook_post_like = 'facebook_post_like'
    facebook_post_share = 'facebook_post_share'
    facebook_post_comment = 'facebook_post_comment'


SpiderTableNames = {
    # dvidshun spider image data:
    SpiderNames.dvidshub_detail: {
        'mysql': [
            'MYSQL_BT_RESOURCE/bt-resource/image',
            'MYSQL_BT_RESOURCE/bt-resource/tag'
        ]
    },
    SpiderNames.flickr_guess: {
        'msyql': ['MYSQL_BT_RESOURCE/bt-resource/image']
    },
    SpiderNames.twitter_guess: {
        'mongo': ['MONGO_DT/twitter/guess']
    },
    SpiderNames.twitter_user: {
        'mongo': ['MONGO_DT/twitter/user']
    },
    SpiderNames.facebook_user: {
        'mongo': ['MONGO_DT/facebook/user'],
        'mysql': ['MYSQL_DT/social_data/fb_user']
    },
    SpiderNames.facebook_user_friends: {
        'mongo': ['MONGO_DT/facebook/friends'],
        'mysql': ['MYSQL_DT/social_data/fb_friend']
    },
    SpiderNames.facebook_user_guess: {
        'mongo': ['MONGO_DT/facebook/guess'],
        'mysql': ['MYSQL_DT/social_data/fb_timeline']
    },
    SpiderNames.facebook_post_like: {
        'mongo': ['MONGO_DT/facebook/post_like_user'],
        'mysql': ['MYSQL_DT/social_data/fb_post_like']
    },
    SpiderNames.facebook_post_share: {
        'mongo': ['MONGO_DT/facebook/post_share_user'],
        'mysql': ['MYSQL_DT/social_data/fb_post_share']
    },
    SpiderNames.facebook_post_comment: {
        'mongo': ['MONGO_DT/facebook/post_comment'],
        'mysql': ['MYSQL_DT/social_data/fb_comment']
    }

}
