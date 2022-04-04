#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 18:05
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : base_chrome.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
import json
import os
import random
import time

import requests
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from scrapy.utils.project import get_project_settings
from PatternSpider.cookies_manage.facebook_cookies import FacebookAccount, FacebookCookies
from PatternSpider.utils.js_utils import JsSentence
from PatternSpider.selenium_manage import BaseSelenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait

settings = get_project_settings()


class BaseChrome(BaseSelenium):

    def clear_cache_driver(self):
        """
        ; func desc 清除浏览器缓存（除cookie）
        ; clear_cache_status 类型 bool true代表第一次清除浏览器缓存  false 代表第二次及以上清除浏览器缓存
        ; return False
        """
        # 打开一个新的标签页面 并访问清除浏览器缓存页面
        self.driver.execute_script(JsSentence.open_new_label.format(''))
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.driver.get('chrome://settings/clearBrowserData')
        time.sleep(2)

        # 行为链开始
        actions = ActionChains(self.driver)
        actions.send_keys(Keys.TAB * 4 + Keys.ENTER) if self.clear_cache_status else actions.send_keys(Keys.TAB * 4)
        self.clear_cache_status = False  # 首次之后改成False
        actions.send_keys(Keys.TAB * 3 + Keys.ENTER)
        actions.perform()
        time.sleep(2)  # wait some time to finish

        # 关闭该标签页
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])  # switch back

    @staticmethod
    def get_opened_chrome(headless=True):
        os.chdir(settings.get('CHROME_DIR', ''))
        cmd = "chrome.exe --remote-debugging-port=9992"
        if headless:
            cmd += " --headless"
        os.popen(cmd)  # 启动chrome浏览器
        time.sleep(2)
        options = webdriver.ChromeOptions()
        options._debugger_address = "localhost:9992"
        return webdriver.Chrome(chrome_options=options)

    @staticmethod
    def get_log_options(headless):
        option = webdriver.ChromeOptions()
        option.add_argument('--no-sandbox')
        option.add_argument('--disable-gpu')
        option.add_argument('--headless') if headless else None
        option.add_argument("--disable-extensions")
        option.add_argument("--allow-running-insecure-content")
        option.add_argument("--ignore-certificate-errors")
        option.add_argument("--disable-single-click-autofill")
        option.add_argument("--disable-autofill-keyboard-accessory-view[8]")
        option.add_argument("--disable-full-form-autofill-ios")
        option.add_experimental_option('prefs',
                                       {'profile.default_content_setting_values': {'notifications': 2, 'images': 2}})

        # 避免检测 and 不打印logger
        # options.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
        option.add_argument(
            'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:55.0) Gecko/20100101 Firefox/55.0')
        option.add_experimental_option('w3c', False)
        option.add_experimental_option('perfLoggingPrefs', {
            'enableNetwork': True,
            'enablePage': False,
        })
        return option

    @staticmethod
    def get_caps():
        """
        :return: chrome 日志配置
        """
        caps = DesiredCapabilities.CHROME
        caps['loggingPrefs'] = {
            'browser': 'ALL',
            'performance': 'ALL',
        }
        caps['perfLoggingPrefs'] = {
            'enableNetwork': True,
            'enablePage': False,
            'enableTimeline': False
        }
        return caps

    def get_new_chrome(self, headless=True):
        options = self.get_log_options(headless)
        desired_capabilities = self.get_caps()
        # 这里也可以对options和caps加入其他的参数，比如代理参数等
        for i in [96, 97, 98, 99]:
            try:
                chrome = webdriver.Chrome(
                    executable_path=os.path.join(os.getcwd(), 'chromedrivers\\chromedriver_{}.exe'.format(i)),
                    options=options,
                    desired_capabilities=desired_capabilities
                )
                return chrome
            except Exception as e:
                print(e)
                continue
        print("启动浏览器失败")
        exit(1)

    def get_api_data(self, match_url):
        log_xhr_array = []
        for typelog in self.driver.log_types:
            perfs = self.driver.get_log(typelog)
            for row in perfs:
                log_data = row
                message_ = log_data['message']
                try:
                    log_json = json.loads(message_)
                    log = log_json['message']
                    if log['method'] == 'Network.responseReceived':
                        # 去掉静态js、css等，仅保留xhr请求
                        type_ = log['params']['type']
                        if type_ == "XHR":
                            log_xhr_array.append(log)
                except:
                    continue

        match_requestids = []
        for index, i in enumerate(log_xhr_array):
            if i['params']['response']['url'] == match_url:
                match_requestids.append(i['params']['requestId'])

        contents = []
        for requestid in match_requestids:
            try:
                # 通过requestId获取接口内容
                content = self.driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': requestid})
                post_data = self.driver.execute_cdp_cmd('Network.getRequestPostData', {'requestId': requestid})
                content.update({"postData": post_data['postData']})
                contents.append(content)
            except:
                continue
        return contents

    def get_handle(self, handle_index):
        # 获取所有窗口的句柄
        handles = self.driver.window_handles

        # 切换到指定标签
        if type(handle_index) == int:
            self.driver.switch_to.window(handles[handle_index])
        else:
            assert type(handle_index) == str
            self.driver.switch_to.window(handle_index)

    def get_page_source(self, handle_index):
        self.get_handle(handle_index)
        # 获取当前页面源代码
        return self.driver.page_source

    def scroll_by(self, length=3000):
        for i in range(5):
            self.driver.execute_script("window.scrollBy(0,{})".format(int(length / 5)))
            # 睡眠时间，随机 0.1s-0.5s 保留三位小数
            time.sleep(round(random.uniform(1, 3), 3))
        time.sleep(5)

    def scroll_by_key(self, task):
        if 'need_tab' in task:
            ActionChains(self.driver).send_keys(Keys.TAB * int(task['need_tab'])).perform()
            time.sleep(2)

        down_num = int(task['down_num']) if 'down_num' in task else 2
        actions = ActionChains(self.driver)
        actions.send_keys(Keys.DOWN * random.randint(5, 100))
        actions.send_keys(Keys.UP * random.randint(1, 5))
        actions.send_keys(Keys.DOWN * random.randint(5, 100))
        actions.send_keys(Keys.UP * random.randint(5, 10))
        for i in range(down_num):
            actions.perform()
            time.sleep(round(random.uniform(0.1, 0.5), 3))

    def scroll_is_over(self):
        check_height = self.driver.execute_script("return document.body.scrollHeight;")  # 当前滚动条的高度
        check_height_after = self.driver.execute_script("return document.body.scrollHeight;")  # 滚动后滚动条的高度
        # 如果两者相等说明到底了
        if check_height == check_height_after:
            return True
        return False

    def scroll_up(self, num=5):
        ActionChains(self.driver).send_keys(Keys.UP * num).perform()

    def scroll_down(self, num=5):
        ActionChains(self.driver).send_keys(Keys.DOWN * num).perform()


