import html
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
from tools.save import save_articles
from tools.settings import mengniu_data_original_col, MongoClient
import subprocess
from functools import partial
subprocess.Popen = partial(subprocess.Popen, encoding='utf-8')
from feapder.utils import metrics


class foodmateNews(object):

    def __init__(self):
        # self.column_domain = None
        self.page = None
        self.detail_url = None
        self.publish_time = None
        self.title = None
        self.area_id = None

    def scheduler(self):
        area_list = [
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "11",
            "12",
            "13",
            "14",
            "15",
            "16",
            "17",
            "18",
            "19",
            "20",
            "21",
            "22",
            "23",
            "24",
            "25",
            "26",
            "27",
            "28",
            "29",
            "30",
            "31",
            "32",
            "33",
            "34",
            "35",
            "394",
            "395",
            "396",
            "397",
            "398",
            "399",
            "400",
            "401",
            "402",
            "403",
            "404",
            "405",
            "406",
            "407",
            "408",
            "409",
            "410",
            "411",
            "412",
            "413",
            "414",
        ]

        for self.area_id in area_list:
            self.get_list()
            # return

    def get_list(self):
        self.page = 1
        url_set = set()
        while True:
            if self.page > 10:
                logger.success(f'{self.area_id} 处理完毕')
                return
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                # 'Connection': 'keep-alive',
                # 'Cookie': 'bc08_f0d8_saltkey=J5H8O5Uj; bc08_f0d8_lastvisit=1735266734; __gads=ID=1a53cb89db76f503:T=1735276973:RT=1735802741:S=ALNI_MYr0qXyEX2csYtPHUMZoqVca5MbXw; __gpi=UID=00000fba18224aa5:T=1735276973:RT=1735802741:S=ALNI_MallygBD9HV5y0fZ5IcSiDig54i6w; __eoi=ID=70828a6734cbb2f0:T=1735276973:RT=1735802741:S=AA-AfjalsNVuAPRi0cNpL2M3mvMu; Hm_lvt_2aeaa32e7cee3cfa6e2848083235da9f=1735615265,1735795255,1735874552,1736131641; HMACCOUNT=FD0AE6F4DC0188C4; __51cke__=; Hm_lvt_ddf629f3b74ddba55e586cf86019a3a4=1736132078; bc08_f0d8_lastact=1736133091%09api.php%09js; __tins__1636283=%7B%22sid%22%3A%201736132078287%2C%20%22vd%22%3A%2015%2C%20%22expires%22%3A%201736134891704%7D; __51laig__=15; Hm_lpvt_ddf629f3b74ddba55e586cf86019a3a4=1736133092; Hm_lpvt_2aeaa32e7cee3cfa6e2848083235da9f=1736133092',
                # 'If-Modified-Since': 'Mon, 06 Jan 2025 03:04:05 GMT',
                # 'If-None-Match': 'W/"677b4825-cd41"',
                # 'Referer': f'https://news.foodmate.net/quanwei/list_{self.page - 1}.html',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
                'sec-ch-ua': '"Chromium";v="109", "Not_A Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'host': 'exim.foodmate.net'
            }
            try:
                time.sleep(2)
                self.list_url = f'http://exim.foodmate.net/news/area_{self.area_id}_{self.page}.html'
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
                li_list = response_html.xpath('//div[@class="catlist"]/ul/li[@class="catlist_li"]')
                logger.info(f'area:{self.area_id} --- {self.page} --- 列表页数量：{len(li_list)}')
                for li in li_list:
                    self.title = li.xpath('./a/@title')[0]
                    self.detail_url = li.xpath('./a/@href')[0]
                    if self.detail_url not in url_set:
                        url_set.add(self.detail_url)
                    else:
                        logger.error(f'出现重复数据：{self.detail_url} --- {self.area_id} -- {self.page}')

                    self.publish_time = li.xpath('./span[@class="f_r px11 f_gray"]/text()')[0].split(' ')[0]
                    if self.publish_time < "2025-01-01":
                        logger.info(f'只采集近一年的数据：{self.publish_time}')
                        return

                    find_detail_url = mengniu_data_original_col.find_one({"_id": self.detail_url})
                    if find_detail_url:
                        logger.info(f'已经采集过：{self.publish_time}, {self.detail_url}, {self.title}')
                        continue
                        # return
                    logger.info(f'{self.publish_time} -- {self.detail_url} -- {self.title}')
                    self.get_detail()
                    # return
                self.page += 1
                # return

    def get_detail(self):
        logger.info(f'process {self.publish_time} -- {self.area_id} -- {self.page} -- {self.title} -- {self.detail_url}')
        while True:
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                # 'Referer': self.list_url,
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
                'sec-ch-ua': '"Chromium";v="109", "Not_A Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'Host': 'exim.foodmate.net'
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
                response.encoding = "utf-8"
                res_text = html.unescape(response.text)
                # print(res_text)

                response_html = etree.HTML(res_text)

                info_text_xpath = response_html.xpath('//div[@class="info"]/text()')
                # print(info_text_xpath)
                if info_text_xpath:
                    info_text_re = re.findall('来源：(.*?)\xa0', res_text)
                    # print(info_text_re)
                    if info_text_re:
                        W_文章来源 = info_text_re[0]
                    else:
                        W_文章来源 = ""
                else:
                    W_文章来源 = ""

                W_地区_re = re.findall(r'地区：</font>(.*?)</br>', res_text, re.S)
                if W_地区_re:
                    W_地区 = ";".join(re.findall('<font class="gjc_c">(.*?)</font>', W_地区_re[0], re.S))
                else:
                    W_地区 = ""

                W_行业_re = re.findall(r'行业：</font>(.*?)</br>', res_text, re.S)
                if W_行业_re:
                    W_行业 = ";".join(re.findall('<font class="gjc_c">(.*?)</font>', W_行业_re[0], re.S))
                else:
                    W_行业 = ""

                # 用BeautifulSoup解析HTML
                soup = BeautifulSoup(res_text, 'html.parser')

                # 将BeautifulSoup对象转换为字符串
                content_str = str(soup.find(name='div', attrs={'id': 'article'}))

                # content_div = response_html.xpath('//div[@id="article"]')
                # content_str = html.unescape(etree.tostring(content_div[0], encoding="utf-8").decode())
                # print(content_str)
                # print(W_文章来源)

                data = {
                    "_id": self.detail_url,
                    "标题": self.title,
                    "网站发布时间": self.publish_time,
                    "文章地址URL": self.detail_url,
                    "采集源名称": "食品伙伴网-进出口",
                    "正文": content_str,
                    "HTML": res_text,
                    "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": 0,
                    "平台形式": "网站",
                    "数据类型": "文章",
                    "W_文章来源": W_文章来源,
                    "W_文章摘要": "",
                    "W_地区": W_地区,
                    "W_行业": W_行业
                }
                if save_articles(data):
                    metrics.emit_counter("详情页采集量", count=1, classify="食品伙伴网-进出口")
                return


if __name__ == '__main__':
    metrics.init()

    obj = foodmateNews()
    obj.scheduler()

    metrics.close()
    MongoClient.close()
