#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/4/29 14:14
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : endbcity.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved
from PatternSpider.settings.spider_names import SpiderNames
from PatternSpider.headers import BaseHeaders


class EnDBCityBase(BaseHeaders):
    def get_headers(self, **kwargs):
        cookies = {
            '__unid': '516fe194-5e8b-77a1-c882-30aa8c02a23f',
            '_pbjs_userid_consent_data': '6683316680106290',
            '_lr_env_src_ats': 'false',
            'pbjs-unifiedid': '%7B%22TDID%22%3A%225aebeece-6aab-4157-9672-2698415833f0%22%2C%22TDID_LOOKUP%22%3A%22TRUE%22%2C%22TDID_CREATED_AT%22%3A%222022-03-09T08%3A44%3A11%22%7D',
            '_cc_id': '87d4adf14dc890fa0b1ff7a88428ee01',
            'unic-consent': 'BPXJ_0APXJ_0A8AAAA',
            'cookieconsent_dismissed': 'yes',
            '__gads': 'ID=d25dc9dd43cbd5f4:T=1650850987:S=ALNI_MbNVHKVlB4y8vUTmsO6DlmdrxJiqQ',
            '_ga': 'GA1.2.237674523.1651047632',
            '_gid': 'GA1.2.1241490886.1651502479',
            'panoramaId_expiry': '1651588898582',
            'sharedid': '%7B%22id%22%3A%2201G06QXG41P8PXKN02BTER9VPV%22%2C%22ts%22%3A1651502499239%7D',
            '__gpi': 'UID=0000050255b1d157:T=1650850987:RT=1651551263:S=ALNI_MZ_3x7C4aV4CUjycvQ_QfOwTZkrAw',
            '__cf_bm': '1xZ5StlTzzal5EPT2qJ8E8Q9b9qdSONPsAoUSiWqiI8-1651551270-0-ASMEO3Sw4Fvu/1NuOhcfkrpTFdCdrZDye75GRKDFER1c1mCY4rQ8+Ei5lNlHBa7iH+Inttzh8dZkTFKHKnL+7qHBG4lS2fiKPezFXgJztRETYAmggf/EL7RgrFjKxl3q4Q==',
            '_lr_retry_request': 'true',
            'pbjs-id5id': '%7B%22created_at%22%3A%222022-04-09T08%3A44%3A11Z%22%2C%22id5_consent%22%3Atrue%2C%22original_uid%22%3A%22ID5*xP_dC73awKgR1RUQzplNdfqg5GmKaE_bg1TySSk-sxYRXHLvLVedExNG7Yq1hTm6%22%2C%22universal_uid%22%3A%22ID5*qLl1FSlZfXuOxcU0rBGYyy19cwsz-GytRP6F1BkcqGkRXLRrzIKYb3S0ik7rsbis%22%2C%22signature%22%3A%22ID5_AZhzNGJHJpCWosdMENPLO3FbGzMe8M7gDxw1Qw8rf_koifhtRpn_wL9CwdYB5u703pNoEi4hMFNO1ZP3hBJ71Pc%22%2C%22link_type%22%3A2%2C%22cascade_needed%22%3Afalse%2C%22privacy%22%3A%7B%22jurisdiction%22%3A%22other%22%2C%22id5_consent%22%3Atrue%7D%7D',
            'pbjs-id5id_last': 'Tue%2C%2003%20May%202022%2004%3A14%3A38%20GMT',
            '_gat_gtag_UA_122129_19': '1',
            'cto_bidid': 'fxaGj19zeU02MlJCOU9mVGJOY21HbGdCZUxQZXhWQ0RDWXdKYW1xb1JETDRKbkFSemMlMkJ6QnhxJTJGUDRRQnhXVksydkZWejNKRDhkbW1WR29nTW5Tc3pkSkZUQ3R6a0JyTU8zJTJGY0QwMWtrQXF5JTJCZTIwJTNE',
            'cto_bundle': 'Ao7oyl93TVpOem43SEF6SmlFUGtEdGlqOUNmVlozN3B5TWhkd2hKeVBiYTBMR0kyOXZJVldiJTJCT2pGT2MwcGI0N1Rjc2xveWFnQSUyRnFZZ1NNc3FsUlhkalFla0VpU0NnRzE5VElnWSUyRlUxaHA5ZUVqZkZKaHJNNEdjT2Z5cnNGQnhxRkdpdlhnS2RFbGtNUFVmYTdWSVNodDNGSXclM0QlM0Q',
        }
        return {
            'authority': 'en.db-city.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            # Requests sorts cookies= alphabetically
            # 'cookie': '__unid=516fe194-5e8b-77a1-c882-30aa8c02a23f; _pbjs_userid_consent_data=6683316680106290; _lr_env_src_ats=false; pbjs-unifiedid=%7B%22TDID%22%3A%225aebeece-6aab-4157-9672-2698415833f0%22%2C%22TDID_LOOKUP%22%3A%22TRUE%22%2C%22TDID_CREATED_AT%22%3A%222022-03-09T08%3A44%3A11%22%7D; _cc_id=87d4adf14dc890fa0b1ff7a88428ee01; unic-consent=BPXJ_0APXJ_0A8AAAA; cookieconsent_dismissed=yes; __gads=ID=d25dc9dd43cbd5f4:T=1650850987:S=ALNI_MbNVHKVlB4y8vUTmsO6DlmdrxJiqQ; _ga=GA1.2.237674523.1651047632; _gid=GA1.2.1241490886.1651502479; panoramaId_expiry=1651588898582; sharedid=%7B%22id%22%3A%2201G06QXG41P8PXKN02BTER9VPV%22%2C%22ts%22%3A1651502499239%7D; __gpi=UID=0000050255b1d157:T=1650850987:RT=1651551263:S=ALNI_MZ_3x7C4aV4CUjycvQ_QfOwTZkrAw; __cf_bm=1xZ5StlTzzal5EPT2qJ8E8Q9b9qdSONPsAoUSiWqiI8-1651551270-0-ASMEO3Sw4Fvu/1NuOhcfkrpTFdCdrZDye75GRKDFER1c1mCY4rQ8+Ei5lNlHBa7iH+Inttzh8dZkTFKHKnL+7qHBG4lS2fiKPezFXgJztRETYAmggf/EL7RgrFjKxl3q4Q==; _lr_retry_request=true; pbjs-id5id=%7B%22created_at%22%3A%222022-04-09T08%3A44%3A11Z%22%2C%22id5_consent%22%3Atrue%2C%22original_uid%22%3A%22ID5*xP_dC73awKgR1RUQzplNdfqg5GmKaE_bg1TySSk-sxYRXHLvLVedExNG7Yq1hTm6%22%2C%22universal_uid%22%3A%22ID5*qLl1FSlZfXuOxcU0rBGYyy19cwsz-GytRP6F1BkcqGkRXLRrzIKYb3S0ik7rsbis%22%2C%22signature%22%3A%22ID5_AZhzNGJHJpCWosdMENPLO3FbGzMe8M7gDxw1Qw8rf_koifhtRpn_wL9CwdYB5u703pNoEi4hMFNO1ZP3hBJ71Pc%22%2C%22link_type%22%3A2%2C%22cascade_needed%22%3Afalse%2C%22privacy%22%3A%7B%22jurisdiction%22%3A%22other%22%2C%22id5_consent%22%3Atrue%7D%7D; pbjs-id5id_last=Tue%2C%2003%20May%202022%2004%3A14%3A38%20GMT; _gat_gtag_UA_122129_19=1; cto_bidid=fxaGj19zeU02MlJCOU9mVGJOY21HbGdCZUxQZXhWQ0RDWXdKYW1xb1JETDRKbkFSemMlMkJ6QnhxJTJGUDRRQnhXVksydkZWejNKRDhkbW1WR29nTW5Tc3pkSkZUQ3R6a0JyTU8zJTJGY0QwMWtrQXF5JTJCZTIwJTNE; cto_bundle=Ao7oyl93TVpOem43SEF6SmlFUGtEdGlqOUNmVlozN3B5TWhkd2hKeVBiYTBMR0kyOXZJVldiJTJCT2pGT2MwcGI0N1Rjc2xveWFnQSUyRnFZZ1NNc3FsUlhkalFla0VpU0NnRzE5VElnWSUyRlUxaHA5ZUVqZkZKaHJNNEdjT2Z5cnNGQnhxRkdpdlhnS2RFbGtNUFVmYTdWSVNodDNGSXclM0QlM0Q',
            'pragma': 'no-cache',
            'referer': 'https://en.db-city.com/Cameroon',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
            'cookies': cookies
        }


class EnDBCityListAndDetail(EnDBCityBase):
    Uri = 'https://en.db-city.com'
    name = SpiderNames.endbcity

    def get_url(self, **kwargs):
        path_url = kwargs.get("path_url", '')
        if not path_url:
            return self.Uri
        return self.Uri + path_url
