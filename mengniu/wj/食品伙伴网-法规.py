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


class foodmateLaw(object):

    def __init__(self):
        self.column_domain = None
        self.page = None
        self.detail_url = None
        self.publish_time = None
        self.title = None
        self.column = None

    def scheduler(self):
        column_list = [
            ("guojia", "食品伙伴网-法规-国家法规"),
            ("difang", "食品伙伴网-法规-地方法规"),
            ("guowai", "食品伙伴网-法规-国外法规"),
            ("qita", "食品伙伴网-法规-其他法规"),
            # ("", "食品伙伴网-法规-"),
        ]

        for self.column in column_list:
            self.column_domain = self.column[0]
            self.get_list()

    def get_list(self):
        self.page = 1

        while True:
            if self.page > 20:
                logger.success(f'{self.column[1]} 处理完毕')
                return
            logger.info(f'process list page：{self.column_domain} -- {self.page}')
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                # 'Connection': 'keep-alive',
                # 'Cookie': 'td_cookie=2366814296; bc08_f0d8_saltkey=J5H8O5Uj; bc08_f0d8_lastvisit=1735266734; td_cookie=2279423562; bc08_f0d8_lastact=1736296139%09api.php%09js; Hm_lvt_2aeaa32e7cee3cfa6e2848083235da9f=1735874552,1736131641,1736210820,1736296141; HMACCOUNT=FD0AE6F4DC0188C4; __51cke__=; Hm_lvt_e0394b4e8560afaa115b5cb521118fcb=1735874552,1736131917,1736210820,1736296144; Hm_lpvt_2aeaa32e7cee3cfa6e2848083235da9f=1736298221; Hm_lpvt_e0394b4e8560afaa115b5cb521118fcb=1736298221; __tins__1636395=%7B%22sid%22%3A%201736298221464%2C%20%22vd%22%3A%201%2C%20%22expires%22%3A%201736300021464%7D; __51laig__=11',
                # 'Referer': 'http://law.foodmate.net/guojia/list_2.html',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
                'Host': 'law.foodmate.net'
            }
            try:
                time.sleep(2)
                self.list_url = f'http://law.foodmate.net/{self.column_domain}/list_{self.page}.html'
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
                # print(response.text)
                # print(response.status_code)

                response_html = etree.HTML(response.text)
                div_list = response_html.xpath('//div[@class="bzlist"]/ul/li/div[@class="bz_listl"]')
                logger.info(f'column:{self.column_domain} --- {self.page} --- 列表页数量：{len(div_list)}')
                for div in div_list:
                    self.title = div.xpath('./ul[1]/a/@alt')[0]
                    self.detail_url = div.xpath('./ul[1]/a/@href')[0]
                    F_有效性状态_en = div.xpath('./ul[1]/a/img/@src')[0].split('/')[-1].split('.')[0]
                    self.F_有效性状态 = F_有效性状态_mapping[F_有效性状态_en]
                    self.publish_time = re.findall('(\d{4}-\d{2}-\d{2})', div.xpath('./ul[@class="ls_bq"]/span/text()')[0])[0]
                    logger.info(f"{self.publish_time}, {self.F_有效性状态}, {self.detail_url}, {self.title}")
                    if self.publish_time < "2025-01-01":
                        logger.info(f'只采集近一年的数据：{self.publish_time}')
                        return
                    find_detail_url = mengniu_data_original_col.find_one({"_id": self.detail_url}, "")
                    if find_detail_url:
                        logger.info(f'已经采集过：{self.publish_time}, {self.F_有效性状态}, {self.detail_url}, {self.title}')
                        continue
                        # return
                    self.get_detail()
                    # return
                self.page += 1
                # return

    def get_detail(self):
        logger.info(f'process {self.column_domain} -- {self.page} -- {self.title} -- {self.detail_url}')
        while True:
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                # 'Referer': self.list_url,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
                'Host': 'law.foodmate.net'
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
                    logger.error(
                        f'response get detail status code != 200 :{response.status_code} --- {response.text}')
                    time.sleep(2)
                    continue
                response.encoding = "utf-8"
                res_text = html.unescape(response.text)
                # print(res_text)
                # print(response.status_code)

                response_html = etree.HTML(res_text)

                info_text_xpath = response_html.xpath('//div[@class="info"]/text()')
                # print(info_text_xpath)
                if info_text_xpath:
                    info_text_re = re.findall('来源：(.*?)\xa0', res_text)
                    # print(info_text_re)
                    if info_text_re:
                        if info_text_re[0].__contains__('</a>'):
                            F_法规来源 = re.findall('>(.*?)</a>', info_text_re[0])[0]
                        else:
                            F_法规来源 = info_text_re[0]
                    else:
                        F_法规来源 = ""
                else:
                    F_法规来源 = ""
                F_法规摘要 = response_html.xpath('//div[@class="introduce"]/text()')[0].replace('核心提示：', '').strip()

                F_发布单位_xpath = response_html.xpath('//th[contains(text(), "发布单位")]/following-sibling::td[1]//div[@id="abc"]/text()')
                if F_发布单位_xpath:
                    F_发布单位 = F_发布单位_xpath[0].strip()
                else:
                    F_发布单位_xpath = response_html.xpath('//th[contains(text(), "发布单位")]/following-sibling::td[1]/text()')
                    if F_发布单位_xpath:
                        F_发布单位 = F_发布单位_xpath[0].strip()
                    else:
                        F_发布单位 = ""

                F_发布文号 = response_html.xpath('//th[contains(text(), "发布文号")]/following-sibling::td[1]/text()')[0].strip()

                F_发布日期_xpath = response_html.xpath('//th[contains(text(), "发布日期")]/following-sibling::td[1]/a/text()')
                F_发布日期 = F_发布日期_xpath[0].strip() if F_发布日期_xpath else ""

                F_生效日期_xpath = response_html.xpath('//th[contains(text(), "生效日期")]/following-sibling::td[1]/a/text()')
                F_生效日期 = F_生效日期_xpath[0].strip() if F_生效日期_xpath else ""

                F_废止日期_xpath = response_html.xpath('//th[contains(text(), "废止日期")]/following-sibling::td[1]/text()')
                F_废止日期 = F_废止日期_xpath[0].strip() if F_废止日期_xpath else ""

                F_属性_xpath = response_html.xpath('//th[contains(text(), "属性")][1]/following-sibling::td[1]/text()')
                F_属性 = F_属性_xpath[0].strip() if F_属性_xpath else ""

                F_专业属性_xpath = response_html.xpath('//th[contains(text(), "专业属性")]/following-sibling::td[1]/text()')
                F_专业属性 = F_专业属性_xpath[0].strip() if F_专业属性_xpath else ""

                F_备注_xpath = response_html.xpath('//th[contains(text(), "备注")]/following-sibling::td[1]//text()')
                F_备注 = "".join([_F_备注.strip() for _F_备注 in F_备注_xpath]) if F_备注_xpath else ""

                # 用BeautifulSoup解析HTML
                soup = BeautifulSoup(res_text, 'html.parser')

                # 将BeautifulSoup对象转换为字符串
                content_str = str(soup.find(name='div', attrs={'id': 'article'}))
                if not content_str:
                    logger.error(f'详情页没有 article：{self.detail_url} --- {response.status_code}')
                    time.sleep(100)
                    continue

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
                    "数据类型": "法规",
                    "F_法规名称": self.title,
                    "F_发布文号": F_发布文号,
                    "F_专业属性": F_专业属性,
                    "F_发布单位": F_发布单位,
                    "F_发布日期": F_发布日期,
                    "F_生效日期": F_生效日期,
                    "F_废止日期": F_废止日期,
                    "F_有效性状态": self.F_有效性状态,
                    "F_属性": F_属性,
                    "F_备注": F_备注,
                    "F_法规来源": F_法规来源,
                    "F_法规摘要": F_法规摘要,
                }
                # print(json.dumps(data, ensure_ascii=False))
                if save_articles(data):
                    metrics.emit_counter("详情页采集量", count=1, classify=f"{self.column[1]}")
                return


if __name__ == '__main__':
    metrics.init()

    obj = foodmateLaw()
    obj.scheduler()

    metrics.close()
    MongoClient.close()
