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
from PatternSpider.models.mysql_model import TableFBTask, TableFBAccount
from PatternSpider.models.mysql_model import TableFBDailyUser
from PatternSpider.cookies_manage.facebook_cookies import FacebookCookies
from PatternSpider.spiders.facebook import FacebookUtils


class FacebookTask(TaskManage):
    facebook_utils = FacebookUtils()

    def add_facebook_user_task(self, user_infos, **kwargs):
        """
        参数解释：
        user_names，facebook用户列表
        """
        total_task_infos = kwargs.get('total_task_infos', {})
        for user_info in user_infos:
            # del user_info['created_time']
            # del user_info['updated_time']
            total_task_infos['user_info'] = user_info
            self.write_task_from_spider_name(
                SpiderNames.facebook_user,
                username=user_info['homepage'].replace("https://www.facebook.com/", ''),
                total_task_infos=total_task_infos
            )
        return SpiderNames.facebook_user

    def add_facebook_user_friends_task(self, user_infos, **kwargs):
        """
        参数解释：
        user_names，facebook用户列表
        """
        total_task_infos = kwargs.get('total_task_infos', '')
        for user_info in user_infos:
            del user_info['created_time']
            del user_info['updated_time']
            total_task_infos['user_info'] = user_info
            self.write_task_from_spider_name(
                SpiderNames.facebook_user_friends,
                source_userid=user_info['userid'],
                source_homepage=user_info['homepage'],
                username=user_info['homepage'].replace('https://www.facebook.com/', ''),
                limit_count=user_info.get('limit_count', 500),
                total_task_infos=total_task_infos
            )
        return SpiderNames.facebook_user_friends

    def add_facebook_user_guess_task(self, user_infos, **kwargs):
        """
        参数解释：
        user_names，facebook用户列表
        """
        total_task_infos = kwargs.get('total_task_infos', {})
        for user_info in user_infos:
            del user_info['created_time']
            del user_info['updated_time']
            total_task_infos['user_info'] = user_info
            self.write_task_from_spider_name(
                SpiderNames.facebook_user_guess,
                name=user_info['name'],
                username=user_info['homepage'].replace('https://www.facebook.com/', ''),
                userid=user_info['userid'],
                homepage=user_info['homepage'],
                limit_count=500,
                limit_day=total_task_infos['task_info']['day_length'],
                total_task_infos=total_task_infos
            )
        return SpiderNames.facebook_user_guess

    def add_facebook_post_like(self, posts, **kwargs):
        """
        参数解释：
        user_names，facebook用户列表
        """
        total_task_infos = kwargs.get('total_task_infos', '')
        for post in posts:
            del post['created_time']
            del post['updated_time']
            total_task_infos['post_info'] = post
            self.write_task_from_spider_name(
                SpiderNames.facebook_post_like,
                post_url=post['post_url'].replace("\\/", "/").replace("\/", "/"),
                post_id=post['post_id'],
                limit_count=500,
                total_task_infos=total_task_infos
            )
        return SpiderNames.facebook_post_like

    def add_facebook_post_share(self, posts, **kwargs):
        """
        参数解释：
        user_names，facebook用户列表
        """
        total_task_infos = kwargs.get('total_task_infos', '')
        for post in posts:
            del post['created_time']
            del post['updated_time']
            total_task_infos['post_info'] = post
            self.write_task_from_spider_name(
                SpiderNames.facebook_post_share,
                post_url=post['post_url'].replace("\\/", "/").replace("\/", "/"),
                post_id=post['post_id'],
                limit_count=500,
                total_task_infos=total_task_infos
            )

        return SpiderNames.facebook_post_share

    def add_facebook_post_comment(self, posts, **kwargs):
        """
        参数解释：
        user_names，facebook用户列表
        """
        total_task_infos = kwargs.get('total_task_infos', '')
        for post in posts:
            del post['created_time']
            del post['updated_time']
            total_task_infos['post_info'] = post
            self.write_task_from_spider_name(
                SpiderNames.facebook_post_comment,
                post_url=post['post_url'].replace("\\/", "/").replace("\/", "/"),
                post_id=post['post_id'],
                limit_count=500,
                total_task_infos=total_task_infos
            )
        return SpiderNames.facebook_post_comment

    def add_task_from_mysql(self, mode, account_id, code, group_ids):
        task_type_mapping = {
            1: "fd_status", 2: "ui_status", 3: "tl_status", 4: "c_status", 5: "l_status", 6: "s_status"
        }
        total_task_infos = {
            'mode': mode,
            'account_id': account_id,
            'code': code,
            'task_type_mapping': task_type_mapping
        }
        spider_name = SpiderNames.facebook_user
        fb_account = TableFBAccount()
        # 采集账号获取
        account_info = fb_account.find({'id': int(account_id)}, 1)
        FacebookCookies().write_to_redis(account_info['username'], account_info['password'], account_info['login_key'])
        fb_mysql_task = []
        if mode == "once":
            fb_task = TableFBTask()
            task_info = fb_task.find({'code': code}, 1)
            del task_info['created_time']
            del task_info['updated_time']
            total_task_infos['task_info'] = task_info
            # 采集类型
            spider_type = int(task_info['type'])
            # 被采集信息获取
            table = self.facebook_utils.get_table_from_task(mode, spider_type, int(task_info['is_public']))
            for group_id in group_ids:
                fb_mysql_task += table.find({
                    'task_group_code': task_info['group_code'],
                    'group_id': int(group_id),
                    task_type_mapping[spider_type]: 0
                })

            # 开始添加任务到redis
            if spider_type == 1:
                spider_name = self.add_facebook_user_friends_task(
                    user_infos=fb_mysql_task,
                    total_task_infos=total_task_infos
                )
            elif spider_type == 2:
                spider_name = self.add_facebook_user_task(
                    user_infos=fb_mysql_task,
                    total_task_infos=total_task_infos
                )
            elif spider_type == 3:
                spider_name = self.add_facebook_user_guess_task(
                    user_infos=fb_mysql_task,
                    total_task_infos=total_task_infos
                )
            elif spider_type == 4:
                spider_name = self.add_facebook_post_comment(
                    posts=fb_mysql_task,
                    total_task_infos=total_task_infos
                )
            elif spider_type == 5:
                spider_name = self.add_facebook_post_like(
                    posts=fb_mysql_task,
                    total_task_infos=total_task_infos
                )
            elif spider_type == 6:
                spider_name = self.add_facebook_post_share(
                    posts=fb_mysql_task,
                    total_task_infos=total_task_infos
                )
        elif mode == 'daily':
            fb_user = TableFBDailyUser()
            for group_id in group_ids:
                fb_mysql_task += fb_user.find({'group_id': int(group_id)})

            spider_name = self.add_facebook_user_guess_task(
                user_infos=fb_mysql_task,
                total_task_infos=total_task_infos
            )
        return spider_name


if __name__ == '__main__':
    user_infos = [
        {"homepage": "https://www.facebook.com/jaleel.daniels"},
        {"homepage": "https://www.facebook.com/donte.gordon.71"},
        {"homepage": "https://www.facebook.com/profile.php?id=100011746563640"},
        {"homepage": "https://www.facebook.com/patrick.tembreull"},
        {"homepage": "https://www.facebook.com/nathan.cohen.165"},
        {"homepage": "https://www.facebook.com/joseph.ellul.90"},
        {"homepage": "https://www.facebook.com/tyler.ward.3551380"},
        {"homepage": "https://www.facebook.com/lucas.fraustfro"},
    ]
    FacebookTask().add_facebook_user_task(user_infos)
