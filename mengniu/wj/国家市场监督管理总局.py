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
class SamrGov(object):

    def __init__(self):
        self.column_domain = None
        self.page = None
        self.detail_url = None
        self.publish_time = None
        self.title = None
        self.column = None

    def scheduler(self):
        column_list = [
            ("39cd9de1f309431483ef3008309f39ca", "国家市场监督管理总局", "国家市场监督管理总局-新闻"),
            ("5a1c443ecf8c471bb9577ba1ae5d2883", "国家市场监督管理总局", "国家市场监督管理总局-总局文件"),
            # # # ("f6a995f86b4f4362836c3c2d7ce72889", "国家市场监督管理总局", "政策解读"), 政策解读 包含在总局文件中
        ]

        for self.column in column_list:
            self.column_domain = self.column[0]
            self.get_list()


    def get_list(self):
        self.page = 1

        while True:
            if self.page > 3:
                logger.success(f'{self.column[2]} 处理完毕')
                return
            headers = {
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.9',

                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            }
            try:
                params = {
                    'webId': '29e9522dc89d4e088a953d8cede72f4c',
                    'pageId': self.column_domain,
                    'parseType': 'bulidstatic',
                    'pageType': 'column',
                    'tagId': '内容区域',
                    'tplSetId': '5c30fb89ae5e48b9aefe3cdf49853830',
                    'paramJson': '{"pageNo":%d,"pageSize":20}' % self.page,
                }
                logger.info(params)

                response = requests.get(
                    'https://www.samr.gov.cn/api-gateway/jpaas-publish-server/front/page/build/unit',
                    params=params,
                    proxies=get_proxies(),
                    headers=headers,
                    verify=False,
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
                if not response.text.__contains__("生成成功"):
                    logger.info(f'列表页没生成成功数据数据 -- 程序结束 --- {response.text}')
                    return
                res_dict = json.loads(response.text)

                res_html = res_dict['data'].get("html", None)
                # print(res_html)
                if not res_html:
                    logger.info(f'列表页没数据 -- 程序结束 --- {response.text}')
                    return

                response_html = etree.HTML(res_html)
                ul_list = response_html.xpath('//div[@class="Three_zhnlist_02"]/ul')
                if not ul_list:
                    logger.info(f'列表页没 li  -- 程序结束 --- {response.text}')
                    return
                logger.info(f'column:{self.column[2]} --- {self.page} --- 列表页数量：{len(ul_list)}')
                for ul in ul_list:
                    self.title = ul.xpath('./li[@class="nav04Left02_content"]/a/text()')[0].strip()
                    self.detail_url = urllib.parse.urljoin("https://www.samr.gov.cn", ul.xpath('./li[@class="nav04Left02_content"]/a/@href')[0])
                    self.publish_time = ul.xpath('./li[@class="nav04Left02_contenttime"]/text()')[0]
                    logger.info(f'{self.publish_time} -- {self.detail_url} --- {self.title}')
                    # if self.detail_url not in url_set:
                    #     url_set.add(self.detail_url)
                    # else:
                    #     logger.error(f'出现重复数据：{self.detail_url} --- {self.column_domain} -- {self.page}')

                    # self.publish_time = li.xpath('./span[@class="f_r px11 f_gray"]/text()')[0].split(' ')[0]
                    # if self.publish_time < "2024-01-01":
                    #     logger.info(f'只采集近一年的数据：{self.publish_time}')
                    #     return

                    find_detail_url = mengniu_data_original_col.find_one({"_id": self.detail_url})
                    if find_detail_url:
                        logger.info(f'已经采集过：{self.detail_url}, {self.title}')
                        # continue
                        return
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
                    if response.status_code == 404:
                        return
                    continue
                response.encoding = "utf-8"
                res_text = html.unescape(response.text)
                # print(res_text)
                # return
                response_html = etree.HTML(res_text)

                info_text_xpath = response_html.xpath('//li[@class="Three_xilan_04"]//text()')
                # print(info_text_xpath)
                if info_text_xpath:
                    # print(res_text)
                    info_text = ''.join(info_text_xpath)
                    W_文章来源_re = re.findall('信息来源：(.*)', info_text)

                    # print(info_text_re)
                    # '  
                    # 发布日期：2024-08-09  来源：北京市市场监督管理局'
                    if W_文章来源_re:
                        W_文章来源 = W_文章来源_re[0].strip()
                        # print(W_文章来源)
                    else:
                        W_文章来源 = ""
                    self.publish_time = re.findall('发布时间：(\d{4}-\d{2}-\d{2})', info_text)[0]
                else:
                    W_文章来源 = ""

                # 用BeautifulSoup解析HTML
                soup = BeautifulSoup(res_text, 'html.parser')

                # 将BeautifulSoup对象转换为字符串
                if self.column[2] == "新闻":
                    content_str = str(soup.find(name='div', attrs={'id': 'zoom'}))
                else:
                    content_str = str(soup.find(name='div', attrs={'class': 'Three_xilan_02'}))

                # content_div = response_html.xpath('//div[@id="zoom"]')
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
                    # "W_地区": W_地区,
                    # "W_行业": W_行业
                }
                if save_articles(data):
                    metrics.emit_counter("详情页采集量", count=1, classify=f"{self.column[2]}")
                # print(json.dumps(data, ensure_ascii=False))
                return


