import html
import json
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
from tenacity import retry, stop_after_attempt, wait_fixed, before_sleep_log
from dateutil import parser
import logging

exclusion_list = [
    "https://www.customs.govt.nz/business/import/import-prohibited-and-restricted-imports/intellectual-property-rights-and-notices/",
    "https://www.customs.govt.nz/business/import/customs-rulings/published-customs-rulings/", # ****,
    "https://www.customs.govt.nz/business/import/import-forms-and-documents/",   # ****
    "https://www.customs.govt.nz/business/export/export-forms-and-documents/",  # ****
    "https://www.customs.govt.nz/business/excise/excise-forms-and-documents/",   # ****
    "https://www.customs.govt.nz/business/tariffs/tariff-concession-notices/",  # ****
    "https://www.customs.govt.nz/business/trade-single-window/latest-news/",     # ****
    "https://www.customs.govt.nz/business/trade-single-window/resource-material/online-guides/",    # ****
    "https://www.customs.govt.nz/business/trade-single-window/resource-material/tsw-fact-sheets/",
    "https://www.customs.govt.nz/about-us/information-releases/briefing-to-the-incoming-minister/",
    "https://www.customs.govt.nz/about-us/information-releases/cabinet-material/",
    "https://www.customs.govt.nz/about-us/information-releases/comptrollers-expenses/",
    "https://www.customs.govt.nz/about-us/information-releases/corporate-documents/",
    "https://www.customs.govt.nz/about-us/information-releases/external-reportsresearch/",
    "https://www.customs.govt.nz/about-us/information-releases/information-disclosure-agreements/",
    "https://www.customs.govt.nz/about-us/information-releases/official-information-act-requests/general-oias/",
    "https://www.customs.govt.nz/about-us/information-releases/official-information-act-requests/jbms-oias/",
    "https://www.customs.govt.nz/about-us/information-releases/official-information-act-requests/media-oias/",
    "https://www.customs.govt.nz/about-us/information-releases/official-information-act-requests/trade-data-oias/",
    "https://www.customs.govt.nz/about-us/infringements/brochures-and-forms/",
    "https://www.customs.govt.nz/about-us/legislation/customs-and-excise-act-2018/ce-act-documentation/",
    "https://www.customs.govt.nz/about-us/legislation/customs-and-excise-act-2018/information-library/",
    "https://www.customs.govt.nz/about-us/legislation/customs-rules/revoked-or-superceded-rules/",
    "https://www.customs.govt.nz/about-us/legislation/customs-rules/previous-versionsamendment-rules/",
    "https://www.customs.govt.nz/about-us/legislation/legal-documents/",




    "https://www.customs.govt.nz/about-us/news/media-releases/", "https://www.customs.govt.nz/about-us/news/social-media-posts/"
    # 以上均未处理， 需要另开发代码，采集 翻页数据

]

