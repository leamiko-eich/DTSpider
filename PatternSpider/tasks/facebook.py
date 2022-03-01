#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/28 11:19
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : facebook.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
from PatternSpider.tasks import TaskManage
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.models.mysql_model import TableFBOncePublic, TableFBOnceUser, TableFBTask, TableFBAccount
from PatternSpider.models.mysql_model import TableFBPost, TableFBDailyUser
from PatternSpider.cookies_manage.facebook_cookies import FacebookCookies


class FacebookTask(TaskManage):

    def add_facebook_user_task(self, user_names, priority=1000):
        """
        参数解释：
        user_names，facebook用户列表
        """
        for user in user_names:
            self.write_task_from_spider_name(
                SpiderNames.facebook_user,
                username=user['name'],
                priority=priority
            )
        return SpiderNames.facebook_user

    def add_facebook_user_friends_task(self, user_infos, priority=1000):
        """
        参数解释：
        user_names，facebook用户列表
        """
        for user_info in user_infos:
            self.write_task_from_spider_name(
                SpiderNames.facebook_user_friends,
                source_userid=user_info['userid'],
                source_homepage=user_info['homepage'],
                username=user_info['name'],
                limit_count=user_info.get('limit_count', -1),
                priority=priority
            )
        return SpiderNames.facebook_user_friends

    def add_facebook_user_guess_task(self, facebook_users, limit_day, priority=1000):
        """
        参数解释：
        user_names，facebook用户列表
        """
        for user in facebook_users:
            self.write_task_from_spider_name(
                SpiderNames.facebook_user_guess,
                name=user['name'],
                userid=user['userid'],
                homepage=user['homepage'],
                limit_count=-1,
                limit_day=limit_day,
                priority=priority
            )
        return SpiderNames.facebook_user_guess

    def add_facebook_post_like(self, posts, priority=1000):
        """
        参数解释：
        user_names，facebook用户列表
        """
        for post in posts:
            self.write_task_from_spider_name(
                SpiderNames.facebook_post_like,
                post_url=post['post_url'],
                post_id=post['post_id'],
                limit_count=-1,
                priority=priority
            )
        return SpiderNames.facebook_post_like

    def add_facebook_post_share(self, posts, priority=1000):
        """
        参数解释：
        user_names，facebook用户列表
        """
        for post in posts:
            self.write_task_from_spider_name(
                SpiderNames.facebook_post_share,
                post_url=post['post_url'],
                post_id=post['post_id'],
                limit_count=-1,
                priority=priority
            )

        return SpiderNames.facebook_post_share

    def add_facebook_post_comment(self, posts, priority=1000):
        """
        参数解释：
        user_names，facebook用户列表
        """
        for post in posts:
            self.write_task_from_spider_name(
                SpiderNames.facebook_post_comment,
                post_url=post['post_url'],
                post_id=post['post_id'],
                limit_count=-1,
                priority=priority
            )
        return SpiderNames.facebook_post_comment

    def add_task_from_msyql(self, mode, account_id, code, group_id):
        spider_name = ''
        fb_account = TableFBAccount()
        # 采集账号获取
        account_info = fb_account.find({'id': int(account_id)}, 1)
        FacebookCookies().write_to_redis(account_info['username'], account_info['password'], account_info['login_key'])

        # 被采集信息获取
        if mode == "once":
            fb_task = TableFBTask()
            task_info = fb_task.find({'code': code}, 1)
            # 是否是公共主页
            is_public = int(task_info['is_public'])
            # 优先级
            priority = int(task_info['priority'])
            # 采集类型
            spider_type = int(task_info['type'])
            # 任务组编号
            group_code = task_info['group_code']
            #
            day_length = task_info['day_length']

            if spider_type in [1, 2, 3]:
                fb_user = TableFBOncePublic() if is_public == 1 else TableFBOnceUser()
                fb_users = fb_user.find({'task_group_code': group_code, 'group_id': int(group_id)})
                if spider_type == 1:
                    spider_name = self.add_facebook_user_friends_task(fb_users, priority)
                elif spider_type == 2:
                    spider_name = self.add_facebook_user_task(fb_users, priority)
                elif spider_type == 3:
                    spider_name = self.add_facebook_user_guess_task(fb_users, day_length, priority)
            elif spider_type in [4, 5, 6]:
                fb_posts = TableFBPost().find({'task_group_code': group_code, 'group_id': int(group_id)})
                if spider_type == 4:
                    spider_name = self.add_facebook_post_comment(fb_posts, priority)
                elif spider_type == 5:
                    spider_name = self.add_facebook_post_like(fb_posts, priority)
                elif spider_type == 6:
                    spider_name = self.add_facebook_post_share(fb_posts, priority)
        else:
            assert mode == 'daily'
            fb_user = TableFBDailyUser()
            fb_users = fb_user.find({'group_id': int(group_id)})
            spider_name = self.add_facebook_user_guess_task(fb_users, 2)

        return spider_name
