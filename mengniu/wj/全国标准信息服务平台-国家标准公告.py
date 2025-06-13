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


# url_set = set()
class StdSamrGov_nocGB(object):

    def __init__(self):
        self.standardNo = None
        self.page = None
        self.detailUrl = None
        self.publishTime = None
        self.title = None

    def scheduler(self):

        self.page = 1

        while True:
            # if self.page > 3:
            #     logger.success(f'处理完毕')
            #     return
            headers = {
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
                'Host': 'std.samr.gov.cn',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            try:

                params = {
                    'searchText': '',
                    'sortOrder': 'asc',
                    'pageSize': '15',
                    'pageNumber': f'{self.page}',
                    '_': f'{int(time.time() * 1000)}',
                }
                # logger.info(params)

                response = requests.get(
                    'https://std.samr.gov.cn/noc/search/nocGBPage',
                    params=params,
                    proxies=get_proxies(),
                    headers=headers,
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
                if not response.text.__contains__("total"):
                    logger.info(f'列表页没生成成功数据数据 -- 程序结束 --- {response.text}')
                    return
                res_dict = json.loads(response.text)
                for row in res_dict['rows']:

                    self.title = row['TITLE']
                    self.detailUrl = f"https://std.sacinfo.org.cn/gnoc/queryInfo?id={row['PID']}"
                    self.publishTime = row["NOTICE_DATE"]
                    self.standardNo = row["CODE"]
                    logger.info(f'{self.publishTime} -- {self.detailUrl} --- {self.standardNo} --- {self.title}')

                    if self.publishTime < "2024-01-01":
                        logger.info(f'只采集近一年的数据：{self.publishTime}')
                        return

                    find_detail_url = mengniu_data_original_col.find_one({"_id": self.detailUrl})
                    if find_detail_url:
                        logger.info(f'已经采集过：{self.detailUrl}, {self.title}')
                        continue
                        # return
                    # return
                    self.get_detail()
                    # return
                self.page += 1
                # return

    def get_detail(self):
        logger.info(f'process: {self.page} -- {self.title} -- {self.detailUrl}')
        while True:
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                # 'Connection': 'keep-alive',
                # 'Cookie': 'td_cookie=2477801757; bc08_f0d8_saltkey=VVoM94Jk; bc08_f0d8_lastvisit=1740034105; td_cookie=2327170393; bc08_f0d8_lastact=1740703541%09api.php%09js; Hm_lvt_2aeaa32e7cee3cfa6e2848083235da9f=1740442869,1740550832,1740637704,1740703542; HMACCOUNT=5E3DCAD3DF824D60; __51cke__=; Hm_lpvt_2aeaa32e7cee3cfa6e2848083235da9f=1740704390; __tins__18962677=%7B%22sid%22%3A%201740703544056%2C%20%22vd%22%3A%2014%2C%20%22expires%22%3A%201740706189897%7D; __51laig__=14',
                # 'Referer': 'http://info.foodmate.net/reading/list-4.html',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            }
            try:
                time.sleep(2)
                response = requests.get(
                    url=self.detailUrl,
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
                    if response.status_code == 404:
                        return
                    continue
                # response.encoding = "utf-8"
                # res_text = html.unescape(response.text)
                res_text = response.text
                # print(res_text)
                # return

                # 用BeautifulSoup解析HTML
                soup = BeautifulSoup(res_text, 'html.parser')

                # 将BeautifulSoup对象转换为字符串
                content_str = str(soup.find(name='div', attrs={'class': 'container'}))

                # content_div = response_html.xpath('//div[@class="container"]')
                # content_str = html.unescape(etree.tostring(content_div[0], encoding="utf-8").decode())
                # print(content_str)

                data = {
                    "_id": self.detailUrl,
                    "标题": self.title,
                    "网站发布时间": self.publishTime,
                    "文章地址URL": self.detailUrl,
                    "采集源名称": "全国标准信息服务平台",
                    "正文": content_str,
                    "HTML": res_text,
                    "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": 0,
                    "平台形式": "网站",
                    "数据类型": "标准",

                    "B_标准编号": self.standardNo,
                    "B_标准名称": self.title,
                    # "B_标准类别": "",
                    "B_发布日期": self.publishTime,
                    # "B_标准状态": "",
                    # "B_实施日期": "",
                    # "B_颁发部门": "",
                    # "B_废止日期": B_废止日期,
                    # "B_标准介绍": B_标准介绍
                    "附件": ""
                }
                if save_articles(data):
                    metrics.emit_counter("详情页采集量", count=1, classify="全国标准信息服务平台-国家标准公告")
                # print(json.dumps(data, ensure_ascii=False))
                return


if __name__ == '__main__':
    metrics.init()

    obj = StdSamrGov_nocGB()
    obj.scheduler()
    # test_list()
    metrics.close()
    MongoClient.close()