def test_detail():
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        # 'Cache-Control': 'max-age=0',
        # 'Connection': 'keep-alive',
        # 'Cookie': '__jsluid_s=972b6f40b84c65a0c078361aabe9b6d2; Hm_lvt_54db9897e5a65f7a7b00359d86015d8d=1741853185; HMACCOUNT=57289C7935A0865A; Hm_lpvt_54db9897e5a65f7a7b00359d86015d8d=1741853514; _jsearchq=%u8D22%u653F%3A',
        # 'If-Modified-Since': 'Thu, 13 Mar 2025 01:27:55 GMT',
        # 'If-None-Match': 'W/"67d2349b-7525"',
        # 'Sec-Fetch-Dest': 'document',
        # 'Sec-Fetch-Mode': 'navigate',
        # 'Sec-Fetch-Site': 'none',
        # 'Sec-Fetch-User': '?1',
        # 'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        # 'sec-ch-ua': '"Chromium";v="109", "Not_A Brand";v="99"',
        # 'sec-ch-ua-mobile': '?0',
        # 'sec-ch-ua-platform': '"Windows"',
    }

    response = requests.get(
        'https://www.samr.gov.cn/zw/zfxxgk/fdzdgknr/zljds/art/2025/art_954e41dd22994ecfa93ee90683694362.html',
        proxies=get_proxies(),
        headers=headers,
    )
    print(response.text)
    print(response.status_code)


def test_list():
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        # 'Connection': 'keep-alive',
        # 'Cookie': '__jsluid_s=972b6f40b84c65a0c078361aabe9b6d2; Hm_lvt_54db9897e5a65f7a7b00359d86015d8d=1741853185; HMACCOUNT=57289C7935A0865A; Hm_lpvt_54db9897e5a65f7a7b00359d86015d8d=1741853514; _jsearchq=%u8D22%u653F%3A',
        # 'Referer': 'https://www.samr.gov.cn/zw/zjwj/index.html',
        # 'Sec-Fetch-Dest': 'empty',
        # 'Sec-Fetch-Mode': 'cors',
        # 'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        # 'X-Requested-With': 'XMLHttpRequest',
        # 'sec-ch-ua': '"Chromium";v="109", "Not_A Brand";v="99"',
        # 'sec-ch-ua-mobile': '?0',
        # 'sec-ch-ua-platform': '"Windows"',
    }

    params = {
        'webId': '29e9522dc89d4e088a953d8cede72f4c',
        'pageId': '39cd9de1f309431483ef3008309f39ca',
        'parseType': 'bulidstatic',
        'pageType': 'column',
        'tagId': '内容区域',
        'tplSetId': '5c30fb89ae5e48b9aefe3cdf49853830',
        'paramJson': '{"pageNo":3,"pageSize":20}',
    }

    response = requests.get(
        'https://www.samr.gov.cn/api-gateway/jpaas-publish-server/front/page/build/unit',
        params=params,
        proxies=get_proxies(),
        headers=headers,
    )
    print(response.text)
    print(response.status_code)

if __name__ == '__main__':
    metrics.init()

    obj = SamrGov()
    obj.scheduler()
    # test_list()
    metrics.close()
    MongoClient.close()
