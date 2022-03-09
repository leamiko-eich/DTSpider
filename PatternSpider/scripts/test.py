import urllib

import requests

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

response = requests.get('https://armypubs.army.mil/epubs/DR_pubs/DR_a/ARN18314-ADP_6-0-000-EBOOK-3.epub', headers=headers,verify=False,stream=True)
with open ("test.pdf",'wb') as f:
    f.write(response.content)
    f.close()
print('文件保存成功')
print(response)

