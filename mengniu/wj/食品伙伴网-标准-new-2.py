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


F_有效性状态_mapping = {
    "jjss": "即将实施",
    "xxyx": "现行有效",
    "yjfz": "已经废止",
    "bfyx": "部分有效",
    "jjfz": "即将废止",
    "jdxwj": "阶段性文件",
    "wz": "未知",
    "bfsx": "部分生效"
}


# 通过检索查询
class foodmateStandard(object):
    def __init__(self):
        self.column_domain = None
        self.page = None
        self.detail_url = None
        self.publish_time = None
        self.title = None
        self.column = None

    def scheduler(self):
        column_list = [
            # ("3", "食品伙伴网-标准-国内标准-国家标准"),
            # ("4", "食品伙伴网-标准-国内标准-行业标准"),
            ("15", "食品伙伴网-标准-国内标准-地方标准"),
            # # # # ("qiyebiaozhun", "食品伙伴网-标准-国内标准-企业标准"),
            # ("12", "食品伙伴网-标准-国内标准-团体标准"),
            # ("9", "食品伙伴网-标准-国内标准-其他国内标准"),
            # ("2", "食品伙伴网-标准-国外标准"),
        ]

        for self.column in column_list:
            self.column_domain = self.column[0]
            self.get_list()

    def get_list(self):
        self.page = 1

        while True:
            logger.info(f'process list page：{self.column[1]} -- {self.page}')
            # if self.page > 10:
            #     logger.success(f'{self.column[1]} 处理完毕')
            #     return
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                # 'Connection': 'keep-alive',
                # 'Cookie': 'td_cookie=2472681024; bc08_f0d8_saltkey=J5H8O5Uj; bc08_f0d8_lastvisit=1735266734; td_cookie=1345700005; Hm_lvt_2aeaa32e7cee3cfa6e2848083235da9f=1736131641,1736210820,1736296141,1736381620; HMACCOUNT=FD0AE6F4DC0188C4; bc08_f0d8_lastact=1736400097%09api.php%09js; __51cke__=; Hm_lvt_d4fdc0f0037bcbb9bf9894ffa5965f5e=1735795255,1736147885,1736299343,1736400102; u_rdown=1; PHPSESSID=03fdd3042375c862ff2bbfb4c2b4ba87; Hm_lpvt_2aeaa32e7cee3cfa6e2848083235da9f=1736404007; Hm_lpvt_d4fdc0f0037bcbb9bf9894ffa5965f5e=1736404007; __tins__1484185=%7B%22sid%22%3A%201736403162122%2C%20%22vd%22%3A%2019%2C%20%22expires%22%3A%201736405806952%7D; __51laig__=20',
                # 'Referer': 'http://down.foodmate.net/standard/search.php?kw=&fields=0&corpstandard=2&bzstatus=0&fromtime=2024-01-01&totime=2025-01-09&catid=6&sfromtime=&stotime=&sub.x=80&sub.y=9',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
                'Host': 'down.foodmate.net',
                # 'cookie': 'td_cookie=1137864979; bc08_f0d8_saltkey=l8F5Yt12; bc08_f0d8_lastvisit=1743387952; bc08_f0d8_lastact=1744762050%09api.php%09js; Hm_lvt_2aeaa32e7cee3cfa6e2848083235da9f=1744096037,1744157465,1744352104,1744762051; HMACCOUNT=5E3DCAD3DF824D60; Hm_lvt_d4fdc0f0037bcbb9bf9894ffa5965f5e=1743145023,1743658183,1744352104,1744762082; __51cke__=; u_rdown=1; PHPSESSID=a7c27058e138b29a6d8e7b281997d2a8; u_search_code=6813ba5955d41b29f17648188f105c56; tfstk=glZ-I8xbjsfkeznGqg_D-tOyRPXcokerk7y6xXYIVSHLGRunR9ou9vF09H4udJxKdjNUtzfzZreQaJNK8TlnOXF3dzXcjG2zUDoIv1jGjZ-jjjPJOHg5dxMsetD5K44iDDoCssvppggSY55DPvq7htHnd3GQOvwfHADtA3gBVEOjgviIAYTWlnMrQYOIOWwfHvljODiI12CKGLGHvPypJ3KHpXKBAoH-lq2SGQ3gcY3-18THAH9se4h_FjCaP8NZlJuLYp-Kk8aaTANWN6hUD-Z7551DrbatpR4LFgtjquy752Z1TewombFIJr59jYnukVE8z9RbF5c850yHB_2xWr3Zhq9pP04gIku_VgdZiVkLMV4R63F14DZgXaoMsfHHPtBv8euS302O2cVpevmmHfXRve8EutkxstBv8euS3xhGe9Le8qWV.; u_last_search=1744778674; __tins__1484185=%7B%22sid%22%3A%201744777074617%2C%20%22vd%22%3A%2068%2C%20%22expires%22%3A%201744780624252%7D; __51laig__=198; Hm_lpvt_d4fdc0f0037bcbb9bf9894ffa5965f5e=1744778824; Hm_lpvt_2aeaa32e7cee3cfa6e2848083235da9f=1744778824'
            }
            try:

                time.sleep(2)
                response = requests.get(
                    f'http://down.foodmate.net/standard/sort/{self.column_domain}/index-{self.page}.html',
                    proxies=get_proxies(),
                    # cookies=cookies,
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
                # response.encoding = "ISO-8859-1"
                response.encoding = "GB2312"
                # print(response.text)
                # print(response.status_code)
                # return
                response_html = etree.HTML(response.text)
                div_list = response_html.xpath('//div[@class="bz_listl"]')
                logger.info(f'column:{self.column_domain} --- {self.page} --- 列表页数量：{len(div_list)}')
                if not div_list:
                    logger.error(f'列表页没数据 --- {self.column[1]} --- {self.page}')
                    return
                for div in div_list:
                    self.title = div.xpath('./ul[1]/a/b/text()')[0].strip()
                    self.detail_url = div.xpath('./ul[1]/a/@href')[0]
                    F_有效性状态_en = div.xpath('./ul[1]/a/img/@src')[0].split('/')[-1].split('.')[0]
                    self.F_有效性状态 = F_有效性状态_mapping[F_有效性状态_en]
                    try:
                        self.publish_time = re.findall('(\d{4}-\d{2}-\d{2})', div.xpath('./ul[@class="ls_bq"]/span[@class="lb_ft"]/text()')[0])[0]

                    except:
                        logger.error(f'列表页没有发布时间：{self.detail_url}')
                        continue
                    logger.info(f"{self.publish_time}, {self.F_有效性状态}, {self.detail_url}, {self.title}")
                    if self.publish_time < "2024-01-01":
                        continue
                    find_detail_url = mengniu_data_original_col.find_one({"_id": self.detail_url})
                    if find_detail_url:
                        logger.info(f'已经采集过：{self.publish_time}, {self.detail_url}, {self.title}')
                        mengniu_data_original_col.update_one({"_id": self.detail_url}, {"$set": {"标题": self.title, "B_标准名称": self.title, "B_标准状态": self.F_有效性状态}})
                        continue
                        # return
                    self.get_detail()
                    # return
                self.page += 1
                # return

    def get_detail(self):
        logger.info(f'process {self.column[1]} -- {self.page} -- {self.title} -- {self.detail_url}')
        while True:
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                # 'Referer': self.list_url,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
                'Host': 'down.foodmate.net'
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
                response.encoding = "gbk"
                # res_text = html.unescape(response.text)
                # print(res_text)
                # print(response.status_code)
                res_text = response.text
                response_html = etree.HTML(res_text)

                try:
                    B_标准编号 = re.findall('(.*?-\d{4})', self.title)[0].strip()
                except:
                    try:
                        B_标准编号 = re.findall('(.*?\d+ \d{4})', self.title)[0].strip()
                    except:
                        B_标准编号 = re.findall('([a-zA-Z0-9/ -]+ )', self.title, re.S)[0].strip()

                B_标准名称 = self.title

                B_标准类别_xpath = response_html.xpath('//th[contains(text(), "标准类别")]/following-sibling::td[1]/text()')
                B_标准类别 = B_标准类别_xpath[0].strip() if B_标准类别_xpath else ""

                B_发布日期_xpath = response_html.xpath('//th[contains(text(), "发布日期")]/following-sibling::td[1]/text()')
                B_发布日期 = B_发布日期_xpath[0].strip() if B_发布日期_xpath else ""
                if B_发布日期 < "2024-01-01":
                    logger.error(f'详情页发布日期<2024:{self.detail_url}')
                    return

                B_标准状态 = self.F_有效性状态

                B_实施日期_xpath = response_html.xpath('//th[contains(text(), "实施日期")]/following-sibling::td[1]/text()')
                B_实施日期 = B_实施日期_xpath[0].strip() if B_实施日期_xpath else ""

                B_颁发部门_xpath = response_html.xpath('//th[contains(text(), "颁发部门")]/following-sibling::td[1]/text()')
                B_颁发部门 = B_颁发部门_xpath[0].strip() if B_颁发部门_xpath else ""

                B_废止日期_xpath = response_html.xpath('//th[contains(text(), "废止日期")]/following-sibling::td[1]/text()')
                B_废止日期 = B_废止日期_xpath[0].strip() if B_废止日期_xpath else ""


                # 用BeautifulSoup解析HTML
                soup = BeautifulSoup(res_text, 'html.parser')

                # 将BeautifulSoup对象转换为字符串
                content_str = str(soup.find(name='div', attrs={'class': 'bznr_box'}))
                if not content_str:
                    logger.error(f'详情页没有 article：{self.detail_url} --- {response.status_code}')
                    time.sleep(100)
                    # continue
                    content_str = ""

                B_标准介绍 = content_str

                data = {
                    "_id": self.detail_url,
                    "标题": self.title,
                    "网站发布时间": B_发布日期,
                    "文章地址URL": self.detail_url,
                    "采集源名称": self.column[1],
                    "正文": B_标准介绍,
                    "HTML": res_text,
                    "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": 0,
                    "平台形式": "网站",
                    "数据类型": "标准",
                    "B_标准编号": B_标准编号,
                    "B_标准名称": B_标准名称,
                    "B_标准类别": B_标准类别,
                    "B_发布日期": B_发布日期,
                    "B_标准状态": B_标准状态,
                    "B_实施日期": B_实施日期,
                    "B_颁发部门": B_颁发部门,
                    "B_废止日期": B_废止日期,
                    "B_标准介绍": B_标准介绍
                }
                # print(json.dumps(data, ensure_ascii=False))
                if save_articles(data):
                    pass
                    # metrics.emit_counter("详情页采集量", count=1, classify=f"{self.column[1]}")
                return


if __name__ == '__main__':
    metrics.init()

    obj = foodmateStandard()
    obj.scheduler()

    metrics.close()
    MongoClient.close()
