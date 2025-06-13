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
from tools.save import save_articles
from tools.settings import mengniu_data_original_col, MongoClient
import subprocess
from functools import partial
subprocess.Popen = partial(subprocess.Popen, encoding='utf-8')
# from feapder.utils import metrics


class foodmateNews(object):

    def __init__(self):
        self.column_domain = None
        self.page = None
        self.detail_url = None
        self.publish_time = None
        self.title = None
        self.column = None

    def scheduler(self):
        column_list = [
            # ("quanwei", "食品伙伴网-资讯-权威发布"),     # >2024 共58页零5条
            # ("shiyao", "食品伙伴网-资讯-权威发布"),
            # ("zhijian", "食品伙伴网-资讯-权威发布"),
            # ("weijiwei", "食品伙伴网-资讯-权威发布"),
            # ("nongye", "食品伙伴网-资讯-权威发布"),
            # ("qita", "食品伙伴网-资讯-权威发布"),
            # #
            # ("guonei", "食品伙伴网-中国食品"),
            # ("yujing", "食品伙伴网-国际预警"),

            ("from_270", "食品伙伴网首页-食品咨询-本站原创"),
        ]

        for self.column in column_list:
            self.column_domain = self.column[0]
            self.get_list()

    def get_list(self):
        self.page = 1
        # url_set = set()
        while True:
            if self.page > 2:
                logger.success(f'{self.column[1]} 处理完毕')
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
                'host': 'news.foodmate.net'
            }
            try:
                time.sleep(2)
                if self.column[1] == "食品伙伴网首页-食品咨询-本站原创":
                    self.list_url = f"https://news.foodmate.net/from_270_{self.page}.html"
                else:
                    self.list_url = f'https://news.foodmate.net/{self.column_domain}/list_{self.page}.html'
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
                logger.info(f'column:{self.column_domain} --- {self.page} --- 列表页数量：{len(li_list)}')
                for li in li_list:
                    self.title = li.xpath('./a/@title')[0]
                    self.detail_url = li.xpath('./a/@href')[0]
                    # if self.detail_url not in url_set:
                    #     url_set.add(self.detail_url)
                    # else:
                    #     logger.error(f'出现重复数据：{self.detail_url} --- {self.column_domain} -- {self.page}')

                    self.publish_time = li.xpath('./span[@class="f_r px11 f_gray"]/text()')[0].split(' ')[0].strip()
                    if not self.publish_time:
                        self.publish_time = li.xpath('./span[@class="f_r px11 f_gray"]/a/text()')[0].split(' ')[0].strip()
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
        logger.info(f'process {self.publish_time} -- {self.column_domain} -- {self.page} -- {self.title} -- {self.detail_url}')
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
                response.encoding = "utf-8"
                res_text = html.unescape(response.text)
                # print(res_text)

                response_html = etree.HTML(res_text)

                info_text_xpath = response_html.xpath('//div[@class="info"]/text()')
                # print(info_text_xpath)
                if info_text_xpath:
                    info_text_re = re.findall('来源：(.*?)\xa0', res_text)
                    # print(info_text_re)
                    W_文章来源 = info_text_re[0] if info_text_re else ""
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
                    "采集源名称": self.column[1],
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
                    pass
                    # metrics.emit_counter("详情页采集量", count=1, classify=f"{self.column[1]}")
                # logger.info(json.dumps(data, ensure_ascii=False))
                return


if __name__ == '__main__':
    # metrics.init()

    obj = foodmateNews()
    obj.scheduler()

    # metrics.close()
    MongoClient.close()
