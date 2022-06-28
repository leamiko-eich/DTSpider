#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/4/29 14:19
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : endbcity.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
import hashlib
import json

from PatternSpider.scrapy_redis.spiders import RedisSpider
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.tasks import TaskManage
from lxml import etree


class EnDBCitySpider(RedisSpider):
    name = SpiderNames.endbcity
    redis_key = "start_urls:" + name
    task_manage = TaskManage()
    custom_settings = {
        'CONCURRENT_REQUESTS': 16,
        'DOWNLOADER_MIDDLEWARES': {
            'PatternSpider.middlewares.middlewares.RandomUserAgentMiddleware': 543,
        },
        "EXTENSIONS": {
            # 'PatternSpider.extensions.RedisSpiderSmartIdleClosedExensions': 100,
        },
        "ITEM_PIPELINES": {
            # 'PatternSpider.pipelines.DownloadImagesPipeline': 1,
            'PatternSpider.pipelines.MongoPipeline': 100,
            # 'PatternSpider.pipelines.Neo4jPipeline': 500,
        }
    }

    contents_ids = [
        "block_sub",  # 下级城市
        "block_dir",  # 城市目录
        "block_bigcity",  # 主要城市
        "block_info",  # 基本信息
        "block_chief",  # 国家元首
        "block_religion",  # 宗教
        "block_stat",  # 一些数据
        "block_chart",  # 图表数据
        "block_covid19",  # 疫情信息
        "block_natural",  # 自然资源
        "block_agriculture",  # 农业
        "block_border",  # 边境
        "block_map",  # 地图
        "block_climate",  # 气候
        "block_weather",  # 天气
        "block_elec",  # 电力
        "block_airport",  # 机场
        "block_hotel",  # 酒店
        "block_jo",  # 奥运会
        "block_page",  # 链接
        "block_adm",  # 管理者
        "block_demo",  # 人口统计
        "block_geo",  # 地理位置
        "block_dist1",  # 距离
        "block_dist2",  # 距离
        "block_hour",  # 时区
        "block_sun",  # 日出日落
        "block_around",  # 附近周边
    ]

    def replace_str(self, s):
        return s.replace("\n", '').replace("\xa0", "").replace('.', '_').replace(' ', '')

    def parse(self, response):
        task = json.loads(response.meta['task'])
        print(task)
        response_html = etree.HTML(response.text)
        if not task['raw'].get('path_url', ''):
            countries = response_html.xpath('//*[@id="left"]//li/div/a')
            for country in countries:
                path = country.xpath("@href")
                title = country.xpath("@title")
                self.task_manage.write_task_from_spider_name(
                    self.name,
                    path_url=path[0] if path else "",
                    name=title[0] if title else ""
                )
        else:
            request_url = response.request.url
            request_url_md5 = hashlib.sha256(response.request.url.encode('utf-8')).hexdigest()
            with open("D:/lff/spider_result/endbcity_htmls/" + request_url_md5, 'w', encoding='utf-8') as f:
                f.write(response.text)
            item = {
                "request_url": request_url,
                "request_url_md5": request_url_md5,
                "path_url": task['raw'].get('path_url', ''),
                "name": task['raw'].get('name', ''),
                'block_dir': self.parse_block_dir(response_html),
                'block_sub': self.parse_block_sub(response_html)
            }
            print(item)
            yield item
            if item['block_sub']:
                for i in item['block_sub']:
                    self.task_manage.write_task_from_spider_name(
                        self.name,
                        path_url=i['path_url'],
                        name=i['name']
                    )
            elif item['block_dir']:
                for i in item['block_dir']:
                    self.task_manage.write_task_from_spider_name(
                        self.name,
                        path_url=i['path_url'],
                        name=i['name']
                    )
        # 删除任务
        self.task_manage.del_item("mirror:" + self.name, response.meta['task'])

    def parse_block_dir(self, response_html):
        div = response_html.xpath("//div[@id='block_dir']/div[@class='h2content']")
        if not div:
            return []
        div = div[0]
        values = []
        a_s = div.xpath("table[2]//tr/td/a")
        for a in a_s:
            try:
                values.append({"name": a.text, "path_url": a.xpath('@href')[0]})
            except Exception as e:
                print(a, str(e))
                continue
        return values

    def parse_block_sub(self, response_html):
        div = response_html.xpath("//div[@id='block_sub']/div[@class='h2content']")
        if not div:
            return []
        div = div[0]
        values = []
        a_s = div.xpath('table//a')
        for a in a_s:
            try:
                values.append({"name": a.text, "path_url": a.xpath('@href')[0]})
            except Exception as e:
                print(a, str(e))
                continue
        return values

    def parse_contents(self, response_html, div_id):
        div = response_html.xpath("//div[@id='{}']/div[@class='h2content']".format(div_id))
        if not div:
            return {div_id: []}
        div = div[0]
        values = []
        if div_id in ["block_sub", "block_bigcity"]:
            a_s = div.xpath('table//a')
            for a in a_s:
                values.append({
                    "name": "city",
                    "value": a.xpath('@title')[0],
                    "path_url": a.xpath('@href')[0]
                })
        elif div_id in ["block_info", "block_chief", "block_stat", "block_covid19", "block_elec", "block_adm",
                        "block_demo", "block_geo"]:
            trs = div.xpath('table//tr')
            for tr in trs:
                data = {}
                name1 = tr.xpath('th//text()')
                name2 = tr.xpath('th//a//text()')
                data["name"] = name2[0] if name2 else name1[0]
                data["name_href"] = tr.xpath('th/a/@href')[0] if name2 else ""

                td_list = []
                td1 = tr.xpath('td/font/font/text()')
                for i in td1:
                    td_list.append({'value': i, 'value_href': ''})
                td2 = tr.xpath('td/a')
                for i in td2:
                    try:
                        td_list.append({'value': i.xpath('@title')[0], 'value_href': i.xpath('@href')[0]})
                    except:
                        print(123)

                data['values'] = td_list
                source = tr.xpath('td/audio/source/@src')
                data['source'] = source[0] if source else ""
                values.append(data)

        elif div_id in ["block_religion", "block_climate"]:
            lis = div.xpath('ol/li')
            for li in lis:
                name1 = li.xpath('strong//text()')
                name2 = li.xpath('font//text()')
                name = name1[0] if name1 else name2[0]
                value = li.xpath('span//text()')[0]
                values.append({"name": name, "value": value})
        elif div_id in ["block_natural", "block_agriculture", "block_airport"]:
            lis = div.xpath('ol/li')
            for li in lis:
                values.append(li.xpath('font/font').text)
            tds = div.xpath('div//td')
            for td in tds:
                values.append(td.xpath('font/font').text)

        elif div_id in ["block_border"]:
            lis = div.xpath('ol/li')
            for li in lis:
                name = li.xpath('a/@title')[0]
                name_path_url = li.xpath('a/@href')[0]
                value = li.xpath('span/font/font').text
                values.append({"name": name, "name_path_url": name_path_url, "value": value})

        elif div_id in ["block_hotel"]:
            trs = div.xpath('table//tr')
            for tr in trs[:-1]:
                photo = tr.xpath('td[1]/img/@src')[0]
                name = tr.xpath('td[2]/strong//text()')[0]
                place = tr.xpath('td[2]/em//text()')[0]
                desc = ",".join(tr.xpath('td[2]/font//text()'))
                price = ",".join(tr.xpath('td[3]/font//text()'))
                values.append({"name": name, "photo": photo, "place": place, "desc": desc, "price": price})

        elif div_id in ["block_dist1", "block_dist2", "block_around"]:
            tds = div.xpath('table//td')
            for td in tds:
                values.append(dict(
                    name=td.xpath('a/@title')[0],
                    name_path_url=td.xpath('a/@href')[0],
                    value=td.xpath('em//text()')[0]
                ))

        return {div_id: values}
