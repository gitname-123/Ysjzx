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
from rs5.wjw_get_cookie import get_rs_cookies
from feapder.utils import metrics


# url_set = set()
class NhcGov(object):

    def __init__(self):
        self.list_url = None
        self.column_domain = None
        self.page = None
        self.detail_url = None
        self.publish_time = None
        self.title = None
        self.column = None
        self.cookies = {}


    def scheduler(self):
        column_list = [
            # # #政策法规
            ("xwdt", "中国人民共和国国家卫生健康委员会", "卫健委-新闻动态"),       # 38
            ("gfxwjj", "中国人民共和国国家卫生健康委员会", "卫健委-规范性文件"),    # 22
            ("zcjd", "中国人民共和国国家卫生健康委员会", "卫健委-政策解读"),          # 4

        ]

        for self.column in column_list:
            self.column_domain = self.column[0]
            self.get_list()

    def get_list(self):
        logger.info(f'处理栏目：{self.column}')
        self.page = 1
        while True:
            if self.page == 1:
                page_arg = "list"
            else:
                page_arg = f"list_{self.page}"
            if self.page > 1:
                logger.success(f'{self.column[2]} 处理完毕')
                return
            headers = {
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Host': 'www.nhc.gov.cn',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            }
            try:
                time.sleep(2)
                self.list_url = f'http://www.nhc.gov.cn/wjw/{self.column_domain}/{page_arg}.shtml'
                response = requests.get(
                    url=self.list_url,
                    proxies=get_proxies(),
                    headers=headers,
                    verify=False,
                    timeout=10,
                    cookies=self.cookies
                )
            except Exception as e:
                logger.error(f'request list url error:{e}')
                time.sleep(2)
                continue
            else:
                if response.status_code != 200:
                    logger.error(f' get list response status code != 200 :{response.status_code}')
                    if response.status_code == 412:
                        logger.info(f'触发瑞数验证')
                        # print(response.text)
                        self.cookies = get_rs_cookies(response)
                        continue

                    time.sleep(2)
                    continue

                response.encoding = 'utf-8'
                # print(response.text)
                if not response.text.__contains__("zxxx_list mt20"):
                    logger.error(f'列表页没有zxxx_list mt20，可能是cookie失效')
                    time.sleep(10)
                    self.cookies = {}
                    continue
                response_html = etree.HTML(response.text)
                li_list = response_html.xpath('//ul[@class="zxxx_list mt20"]/li')
                # if not li_list:
                #     logger.info(f'列表页没 li  -- 程序结束 --- {response.text}')
                #     return
                logger.info(f'column:{self.column[2]} --- {self.page} --- 列表页数量：{len(li_list)}')
                for li in li_list:
                    self.title = li.xpath('./a/@title')[0]

                    self.detail_url = urllib.parse.urljoin(self.list_url, li.xpath('./a/@href')[0])
                    if not str(self.detail_url).__contains__('nhc.gov.cn'):
                        logger.error(f'详情页链接异常{self.detail_url}')
                        time.sleep(10)
                        continue
                    self.publish_time = li.xpath('./span/text()')[0]
                    logger.info(f'{self.publish_time} -- {self.detail_url} --- {self.title}')

                    # if self.detail_url not in url_set:
                    #     url_set.add(self.detail_url)
                    # else:
                    #     logger.error(f'出现重复数据：{self.detail_url} --- {self.column_domain} -- {self.page}')

                    # self.publish_time = li.xpath('./span[@class="f_r px11 f_gray"]/text()')[0].split(' ')[0]
                    # if self.publish_time < "2024-01-01":
                    #     logger.info(f'只采集近一年的数据：{self.publish_time}')
                    #     return
                    #
                    find_detail_url = mengniu_data_original_col.find_one({"_id": self.detail_url})
                    if find_detail_url:
                        logger.info(f'已经采集过：{self.detail_url}, {self.title}')
                        continue
                        # return
                    # return
                    self.get_detail()
                    # return
                self.page += 1
                # return

    def get_detail(self):
        logger.info(f'process {self.column[2]} -- {self.page} -- {self.title} -- {self.detail_url}')
        while True:
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                # 'Connection': 'keep-alive',
                # 'Cookie': 'td_cookie=2477801757; bc08_f0d8_saltkey=VVoM94Jk; bc08_f0d8_lastvisit=1740034105; td_cookie=2327170393; bc08_f0d8_lastact=1740703541%09api.php%09js; Hm_lvt_2aeaa32e7cee3cfa6e2848083235da9f=1740442869,1740550832,1740637704,1740703542; HMACCOUNT=5E3DCAD3DF824D60; __51cke__=; Hm_lpvt_2aeaa32e7cee3cfa6e2848083235da9f=1740704390; __tins__18962677=%7B%22sid%22%3A%201740703544056%2C%20%22vd%22%3A%2014%2C%20%22expires%22%3A%201740706189897%7D; __51laig__=14',
                # 'Referer': 'http://info.foodmate.net/reading/list-4.html',
                'Upgrade-Insecure-Requests': '1',
                'Host': 'www.nhc.gov.cn',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            }
            try:
                time.sleep(2)
                # self.detail_url = "http://www.moa.gov.cn/govpublic/ZZYGLS/202410/t20241016_6464460.htm"
                response = requests.get(
                    url=self.detail_url,
                    proxies=get_proxies(),
                    headers=headers,
                    timeout=10,
                    verify=False,
                    cookies=self.cookies
                )
            except Exception as e:
                logger.error(f'request detail url error:{e}')
                time.sleep(2)
                continue
            else:
                if response.status_code != 200:
                    logger.error(f'response get detail status code != 200 :{response.status_code}')
                    time.sleep(2)
                    if response.status_code == 404:
                        return
                    elif response.status_code == 412:
                        logger.info(f'详情页 触发瑞数验证')
                        # print(response.text)
                        self.cookies = get_rs_cookies(response)
                        continue
                    time.sleep(100)
                    continue

                response.encoding = "utf-8"
                # res_text = html.unescape(response.text)
                # print(response.text)
                # return
                response_html = etree.HTML(response.text)

                if not response.text.__contains__('id="xw_box"'):
                    logger.error(f'列表页没有zxxx_list mt20，可能是cookie失效')
                    time.sleep(10)
                    self.cookies = {}
                    continue
                    # continue
                source_text = ''.join([span_text.strip() for span_text in response_html.xpath('//div[@class="source"]/span/text()') if span_text])

                publish_time_re = re.findall('(\d{4}-\d{2}-\d{2})', source_text)

                if publish_time_re:
                    self.publish_time = publish_time_re[0]
                # 来源
                W_文章来源_xpath = response_html.xpath('//div[@class="source"]/span[@class="mr"]/text()')
                W_文章来源 = W_文章来源_xpath[0].replace("来源:", "").strip() if W_文章来源_xpath else ""

                # 用BeautifulSoup解析HTML
                soup = BeautifulSoup(response.text, 'html.parser')

                # 将BeautifulSoup对象转换为字符串
                content_str = str(soup.find(name='div', attrs={'id': 'xw_box'}))

                data = {
                    "_id": self.detail_url,
                    "标题": self.title,
                    "网站发布时间": self.publish_time,
                    "文章地址URL": self.detail_url,
                    "采集源名称": self.column[1],
                    "正文": content_str,
                    "HTML": response.text,
                    "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": 0,
                    "平台形式": "网站",
                    "数据类型": "文章",
                    "W_文章来源": W_文章来源,
                }
                if save_articles(data):
                    metrics.emit_counter("详情页采集量", count=1, classify=f"{self.column[2]}")
                    # pass
                # print(json.dumps(data, ensure_ascii=False))
                return


if __name__ == '__main__':
    metrics.init()

    obj = NhcGov()
    obj.scheduler()
    # test_list()
    # test_detail()
    metrics.close()
    MongoClient.close()
