# coding=utf8
import html
import json
import re
import urllib
import requests
import time
import warnings
from bs4 import BeautifulSoup
warnings.filterwarnings("ignore")
from datetime import datetime
from loguru import logger
from lxml import etree
import sys
sys.path.append('../')
from tools.get_proxy import get_proxies
from tools.save import save_articles
from tools.settings import mengniu_data_original_col, MongoClient
import subprocess
from functools import partial
subprocess.Popen = partial(subprocess.Popen, encoding='utf-8')
from feapder.utils import metrics


class CBP_Gov(object):

    def __init__(self):
        self.page = 0
        self.list_url = 'https://www.cbp.gov/views/ajax'
        self.column_domain = None
        self.detail_url = None
        self.publish_time = None
        self.title = None
        self.column = None


    def get_list(self):

        # while self.page < 25:
        while self.page < 5:
            headers = {
                'host': 'www.cbp.gov',
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'accept-language': 'zh-CN,zh;q=0.9',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
                'x-requested-with': 'XMLHttpRequest',
            }

            params = {
                '_wrapper_format': 'drupal_ajax',
                'view_name': 'newsroom',
                'view_display_id': 'block_17',
                'view_args': 'all',
                'view_path': '/node/428686',
                'view_base_path': 'newsroom/media-releases',
                # 'view_dom_id': '66e7a903aad8f2b8a296b2fe2f180f50caadfa568ef240162010ace4d2c1db36',
                'pager_element': '0',
                'page': f'{self.page}',
                '_drupal_ajax': '1',
                'ajax_page_state[theme]': 'cbpd8_gov_theme',
                'ajax_page_state[theme_token]': '',
                'ajax_page_state[libraries]': 'eJxtUEFywyAM_BC2rv0NI0DGNDIwCgwCd2Xl8ckjRtchHalYbVrqFaqWjachJgwegeyegrcoICnSAVZGcbrDiakEb9xU9Zk96ggV9Ous600LQsEbDlBl3Km9jz8m0Tz7Tg9SdQ_TKnsiFmopGa1NxIUV4duNUUqwUnbKMIu0UFHr0Cgw4mgJ1FtmSCmsiCHKyk3i17l4uRxAG21KgwZ3AlTUjj3eoulmwmGuTUj4lz6QrevCt_Mc9gT_koqLgwXHPxcTdrgpVcZC_qCeZaH6C8zrjGvhoPM5FQuIdYjQqBYQ92H4zJRskulpbtdZSJ3pHfXxgwoi812AFOKEgewbnnCwLqruu2t2oJ_5NiVqJxxmoY8-5HwOdBG41e74lVgwegiSW5nUxS46Jkd6InIG7QnemNuOrOVMO_TnBgweyUE8d5',
            }

            try:
                time.sleep(5)
                response = requests.get(
                    url=self.list_url,
                    params=params,
                    # cookies=cookies,
                    headers=headers,
                    proxies=get_proxies(),
                    verify=False,
                    timeout=10

                )
            except Exception as e:
                logger.error(f'request list url error:{e}')
                time.sleep(2)
                continue
            else:
                if response.status_code != 200:
                    logger.error(f' get list response status code != 200 :{response.status_code} --- {response.text}')
                    time.sleep(2)
                    continue
                # print(response.text)
                res_list = json.loads(response.text)
                res_html_text = ""
                for res_dict in res_list:
                    method = res_dict.get('method', "")
                    if method == "replaceWith":
                        res_html_text = res_dict["data"]
                        break
                if not res_html_text:
                    logger.error(f'没获取到data:{response.text}')
                    return
                response_html = etree.HTML(res_html_text)
                li_list = response_html.xpath('//div[@class="item-list"]/ul/li')
                logger.info(f'page:{self.page} --- 列表页数量：{len(li_list)}')
                for li in li_list:
                    self.title = li.xpath('.//div[@class="usa-collection__heading sizeH3-adj"]/a/text()')[0]
                    self.detail_url = urllib.parse.urljoin(self.list_url, li.xpath('.//div[@class="usa-collection__heading sizeH3-adj"]/a/@href')[0])
                    logger.info(f'list data: {self.detail_url} -- {self.title}')
                    # if self.publish_time < "2024-01-01":
                    #     logger.info(f'只采集近一年的数据：{self.publish_time}')
                    #     return

                    find_detail_url = mengniu_data_original_col.find_one({"_id": self.detail_url})
                    if find_detail_url:
                        logger.info(f'已经采集过：{self.publish_time}, {self.detail_url}, {self.title}')
                        continue
                        # return
                    self.get_detail()
                    # return
                self.page += 1
                # return

    def get_detail(self):
        logger.info(f'process detail: {self.detail_url} -- {self.title}')
        while True:
            headers = {
                'host': 'www.cbp.gov',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-language': 'zh-CN,zh;q=0.9',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            }

            try:
                time.sleep(1)
                response = requests.get(
                    url=self.detail_url,
                    proxies=get_proxies(),
                    headers=headers,
                    timeout=10,
                    verify=False
                )
            except Exception as e:
                logger.error(f'request detail url error:{e}')
                time.sleep(2)
                continue
            else:
                if response.status_code != 200:
                    logger.error(f'response get detail status code != 200 :{response.status_code} --- {response.text}')
                    time.sleep(2)
                    continue
                res_text = response.text
                response_html = etree.HTML(res_text)

                publish_text = response_html.xpath('//div[@id="node-newsroom-full-group-date-location"]//div[@class="field__item"]/text()')[0]
                self.publish_time = datetime.strptime(re.findall('(\d{2}/\d{2}/\d{4})', publish_text)[0], '%m/%d/%Y').strftime('%Y-%m-%d')
                # # 用BeautifulSoup解析HTML
                soup = BeautifulSoup(res_text, 'html.parser')

                # 将BeautifulSoup对象转换为字符串
                content_div = soup.find(name='div', attrs={'id': 'block-cbpd8-gov-theme-cbp-gov-theme-system-main'})

                div_date = content_div.find('div', attrs={'id': 'node-newsroom-full-group-date-location'})
                if div_date:
                    div_date.decompose()

                content_str = str(content_div)

                data = {
                    "_id": self.detail_url,
                    "标题": self.title,
                    "网站发布时间": self.publish_time,
                    "文章地址URL": self.detail_url,
                    "采集源名称": "海关",
                    "正文": content_str,
                    "HTML": res_text,
                    "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": 0,
                    "平台形式": "网站",
                    "数据类型": "文章"
                }
                # print(json.dumps(data, ensure_ascii=False))
                if save_articles(data):
                    metrics.emit_counter("详情页采集量", count=1, classify="海关-美国海关")
                return


def test_list():
    headers = {
        'host': 'www.cbp.gov',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        # 'cookie': '__utmzz=utmcsr=(direct)|utmcmd=(none)|utmccn=(not set); _ga=GA1.1.840045779.1742262844; nmstat=5bd5ef88-162b-ab2e-283a-49f9c40bb1fb; wcmSurveyBlockSurvey=true; ak_bmsc=9788792B58A6A2EE6356C86BD28C648F~000000000000000000000000000000~YAAQRZ42Fzw4/wyWAQAAZiDoNhvvdh811RdLNyxaOKXzhoOIReoNGcb8B8A5gKIpcqR/Z9TjILn66942l/uTTRxX0MEVOeYvtfhquzjI0HFpJMp8Mf5o/BV2kscSn6N77SDnTRYEq/PqBMPTVwm0G5JzpGUSLMdaySPU9gJT52AvAn6mo7fmIumseXwZxx1Vm3LpB+EIR2rqD4YebZQI6nxADAfsDDzSd/TW5LkdOQnBODB9nXa4+xwcrmhK+bYDypspLWz24rPSe6oIyYiN1XGliomkz8oHKnGxgZ/Ec4f0oFtrgvMHUFvw3ldH+Jnch7V++haT5lQefQ2DBIjUYtgs1Bag6LGuohZ6hT+6lY9b9o1/3KtjsNmx491YQ58ch7RKga9QLA==; __utmzzses=1; bm_sv=A083EA8AE75F6C9AAC698067DBB67B79~YAAQRZ42F/l9Bg2WAQAAjrIqNxtWJ2IvV0/79Yv92B1N0bYW0+nURdb8hAvZoFWbmQfbjSwgXomhM2Tw99fDEZdi25F/7BfizoGmoehBsO+oTUinAJ87OWjy15wfnT/L7K1EeFapVZbEiCGE+DBLaQlq+/W5ZkCvgPCuT7ALMWqlhTXCKHtVs/m8fk0qF8egLBlhNcJFpgN9KDCXbzK6eAZQSukKXKMlk/IcLUOD0JmKgDIHpICuc/BrKduRJQ==~1; _ga_CSLL4ZEK4L=GS1.1.1744682163.6.1.1744682269.0.0.0; _ga_V6DQTJJ2XE=GS1.1.1744682163.6.1.1744682269.0.0.0; _ga_WYBYBJKKZ6=GS1.1.1744682163.6.1.1744682269.0.0.0',
        'referer': 'https://www.cbp.gov/newsroom/media-releases/all',
        'sec-ch-ua': '"Chromium";v="109", "Not_A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    params = {
        '_wrapper_format': 'drupal_ajax',
        'view_name': 'newsroom',
        'view_display_id': 'block_17',
        'view_args': 'all',
        'view_path': '/node/428686',
        'view_base_path': 'newsroom/media-releases',
        # 'view_dom_id': '66e7a903aad8f2b8a296b2fe2f180f50caadfa568ef240162010ace4d2c1db36',
        'pager_element': '0',
        'page': '6',
        '_drupal_ajax': '1',
        'ajax_page_state[theme]': 'cbpd8_gov_theme',
        'ajax_page_state[theme_token]': '',
        'ajax_page_state[libraries]': 'eJxtUEFywyAM_BC2rv0NI0DGNDIwCgwCd2Xl8ckjRtchHalYbVrqFaqWjachJgwegeyegrcoICnSAVZGcbrDiakEb9xU9Zk96ggV9Ous600LQsEbDlBl3Km9jz8m0Tz7Tg9SdQ_TKnsiFmopGa1NxIUV4duNUUqwUnbKMIu0UFHr0Cgw4mgJ1FtmSCmsiCHKyk3i17l4uRxAG21KgwZ3AlTUjj3eoulmwmGuTUj4lz6QrevCt_Mc9gT_koqLgwXHPxcTdrgpVcZC_qCeZaH6C8zrjGvhoPM5FQuIdYjQqBYQ92H4zJRskulpbtdZSJ3pHfXxgwoi812AFOKEgewbnnCwLqruu2t2oJ_5NiVqJxxmoY8-5HwOdBG41e74lVgwegiSW5nUxS46Jkd6InIG7QnemNuOrOVMO_TnBgweyUE8d5',
    }

    response = requests.get(
        url='https://www.cbp.gov/views/ajax',
        params=params,
        # cookies=cookies,
        headers=headers,
        proxies=get_proxies(),
        # verify=False
    )
    response.encoding="utf-8"
    print(response.text)
    print(response.status_code)


def test_detail():
    headers = {
        'host': 'www.cbp.gov',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'zh-CN,zh;q=0.9',
        # 'cache-control': 'max-age=0',
        # 'cookie': '__utmzz=utmcsr=(direct)|utmcmd=(none)|utmccn=(not set); _ga=GA1.1.840045779.1742262844; nmstat=5bd5ef88-162b-ab2e-283a-49f9c40bb1fb; wcmSurveyBlockSurvey=true; ak_bmsc=9788792B58A6A2EE6356C86BD28C648F~000000000000000000000000000000~YAAQRZ42Fzw4/wyWAQAAZiDoNhvvdh811RdLNyxaOKXzhoOIReoNGcb8B8A5gKIpcqR/Z9TjILn66942l/uTTRxX0MEVOeYvtfhquzjI0HFpJMp8Mf5o/BV2kscSn6N77SDnTRYEq/PqBMPTVwm0G5JzpGUSLMdaySPU9gJT52AvAn6mo7fmIumseXwZxx1Vm3LpB+EIR2rqD4YebZQI6nxADAfsDDzSd/TW5LkdOQnBODB9nXa4+xwcrmhK+bYDypspLWz24rPSe6oIyYiN1XGliomkz8oHKnGxgZ/Ec4f0oFtrgvMHUFvw3ldH+Jnch7V++haT5lQefQ2DBIjUYtgs1Bag6LGuohZ6hT+6lY9b9o1/3KtjsNmx491YQ58ch7RKga9QLA==; __utmzzses=1; bm_sv=A083EA8AE75F6C9AAC698067DBB67B79~YAAQESYHYFNVDxCWAQAAN/NGNxvTFkYXOsVEIgFieV0YPoe/m/D2eJ3H0+XO4iG+4E6hYuu6bvRlx0L4IHSdJ2lhy0X2vIaozzqMXd4ChGKdZ0OTS3Hm2Xs2Phk9hSCKyTJRj5LePHlYBvLGNeQsMcBGZ51b978gIMOGjjkRcboPH9Kd4mFGSOQP3snzn1Js8cW91cn0us5L4zoNCa7z7Yuk4A5MFaiot+usIN2rMO9p/gktkugx/+D4McAOQA==~1; _ga_CSLL4ZEK4L=GS1.1.1744684107.7.0.1744684259.0.0.0; _ga_V6DQTJJ2XE=GS1.1.1744684107.7.0.1744684259.0.0.0; _ga_WYBYBJKKZ6=GS1.1.1744684107.7.0.1744684259.0.0.0',
        # 'if-modified-since': 'Tue, 15 Apr 2025 02:19:53 GMT',
        # 'if-none-match': '"1744683593"',
        # 'sec-ch-ua': '"Chromium";v="109", "Not_A Brand";v="99"',
        # 'sec-ch-ua-mobile': '?0',
        # 'sec-ch-ua-platform': '"Windows"',
        # 'sec-fetch-dest': 'document',
        # 'sec-fetch-mode': 'navigate',
        # 'sec-fetch-site': 'none',
        # 'sec-fetch-user': '?1',
        # 'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    }

    response = requests.get(
        'https://www.cbp.gov/newsroom/local-media-release/us-border-patrol-arrests-registered-sex-offender-near-sasabe-arizona',
        proxies=get_proxies(),
        headers=headers,
    )
    response.encoding="utf-8"
    print(response.text)
    print(response.status_code)


def test():
    data = {
        "_id": "https://www.cbp.gov/document/publications/importing-united-states",
        "标题": "Importing into the United States",
        "网站发布时间": "2014-03-18",
        "文章地址URL": "https://www.cbp.gov/document/publications/importing-united-states",
        "采集源名称": "",
        "正文": "",
        "HTML": "",
        "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": 0,
        "平台形式": "网站",
        "数据类型": "文章",
        "附件": json.dumps([{"fileName": "Importing into the U.S.pdf", "fileLink": "https://www.cbp.gov/sites/default/files/documents/Importing%20into%20the%20U.S.pdf"}], ensure_ascii=False)
    }
    # print(json.dumps(data, ensure_ascii=False))
    save_articles(data)



if __name__ == '__main__':

    # # # test()
    # test_list()
    # test_detail()

    metrics.init()

    obj = CBP_Gov()
    obj.get_list()

    metrics.close()

    MongoClient.close()
