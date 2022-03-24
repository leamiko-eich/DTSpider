import re
import pymongo
import requests
from lxml import etree

mongo_db = pymongo.MongoClient()['publishing']

cat = mongo_db['cat']
org = mongo_db['org']
series = mongo_db['series']
cos_data = mongo_db['cos_data']
tables = mongo_db['tables']

headers = {
    'Connection': 'keep-alive',
    'sec-ch-ua': '',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': 'Windows',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}


def save_pdf(url):
    response = requests.get(url, headers=headers, verify=False, stream=True)
    with open("test.epub", 'wb') as f:
        f.write(response.content)
        f.close()
    print('文件保存成功')


def re_pattern_cat(text, title):
    text_list = re.search("\((.*?)\)", text).group(1).replace("'", '').replace(", ", ',').split(',')
    return {
        "title": title,
        "name": text_list[1],
        "cat_id": text_list[0]
    }


def re_pattern_org(text):
    text_list = re.search("\((.*?)\)", text).group(1).replace("'", '').replace(", ", ',').split(',')
    return {
        "org_id": text_list[0],
        "cat_id": text_list[1],
        "org_name": text_list[3]
    }


def re_pattern_series(text):
    text_list = re.search("\((.*?)\)", text).group(1).replace("'", '').replace(", ", ',').split(',')
    return {
        "org_id": text_list[0],
        "cat_id": text_list[1],
        "series_id": text_list[2],
        "series_name": text_list[3]
    }


def get_first_page():
    # 首页记录
    # response = requests.get('https://www.e-publishing.af.mil/Product-Index/', headers=headers, verify=False)
    # response_html = etree.HTML(response.text)
    with open("test2.html", 'r', encoding='utf-8') as f:
        response = f.read()
    response_html = etree.HTML(response)
    forms_str_ids = response_html.xpath("//h4[text()='Forms']/following-sibling::ul[1]")[0].xpath("li/a/@onclick")
    forms_ids = [re_pattern_cat(str(i), "Forms") for i in forms_str_ids]
    cat.insert_many(forms_ids)

    publications_str_ids = response_html.xpath("//h4[text()='Publications']/following-sibling::ul[1]")[0].xpath(
        "li/a/@onclick")
    publications_ids = [re_pattern_cat(str(i), "Publications") for i in publications_str_ids]
    cat.insert_many(publications_ids)

    cat_ids = publications_ids + forms_ids
    # org记录：
    org_datas = []
    for i in cat_ids:
        div = response_html.xpath("//div[@id='cat-%s']" % i['cat_id'])
        orgs = div[0].xpath("div/ul/li/a/@onclick")
        org_datas += [re_pattern_org(str(i)) for i in orgs]
    org.insert_many(org_datas)


def get_series_data():
    org_count = org.count()
    org_datas = org.find().skip(114)
    finish_count = 114
    for org_data in org_datas:
        url = "https://www.e-publishing.af.mil/DesktopModules/MVC/EPUBS/EPUB/GetSeriesView/?orgID={}&catID={}".format(
            org_data['org_id'], org_data['cat_id']
        )
        response = requests.get(url, headers=headers, verify=False)
        response_html = etree.HTML(response.text)
        titles = response_html.xpath("//h4/text()")
        for title in titles:
            series_datas = response_html.xpath("//h4[text()='{}']/following-sibling::ul[1]".format(title))[0].xpath(
                "li/a/@onclick")
            series_datas = [re_pattern_series(str(i)) for i in series_datas]
            series.insert_many(series_datas)
        finish_count += 1
        print("finish count:{},total count:{}".format(finish_count, org_count))


def get_tables_data():
    pub_datas = cat.find({"title": "Publications"})
    total_datas = []
    for i in pub_datas:
        orgs = org.find({'cat_id': i['cat_id']})
        for j in orgs:
            series_datas = series.find({"org_id": j['org_id'], 'cat_id': i['cat_id']})
            for k in series_datas:
                total_datas.append({
                    'cat_id': i['cat_id'],
                    'cat_title': i['title'],
                    'cat_name': i['name'],
                    'org_id': j['org_id'],
                    'org_name': j['org_name'],
                    'series_id': k['series_id'],
                    # 'series_title':k['series_title'],
                    'series_name': k['series_name']
                })
    for d in total_datas:
        if not cos_data.find_one({'cat_id': d['cat_id'], 'org_id': d['org_id'], 'series_id': d['series_id']}):
            cos_data.insert_one(d)


if __name__ == '__main__':
    get_tables_data()
