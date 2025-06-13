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


class CustomsGovHK(object):

    def __init__(self):
        self.list_url = None
        self.column_domain = None
        self.detail_url = None
        self.publish_time = None
        self.title = None
        self.column = None

    def scheduler(self):
        column_list = [
            ("", "海关", "香港海关-新闻公报"),     # >2024 共58页零5条

        ]

        for self.column in column_list:
            self.column_domain = self.column[0]
            self.get_list()



    def get_list(self):

        while True:

            headers = {
                'host': 'www.customs.gov.hk',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-language': 'zh-CN,zh;q=0.9',
                # 'cache-control': 'max-age=0',
                # 'cookie': 'TS01b6fa6b=01885b66e8added7fb2aec3f43ea7a19d0f7f60bdc9bb76227645689b31cfd7e7b380fadbd7dab4ffd7f2cc3720ce65efe2de7f8ba',
                # 'if-modified-since': 'Mon, 07 Apr 2025 04:03:44 GMT',
                'referer': 'https://www.customs.gov.hk/sc/customs-announcement/press-release/index.html',
                'sec-ch-ua': '"Chromium";v="109", "Not_A Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            }

            params = {
                'p': '2',
                'y': '',
                'm': '',
            }

            try:
                self.list_url = 'https://www.customs.gov.hk/sc/customs-announcement/press-release/index.html'
                response = requests.get(
                    url=self.list_url,
                    params=params,
                    # cookies=cookies,
                    proxies=get_proxies(),
                    headers=headers,
                    # allow_redirects=False
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
                response.encoding = "utf-8"
                response_html = etree.HTML(response.text)
                tr_list = response_html.xpath('//table[@class="newsTable"]/tbody/tr')
                logger.info(f'column:{self.column_domain} --- 列表页数量：{len(tr_list)}')
                for tr in tr_list:
                    self.title = tr.xpath('./td[2]/a/text()')[0]
                    self.detail_url = urllib.parse.urljoin(self.list_url, tr.xpath('./td[2]/a/@href')[0])
                    self.publish_time = tr.xpath('./@data-recorddate')[0].replace("/", "-")
                    if self.publish_time < "2024-01-01":
                        logger.info(f'只采集近一年的数据：{self.publish_time}')
                        return

                    find_detail_url = mengniu_data_original_col.find_one({"_id": self.detail_url})
                    if find_detail_url:
                        logger.info(f'已经采集过：{self.publish_time}, {self.detail_url}, {self.title}')
                        continue
                        # return
                    # print(self.publish_time, self.detail_url, self.title)
                    self.get_detail()
                    # return
                return

    def get_detail(self):
        logger.info(f'process {self.publish_time} -- {self.detail_url} -- {self.title}')
        while True:
            headers = {
                'host': 'www.customs.gov.hk',
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
                response.encoding = "utf-8"
                res_text = html.unescape(response.text)
                # print(res_text)

                response_html = etree.HTML(res_text)

                # # 用BeautifulSoup解析HTML
                # soup = BeautifulSoup(res_text, 'html.parser')

                # 将BeautifulSoup对象转换为字符串
                # content_str = str(soup.find(name='div', attrs={'id': 'article'}))

                content_p = response_html.xpath('//div[@class="date"]/following-sibling::p | //div[@class="date"]/following-sibling::div[@class="mB15 f15"]')
                content_str = html.unescape(etree.tostring(content_p[0], encoding="utf-8").decode())
                # print(content_str)

                data = {
                    "_id": self.detail_url,
                    "标题": self.title,
                    "网站发布时间": self.publish_time,
                    "文章地址URL": self.detail_url,
                    "采集源名称": self.column[1],
                    "正文": content_str,
                    "HTML": res_text,
                    "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": 0,
                    "平台形式": "网站",
                    "数据类型": "文章"
                }
                # print(json.dumps(data, ensure_ascii=False))
                if save_articles(data):
                    metrics.emit_counter("详情页采集量", count=1, classify=f"{self.column[2]}")
                return


def test_list():
    headers = {
        'host': 'www.customs.gov.hk',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'zh-CN,zh;q=0.9',
        # 'cache-control': 'max-age=0',
        # 'cookie': 'TS01b6fa6b=01885b66e8added7fb2aec3f43ea7a19d0f7f60bdc9bb76227645689b31cfd7e7b380fadbd7dab4ffd7f2cc3720ce65efe2de7f8ba',
        # 'if-modified-since': 'Mon, 07 Apr 2025 04:03:44 GMT',
        'referer': 'https://www.customs.gov.hk/sc/customs-announcement/press-release/index.html',
        'sec-ch-ua': '"Chromium";v="109", "Not_A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    }

    params = {
        'p': '2',
        'y': '',
        'm': '',
    }

    response = requests.get(
        'https://www.customs.gov.hk/sc/customs-announcement/press-release/index.html',
        params=params,
        # cookies=cookies,
        proxies=get_proxies(),
        headers=headers,
        allow_redirects=False
    )
    response.encoding="utf-8"
    print(response.text)
    print(response.status_code)


def test_detail():
    headers = {
        'host': 'www.customs.gov.hk',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'zh-CN,zh;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    }

    response = requests.get(
        'https://www.customs.gov.hk/sc/customs-announcement/press-release/index_id_4537.html',
        proxies=get_proxies(),
        headers=headers,
    )
    response.encoding="utf-8"
    print(response.text)
    print(response.status_code)


if __name__ == '__main__':
    metrics.init()
    # test_list()
    # test_detail()
    obj = CustomsGovHK()
    obj.scheduler()

    metrics.close()
    MongoClient.close()

