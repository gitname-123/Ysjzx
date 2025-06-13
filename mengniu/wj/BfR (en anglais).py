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


class BfRNew(object):

    def __init__(self):
        self.list_url = None
        self.column_domain = None
        self.page = None
        self.detail_url = None
        self.publish_time = None
        self.title = None

    def scheduler(self):
        while True:

            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
                'host': 'www.bfr.bund.de'
            }
            try:
                # time.sleep(2)
                self.list_url = f'https://www.bfr.bund.de/en/new.html'
                response = requests.get(
                    url=self.list_url,
                    proxies=get_proxies(),
                    headers=headers,
                    timeout=10,
                    verify=False
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
                result_list = response_html.xpath('//div[@class="resultList"]/div')
                logger.info(f'列表页数量：{len(result_list)}')
                for result_div in result_list:
                    self.title = result_div.xpath('./h4/a/text()')[0]
                    self.detail_url = urllib.parse.urljoin(self.list_url, result_div.xpath('./h4/a/@href')[0])
                    publish_time_text = result_div.xpath('./span[@class="date"]/text()')[0]
                    self.publish_time = datetime.strptime(publish_time_text, '%d.%m.%Y').strftime('%Y-%m-%d')
                    find_detail_url = mengniu_data_original_col.find_one({"_id": self.detail_url})
                    if find_detail_url:
                        logger.info(f'已经采集过：{self.publish_time}, {self.detail_url}, {self.title}')
                        continue
                    class_type = result_div.xpath('./@class')[0]
                    if class_type == 'resultItem htmlDoc':
                        self.get_detail()
                    elif class_type == 'resultItem pdfDoc':
                        data = {
                            "_id": self.detail_url,
                            "标题": self.title,
                            "网站发布时间": self.publish_time,
                            "文章地址URL": self.detail_url,
                            "采集源名称": "BfR (en anglais)",
                            "正文": "",
                            "HTML": "",
                            "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "status": 0,
                            "平台形式": "网站",
                            "数据类型": "文章",
                            "附件": json.dumps([{"fileName": self.detail_url.split("/")[-1], "fileLink": self.detail_url}])
                        }
                        # print(data)
                        if save_articles(data):
                            metrics.emit_counter("详情页采集量", count=1, classify="BfR (en anglais)")
                    else:
                        logger.error(f'出现了没有覆盖到的页面：{self.title} --- {self.detail_url}')
                        continue
                return

    def get_detail(self):
        logger.info(f'process {self.publish_time} -- {self.title} -- {self.detail_url}')
        while True:
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Referer': self.list_url,
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
                'sec-ch-ua': '"Chromium";v="109", "Not_A Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
            }
            try:
                time.sleep(2)
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
                # response.encoding = "utf-8"
                # res_text = html.unescape(response.text)
                # print(response.text)

                # response_html = etree.HTML(res_text)

                # 用BeautifulSoup解析HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                content_div = soup.find(name='div', attrs={'id': 'main'})
                # print(str(content_div))

                h2 = content_div.find('h2')
                h2.decompose()
                h3 = content_div.find('h3')
                h3.decompose()
                div_service = content_div.find('div', attrs={'class': 'serviceArea'})
                if div_service:
                    div_service.decompose()
                pageTops = content_div.find_all('p', attrs={'class': 'pageTop'})
                for pageTop in pageTops:
                    pageTop.decompose()
                span_hits = content_div.find_all('span', attrs={'class': 'hits'})
                for span_hit in span_hits:
                    span_hit.decompose()
                div_stay_Opens = content_div.find_all('div', attrs={'class': 'stay_Open'})
                for div_stay_Open in div_stay_Opens:
                    div_stay_Open.decompose()
                # content_div = response_html.xpath('//div[@id="article"]')
                # content_str = html.unescape(etree.tostring(content_div[0], encoding="utf-8").decode())
                # print(content_str)
                # print(W_文章来源)
                # 将BeautifulSoup对象转换为字符串

                content_str = str(content_div)

                data = {
                    "_id": self.detail_url,
                    "标题": self.title,
                    "网站发布时间": self.publish_time,
                    "文章地址URL": self.detail_url,
                    "采集源名称": "BfR (en anglais)",
                    "正文": content_str,
                    "HTML": response.text,
                    "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": 0,
                    "平台形式": "网站",
                    "数据类型": "文章"
                }
                if save_articles(data):
                    metrics.emit_counter("详情页采集量", count=1, classify="BfR (en anglais)")
                    # pass
                return


if __name__ == '__main__':
    metrics.init()
    obj = BfRNew()
    obj.scheduler()
    metrics.close()
    MongoClient.close()