class FacebookChrome(BaseChrome):
    URL = "https://www.facebook.com/"

    def __init__(self, logger, headless=True):
        super(self.__class__, self).__init__()
        self.logger = logger
        self.driver = self.get_new_chrome(headless=headless)
        self.facebook_account = FacebookAccount()
        self.facebook_cookie = FacebookCookies()
        account_info = self.get_account()
        self.account = account_info['account']
        self.password = account_info['password']
        self.key = account_info['key']

    def get_account(self):
        """
        :return: 从redis中获取账号信息
        """
        account_info = self.facebook_account.get_random_username_cookie()
        return json.loads(account_info['cookie'])

    def get_token(self):
        """
        :return code 二次验证需要的code
        """
        url = "http://2fa.live/tok/{}".format(self.key)
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en',
            'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
            'Referer': 'https://www.dvidshub.net/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/69.0.3497.100 Safari/537.36',
        }
        try:
            response = requests.get(url=url, headers=headers, timeout=10)
            token = json.loads(response.text)
            token = token["token"]
        except Exception as e:
            self.logger.error(str(e))
            self.logger.error("请手动在浏览器上输入地址：http://2fa.live/tok/{},并在控制台输入code".format(self.key))
            token = None
        return token

    def check_login_result(self):
        login_results = [
            {"account_status": -1, "str_patterns": ["Your account has been disabled"]},
            {"account_status": 3, "str_patterns": ["你的帳號已被鎖住"]},
            {"account_status": 5, "str_patterns": ["Help us confirm it's you"]},
            {"account_status": 6, "str_patterns": ["Suspended Your Account", "We've suspended your account"]},
            {"account_status": 7, "str_patterns": ["帐号或密码无效"]},
        ]
        for i in login_results:
            for j in i['str_patterns']:
                if j in self.driver.page_source:
                    return i['account_status']
        return 0

    def check_login(self):
        """
        :return: bool值 检测当前浏览器是否登录成功

        账号状态，-1：被封（blocked），0：可用，1：备用，2：临时受限，3：锁定（locked），4：出错（Error） 5:需要验证
        "Your account has been disabled"    -1
        login successful 0
        You're Temporarily Blocked/你的帳號已被鎖住 3
        login failed  4
        "Help us confirm it's you"    5
        We Suspended Your Account   6(我们暂停了您的帐户)
        """
        cookies = []
        try:
            account_status = self.check_login_result()
            if account_status != 0:
                return 0, account_status
            login_name = self.driver.find_element_by_xpath(
                '(//*[@class="a8c37x1j ni8dbmo4 stjgntxs l9j0dhe7"])[position()=1]').text
            self.logger.info("登录成功：{}".format(login_name))
            cookies = self.driver.get_cookies()
            login_res, account_status = 1, 0
        except Exception as e:
            self.logger.error('登录失败，请确认。account:{}\nerror:{}'.format(self.account, str(e)))
            login_res, account_status = 0, 4

        login_result = {
            'login_res': login_res,
            'account_status': account_status,
            'cookies': cookies
        }
        self.facebook_cookie.write_to_redis(self.account, login_result)
        return login_res, account_status

    def login_facebook(self):
        """
        账号密码信息在实例化对象时初始化
        :return: bool值 登录之后的浏览器 成功或者失败
        """
        # 访问站点地址
        self.driver.get(url=self.URL)
        self.driver.maximize_window()  # 窗口最大化
        self.driver.implicitly_wait(3)  # 隐式等待

        # 如果已经登录过就不再登录:
        cookies = self.facebook_cookie.get_random_username_cookie()
        if cookies:
            login_result = cookies['login_result']
            if login_result['login_res'] == 1:
                for i in login_result['cookies']:
                    self.driver.add_cookie(i)
                self.driver.refresh()
                time.sleep(3)
                return self.check_login()
            else:
                return 0, 6

        # 输入账号密码
        self.driver.find_element_by_id("email").send_keys(self.account)
        self.driver.find_element_by_id("pass").send_keys(self.password)
        self.driver.find_element_by_name("login").click()

        # 二次验证登录
        token = self.get_token()
        if not token:
            self.logger.error('当前账号获取token失败！!!!! 登录失败')
            return False
        try:
            time.sleep(5)
            self.driver.find_element_by_id("approvals_code").send_keys(token)
            self.driver.find_element_by_id("checkpointSubmitButton").click()
            self.driver.find_element_by_id("checkpointSubmitButton").click()
        except Exception as e:
            self.logger.error(str(e))
            self.logger.error('当前账号无需二次验证')

        # 如果出现异地登录，需要继续点击是本人登录
        try:
            self.driver.find_element_by_id("checkpointSubmitButton").click()
            self.driver.find_element_by_id("checkpointSubmitButton").click()
            self.driver.find_element_by_id("checkpointSubmitButton").click()
        except Exception as e:
            self.logger.error(str(e))

        return self.check_login()

    def login_old(self):
        """旧版登录"""
        # 监听动态请求
        status = True
        self.driver.get(url=self.URL)
        self.driver.maximize_window()  # 窗口最大化
        self.driver.implicitly_wait(3)  # 隐式等待

        try:
            self.logger.info("account:{} pwd:{}".format(self.account, self.password))
            self.driver.find_element_by_name("email").send_keys(self.account)
            self.driver.find_element_by_name("pass").send_keys(self.password)
            self.driver.find_element_by_name("login").click()
        except Exception as e:
            self.logger.error(e)

        # 二次验证登录
        try:
            time.sleep(5)
            token = self.get_token()
            self.driver.find_element_by_id("approvals_code").send_keys(token)
            self.driver.find_element_by_id("checkpointSubmitButton").click()
            self.driver.find_element_by_id("checkpointSubmitButton").click()
        except Exception as e:
            self.logger.info('当前账号无需二次验证', e)

        # 如果出现异地登录，需要继续点击是本人登录
        try:
            self.driver.find_element_by_id("checkpointSubmitButton").click()
            self.driver.find_element_by_id("checkpointSubmitButton").click()
            self.driver.find_element_by_id("checkpointSubmitButton").click()
        except Exception as e:
            self.logger.info('当前账号未出现异地登录', e)

        try:
            login_name = self.driver.find_element_by_xpath('//*[@id="mbasic_logout_button"]').text
            self.logger.info("登录成功：{}".format(login_name))
            time.sleep(3)
        except Exception as e:
            self.logger.info('登录失败，请确认。error:{}'.format(e))
            status = False

        return status

    def get_graphql_data(self):
        # 解析数据
        graphql_datas = self.get_api_data(match_url='https://www.facebook.com/api/graphql/')
        graphql_data_list = []
        # 将响应字符序列化
        for graphql_data in graphql_datas:
            graphql_response_contents = graphql_data['body'].split('\r\n')
            for graphql_response_content in graphql_response_contents:
                graphql_data_dict = json.loads(graphql_response_content)
                graphql_data_dict.update({'postData': graphql_data['postData']}) if 'postData' in graphql_data else None
                graphql_data_list.append(graphql_data_dict)
        return graphql_data_list

    def get_page_source_person(self, handle_index):
        """
        :return: homepage 网页源代码
        """
        # 切换到该页面
        self.get_handle(handle_index=handle_index)
        # 等待页面加载结束之后 返回页面源码
        try:
            Wait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//h1[@class="gmql0nx0 l94mrbxd p1ri9a11 lzcic4wl"]')))
        except:
            pass
        time.sleep(3)
        return self.driver.page_source

    def get_page_source_like(self, handle_index):
        # 切换到该页面
        self.get_handle(handle_index=handle_index)
        # 等待页面加载结束之后 返回页面源码
        flag = 0
        time.sleep(5)
        try:
            like_button = self.driver.find_element_by_xpath('//span[@class="pcp91wgn"]')
            if like_button:
                like_button.click()
                flag = 1
        except:
            flag = 0
        time.sleep(5)
        return flag, self.driver.page_source

    def get_page_source_share(self, handle_index):
        # 切换到该页面
        self.get_handle(handle_index=handle_index)
        flag = 0
        time.sleep(5)
        try:
            share_button = self.driver.find_elements_by_xpath('//div[@class="gtad4xkn"]')
            if share_button:
                share_button[2].click()
                flag = 1
        except:
            flag = 0
        time.sleep(5)
        return flag, self.driver.page_source


if __name__ == '__main__':
    pass
