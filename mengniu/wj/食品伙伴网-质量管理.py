import html
import json
import re
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
from tools.settings import mengniu_data_original_col, today, MongoClient
from tools.save import save_articles
import subprocess
from functools import partial
subprocess.Popen = partial(subprocess.Popen, encoding='utf-8')
from feapder.utils import metrics



# 通过检索查询 质量管理
class foodmateZhiLiang(object):
    def __init__(self):
        self.column_domain = None
        self.page = None
        self.detail_url = None
        self.publish_time = None
        self.title = None
        self.column = None

    def scheduler(self):

        self.page = 1

        while True:
            logger.info(f'process list page：食品伙伴网-质量管理 -- {self.page}')
            # if self.page > 10:
            #     logger.success(f'{self.column[1]} 处理完毕')
            #     return

            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Connection': 'keep-alive',
                # 'Cookie': 'hasshown=1; bc08_f0d8_saltkey=pGq0UTXQ; bc08_f0d8_lastvisit=1748217220; bc08_f0d8_lastact=1748220820%09api.php%09js; Hm_lvt_2aeaa32e7cee3cfa6e2848083235da9f=1748220824; HMACCOUNT=5E3DCAD3DF824D60; __51cke__=; __51uvsct__undefined=1; __51vcke__undefined=65fc7410-df77-5b44-a12a-a88fdbc76fbd; __51vuft__undefined=1748220824335; __tins__1638669=%7B%22sid%22%3A%201748220824196%2C%20%22vd%22%3A%202%2C%20%22expires%22%3A%201748222632387%7D; __51laig__=2; __vtins__undefined=%7B%22sid%22%3A%20%226365006f-fefc-5840-b427-08094457d062%22%2C%20%22vd%22%3A%202%2C%20%22stt%22%3A%208159%2C%20%22dr%22%3A%208159%2C%20%22expires%22%3A%201748222632492%2C%20%22ct%22%3A%201748220832492%7D; __gads=ID=7c16771d11225376:T=1748220833:RT=1748220833:S=ALNI_MaMnJRSITjZOmfyT8qLrDdTPvZ6rw; __gpi=UID=000010e7731a3f2e:T=1748220833:RT=1748220833:S=ALNI_MYwmepmdyPr8ogHKYg_zXexosEyVg; __eoi=ID=828610b544c3e595:T=1748220833:RT=1748220833:S=AA-AfjbfhkmyzW0uwpyNSwRH3bC9; u_last_search=1748220861; Hm_lpvt_2aeaa32e7cee3cfa6e2848083235da9f=1748220865',
                # 'Referer': 'https://www.foodmate.net/zhiliang/search.php?kw=%BD%E2%B6%C1&x=41&y=13',
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
                params = {
                    'kw': '',
                    'fields': '0',
                    'catid': '0',
                    'order': '0',
                    'x': '79',
                    'y': '11',
                    'page': f'{self.page}',
                }
                # time.sleep(2)
                response = requests.get(
                    'https://www.foodmate.net/zhiliang/search.php',
                    params=params,
                    proxies=get_proxies(),
                    headers=headers,
                    verify=False,
                    timeout=10,
                )

            except Exception as e:
                logger.error(f'request list url error:{e}')
                time.sleep(2)
                continue
            else:
                if response.status_code != 200:
                    logger.error(
                        f' get list response status code != 200 :{response.status_code} --- {response.text}')
                    time.sleep(2)
                    continue
                # response.encoding = "utf-8"
                # print(response.text)
                # print(response.status_code)

                response_html = etree.HTML(response.text)
                li_list = response_html.xpath('//div[@class="catlist"]/ul/li[@class="catlist_li"]')
                logger.info(f'column:{self.column_domain} --- {self.page} --- 列表页数量：{len(li_list)}')
                for li in li_list:
                    self.title = li.xpath('./a/@title')[0]
                    self.detail_url = li.xpath('./a/@href')[0]
                    self.publish_time = li.xpath('./span[@class="f_r px11 f_gray"]/text()')[0].split(' ')[0].strip()
                    logger.info(f'{self.publish_time} -- {self.detail_url} -- {self.title}')
                    # if not self.publish_time:
                    #     self.publish_time = li.xpath('./span[@class="f_r px11 f_gray"]/a/text()')[0].split(' ')[0].strip()
                    if self.publish_time < "2024-01-01":
                        logger.info(f'只采集近一年的数据：{self.publish_time}')
                        return

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
        logger.info(f'process -- {self.page} -- {self.title} -- {self.detail_url}')
        while True:
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                # 'Referer': self.list_url,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
                'Host': 'www.foodmate.net'
            }
            try:
                # time.sleep(2)
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
                    logger.error(
                        f'response get detail status code != 200 :{response.status_code} --- {response.text}')
                    time.sleep(2)
                    continue

                # response.encoding = "gbk"

                res_text = html.unescape(response.text)

                response_html = etree.HTML(res_text)

                info_text_xpath = response_html.xpath('//div[@class="info"]/text()')
                # print(info_text_xpath)
                if info_text_xpath:
                    info_text_re = re.findall('来源：(.*?)\xa0', res_text)
                    # print(info_text_re)
                    if info_text_re:
                        if info_text_re[0].__contains__('</a>'):
                            W_文章来源 = re.findall('>(.*?)</a>', info_text_re[0])[0]
                        else:
                            W_文章来源 = info_text_re[0]
                    else:
                        W_文章来源 = ""
                else:
                    W_文章来源 = ""
                # print(W_文章来源)
                W_文章摘要 = response_html.xpath('//div[@class="introduce"]/text()')[0].replace('核心提示：', '').strip()
                # 用BeautifulSoup解析HTML
                soup = BeautifulSoup(res_text, 'html.parser')

                # 将BeautifulSoup对象转换为字符串
                content_str = str(soup.find(name='div', attrs={'id': 'article'}))
                if not content_str:
                    logger.error(f'详情页没有 article：{self.detail_url} --- {response.status_code}')
                    time.sleep(100)
                    continue

                data = {
                    "_id": self.detail_url,
                    "标题": self.title,
                    "网站发布时间": self.publish_time,
                    "文章地址URL": self.detail_url,
                    "采集源名称": "食品伙伴网-质量管理",
                    "正文": content_str,
                    "HTML": res_text,
                    "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": 0,
                    "平台形式": "网站",
                    "数据类型": "法规",
                    "W_文章来源": W_文章来源,
                    "W_文章摘要": W_文章摘要,
                }
                # print(json.dumps(data, ensure_ascii=False))
                if save_articles(data):
                    pass
                    metrics.emit_counter("详情页采集量", count=1, classify=f"食品伙伴网-质量管理")
                return


if __name__ == '__main__':
    metrics.init()

    obj = foodmateZhiLiang()
    obj.scheduler()

    metrics.close()
    MongoClient.close()