class CustomsGovtNZ(object):

    def __init__(self):
        self.task_url = None
        # self.task_list = [
        #     "https://www.customs.govt.nz/personal/",
        #     "https://www.customs.govt.nz/business/",
        #     "https://www.customs.govt.nz/about-us/",
        #     # "https://www.customs.govt.nz/personal/prohibited-and-restricted-items/",
        #     # "https://www.customs.govt.nz/about-us/news/important-notices/",
        #     # "https://www.customs.govt.nz/about-us/news/important-notices/us-tariff-announcement---contacting-new-zealand-customs/",
        #
        # ]
        self.task_list = ['https://www.customs.govt.nz/about-us/news/important-notices/', ]










        self.headers = {
            'host': 'www.customs.govt.nz',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'zh-CN,zh;q=0.9',
            # 'referer': 'https://www.customs.govt.nz/personal/travel-to-and-from-nz/medicines/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        }

    def scheduler(self):
        while self.task_list:
            print(self.task_list)
            self.task_url = self.task_list.pop(0)
            # self.interval.insert(0, (middle_date, self.month_tuple[1]))
            if self.task_url in exclusion_list:
                continue
            try:
                self.get_page()
            except Exception as e:
                logger.error(f'failed to get {self.task_url}: {e}')
            # return
        else:
            logger.success(f'task finish')

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_fixed(1),
        # before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def get_page(self):
        logger.info(f'task：{self.task_url}')
        try:
            response = requests.get(
                url=self.task_url,
                proxies=get_proxies(),
                headers=self.headers,
                # verify=False,
                timeout=10
            )
        except Exception as e:
            raise logger.error(f'request list url error:{e}')
        else:
            if response.status_code != 200:
                logger.error(f'failed to page {self.task_url}')
                raise logger.error(f'get_page code!=200: {response.status_code} --- url: {self.task_url} --- {response.text}')
            # response.encoding = 'utf-8'
            # print(response.text)
            try:
                self.parse_page(response)
            except Exception as e:
                logger.error(f'parse page error: {e}')
                sys.exit(1)

            return

    def parse_page(self, response):
        response_html = etree.HTML(response.text)
        content_str = ""

        pagesummary = response_html.xpath('//div[@class="pagesummary"]')
        pagesummary_text = pagesummary[0].xpath('.//text()') if pagesummary else None
        if pagesummary_text:
            content_str = content_str + "\n" + html.unescape(etree.tostring(pagesummary[0], encoding="utf-8").decode()) if pagesummary_text else ""

        mainbody = response_html.xpath('//div[@class="mainbody"]')
        mainbody_text_list = mainbody[0].xpath('.//text()') if mainbody else []

        mainbody_text = ''.join([text_item.strip() for text_item in mainbody_text_list])
        if mainbody_text:
            content_str = content_str + "\n" + html.unescape(etree.tostring(mainbody[0], encoding="utf-8").decode())
        if content_str:
            content_str = '<div>' + content_str + '</div>'

            title = response_html.xpath('//div[@id="main-content"]/h1/text()')[0].strip()
            publish_time_xpath = response_html.xpath('//div[@id="main-content"]/p/span/text()')

            # # time_str = "11.19am 10 April 2025"
            # if publish_time_xpath:
            #     print(publish_time_xpath)
            # else:
            #     print('没有发布时间')
            publish_time = parser.parse(publish_time_xpath[0].strip()).strftime("%Y-%m-%d") if publish_time_xpath else ""
            data = {
                "_id": self.task_url,
                "标题": title,
                "网站发布时间": publish_time,
                "文章地址URL": self.task_url,
                "采集源名称": "新西兰海关",
                "正文": content_str,
                "HTML": response.text,
                "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": 0,
                "平台形式": "网站",
                "数据类型": "文章"
            }
            if save_articles(data):
                metrics.emit_counter("详情页采集量", count=1, classify=f"海关-新西兰")
            # print(json.dumps(data, ensure_ascii=False))

        else:
            logger.info(f'page not found content: {self.task_url}')

        detail_list_xpath = response_html.xpath('//div[@id="main-content"]/div[@class="row"]/div[@class="col-md-6 col-lg-4"]//a/@href')
        self.task_list[:0] = [urllib.parse.urljoin("https://www.customs.govt.nz/", detail_url) for detail_url in detail_list_xpath] if detail_list_xpath else []
        # print(self.task_list)


def get_page1():
    headers = {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',

    }

    params = {
        'skip': '0',
        'pageSize': '300',
        'pageCategories[]': '105',
        'sortAscending': 'true',
        'currentPageContentId': '1052',
        '_': f'{int(time.time() * 1000)}',
    }

    response = requests.get('https://www.customs.govt.nz/api/find/news', params=params, proxies=get_proxies(), verify=False, headers=headers)

    # print(response.text)
    res_detail = response.json()
    findResults = res_detail['findResults']
    for result in findResults:
        get_detail(result)
        # return


def get_page2():
    headers = {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',

    }

    params = {
        'skip': '0',
        'pageSize': '50',
        'pageCategories[]': '235',
        'sortAscending': 'true',
        'currentPageContentId': '7502',
        '_': f'{int(time.time() * 1000)}',
    }

    response = requests.get('https://www.customs.govt.nz/api/find/news', params=params, proxies=get_proxies(), verify=False, headers=headers)

    # print(response.text)
    res_detail = response.json()
    findResults = res_detail['findResults']
    for result in findResults:
        get_detail(result)
        # return


def get_detail(data):
    url = data["link"]['href']
    logger.info(url)
    find_detail_url = mengniu_data_original_col.find_one({"_id": url})
    if find_detail_url:
        logger.info(f'已经采集过：{url}')
        return
    retry = 0
    headers = {
        'host': 'www.customs.govt.nz',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'zh-CN,zh;q=0.9',
        # 'referer': 'https://www.customs.govt.nz/personal/travel-to-and-from-nz/medicines/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    }
    while retry < 5:
        try:
            response = requests.get(
                url=url,
                proxies=get_proxies(),
                headers=headers,
                verify=False,
                timeout=10
            )
        except Exception as e:
            logger.error(f'request detail url error:{e}')
            retry += 1
            time.sleep(2)
        else:
            if response.status_code != 200:
                # logger.error(f'failed to page {url}')
                logger.error(f'get_page code!=200: {response.status_code} --- url: {url} --- {response.text}')
            # response.encoding = 'utf-8'
            # print(response.text)

            response_html = etree.HTML(response.text)

            soup = BeautifulSoup(response.text, 'html.parser')

            article_details = soup.find(name='div', attrs={'class': 'article-details'})
            # print(str(article_details))
            p_s = article_details.find_all(name='p')
            if p_s:
                p_s[0].decompose()

            hr = soup.find('hr')
            if hr:
                hr.decompose()

            # 将BeautifulSoup对象转换为字符串
            content_str = str(article_details)

            if content_str:

                title = response_html.xpath('//div[@id="main-content"]/h1/text()')[0].strip()
                publish_time_xpath = response_html.xpath('//div[@class="article-details"]/p/span/text()')

                # # time_str = "11.19am 10 April 2025"
                # if publish_time_xpath:
                #     print(publish_time_xpath)
                # else:
                #     print('没有发布时间')
                publish_time = parser.parse(publish_time_xpath[0].strip()).strftime("%Y-%m-%d") if publish_time_xpath else ""
                save_data = {
                    "_id": url,
                    "标题": title,
                    "网站发布时间": publish_time,
                    "文章地址URL": url,
                    "采集源名称": "新西兰海关",
                    "正文": content_str,
                    "HTML": response.text,
                    "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": 0,
                    "平台形式": "网站",
                    "数据类型": "法规"
                }
                if save_articles(save_data):
                    metrics.emit_counter("详情页采集量", count=1, classify=f"新西兰海关")
                # print(json.dumps(save_data, ensure_ascii=False))
                return
            else:
                logger.error(f'没有正文：{url}')
                logger.error(response.text)
    else:
        logger.error(f'重试五次都失败了：{data}')
        # time.sleep(100)
        return

if __name__ == '__main__':
    metrics.init()

    # # Important notices
    # obj = CustomsGovtNZ()
    # obj.scheduler()

    # Media releases
    get_page1()

    # Our stories
    get_page2()

    metrics.close()
    MongoClient.close()
