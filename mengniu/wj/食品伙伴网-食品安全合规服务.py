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


# url_set = set()
# 采集食品伙伴网 合规模块下的专业解读-标准法规解读
class infoFoodmateReading(object):

    def __init__(self):
        self.list_url = None
        self.column_domain = None
        self.page = None
        self.detail_url = None
        self.publish_time = None
        self.title = None
        self.column = None

    def scheduler(self):
        column_list = [
            ("4", "食品伙伴网-食品安全合规服务", "食品伙伴网-食品安全合规服务-标准法规解读"),
        ]

        for self.column in column_list:
            self.column_domain = self.column[0]
            self.get_list()


    def get_list(self):
        self.page = 1
        while True:
            if self.page > 5:
                logger.success(f'{self.column[2]} 处理完毕')
                return
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
                self.list_url = f'http://info.foodmate.net/reading/list-{self.column_domain}-{self.page}.html'
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
                li_list = response_html.xpath('//div[@class="page-news"]/ul/li')
                if not li_list:
                    logger.info(f'列表页没数据 -- 程序结束')
                    return
                logger.info(f'column:{self.column[2]} --- {self.page} --- 列表页数量：{len(li_list)}')
                for li in li_list:
                    self.title = li.xpath('./span[@class="dateTitle"]/a/text()')[0].strip()
                    self.detail_url = li.xpath('./span[@class="dateTitle"]/a/@href')[0]
                    logger.info(f'{self.detail_url} --- {self.title}')
                    # if self.detail_url not in url_set:
                    #     url_set.add(self.detail_url)
                    # else:
                    #     logger.error(f'出现重复数据：{self.detail_url} --- {self.column_domain} -- {self.page}')
                    try:
                        self.publish_time = re.findall('(\d{4}-\d{2}-\d{2})', li.xpath('./span[@class="f_r"]/text()')[0])[0]
                        if self.publish_time < "2025-01-01":
                            logger.info(f'只采集近一年的数据：{self.publish_time}')
                            return
                    except:
                        pass

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
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
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

                info_text_xpath = response_html.xpath('//div[@class="info"]//text()')
                # print(info_text_xpath)
                if info_text_xpath:
                    # print(res_text)
                    info_text = ''.join(info_text_xpath)
                    W_文章来源_re = re.findall('来源：(.*)', info_text)
                    # print(info_text_re)
                    # '  
                    # 发布日期：2024-08-09  来源：北京市市场监督管理局'

                    W_文章来源 = W_文章来源_re[0] if W_文章来源_re else ""

                    self.publish_time = re.findall('发布日期：(\d{4}-\d{2}-\d{2})', info_text)[0]
                else:
                    W_文章来源 = ""

                introduce_xpath = response_html.xpath('//div[@class="introduce"]/text()')
                introduce = introduce_xpath[0] if introduce_xpath else ""

                # 用BeautifulSoup解析HTML
                soup = BeautifulSoup(res_text, 'html.parser')

                # 将BeautifulSoup对象转换为字符串
                content_str = str(soup.find(name='div', attrs={'id': 'content'}))

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
                    "W_文章摘要": introduce,
                    # "W_地区": W_地区,
                    # "W_行业": W_行业
                }
                if save_articles(data):
                    metrics.emit_counter("详情页采集量", count=1, classify=f"{self.column[2]}")
                # print(json.dumps(data, ensure_ascii=False))
                return


if __name__ == '__main__':
    metrics.init()

    # 合规下的专业解读
    obj = infoFoodmateReading()
    obj.scheduler()

    metrics.close()
    MongoClient.close()
