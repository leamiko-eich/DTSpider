#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/28 11:19
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : facebook.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
import json

from PatternSpider.models.redis_model import OriginSettingsData
from PatternSpider.tasks import TaskManage
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.models.mysql_model import TableFBTask, TableFBAccount, TableFBInstance
from PatternSpider.models.mysql_model import TableFBDailyUser
from PatternSpider.cookies_manage.facebook_cookies import FacebookAccount, FacebookCookies
from PatternSpider.spiders.facebook import FacebookUtils


class FacebookTask(TaskManage):
    facebook_utils = FacebookUtils()
    task_type_mapping = {
        1: "fd_status", 2: "ui_status", 3: "tl_status", 4: "c_status", 5: "l_status", 6: "s_status"
    }

    def add_facebook_user_task(self, user_infos, **kwargs):
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
                limit_count=user_info.get('limit_count', 2000),
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
                limit_count=2000,
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
                limit_count=2000,
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
                limit_count=2000,
                total_task_infos=total_task_infos
            )
        return SpiderNames.facebook_post_comment

    def add_task_from_mysql(self, mode, account_id, code, group_ids):

        total_task_infos = {
            'mode': mode,
            'account_id': account_id,
            'code': code,
            'task_type_mapping': self.task_type_mapping
        }
        spider_name = SpiderNames.facebook_user
        fb_account = TableFBAccount()
        # 采集账号获取
        account_info = fb_account.find({'id': int(account_id)}, 1)
        FacebookAccount().write_to_redis(account_info['username'], account_info['password'], account_info['login_key'])
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
                    self.task_type_mapping[spider_type]: 0
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
        return spider_name, len(fb_mysql_task)

    def update_account_info(self, settings_data, ding):
        cookies = FacebookCookies().get_random_username_cookie()
        login_result = cookies['login_result']
        if login_result['login_res'] == 0:
            # 修改账号状态
            TableFBAccount().update_one(
                {'id': settings_data['account_id']},
                {'status': login_result['account_status'], 'is_using': 0}
            )
            ding += "理由：账号登录失败{}".format(login_result['account_status'])
        else:
            # 账号rank+1,daily_use_count+1
            account_info = TableFBAccount().find({'id': settings_data['account_id']}, 1)
            account_info['daily_use_count'] = account_info['daily_use_count'] if account_info[
                'daily_use_count'] else 0
            account_info['account_rank'] = account_info['account_rank'] if account_info['account_rank'] else 0
            account_rank = account_info['account_rank'] + 1
            daily_use_count = account_info['daily_use_count'] + 1
            TableFBAccount().update_one(
                {'id': settings_data['account_id']},
                {'account_rank': account_rank, 'daily_use_count': daily_use_count, 'is_using': 0}
            )
        return ding

    def update_task_status(self, spider_name, ding):
        # 失败任务修改任务状态为
        faileds_tasks = self.get_mirror_task(spider_name)
        for faileds_task in faileds_tasks:
            self.facebook_utils.update_current_user_status(json.loads(faileds_task), 3)
        ding += "理由：正常结束,失败任务数量:{}".format(len(faileds_tasks))
        return ding

    def end_task(self, spider_name):
        # 获取原始数据
        settings_data = OriginSettingsData().get_settings_data()
        ding = "关闭采集程序：instance_id:{},allocation_id:{}、采集程序：{}\n".format(
            settings_data['instance_id'], settings_data['allocation_id'], spider_name)
        # 修改账号状态
        ding = self.update_account_info(settings_data, ding)
        # 修改被采集账号任务状态
        ding = self.update_task_status(spider_name, ding)
        # # 上报日志：
        # log_upload(
        #     task_code=settings_data['code'],
        #     group_id=','.join(settings_data['group_id']),
        #     log_name=spider.name
        # )
        # 获取当前机器实例id，并更新数据库状态为3
        TableFBInstance().update_one(
            {'status': 1, 'instance_id': settings_data['instance_id'],
             'allocation_id': settings_data['allocation_id']},
            {'status': 3}
        )
        return ding
