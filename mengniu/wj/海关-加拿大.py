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


# 按url获取特殊界面
def get_page1():
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        # 'Connection': 'keep-alive',
        # 'Cookie': 'Apache=106.37.240.36.1748225352740317; _gid=GA1.3.1306163065.1748225644; _ga=GA1.1.617237689.1748225364; _ga_QTGHKKHBHH=GS2.1.s1748225364$o1$g1$t1748225969$j0$l0$h0',
        'Referer': 'https://www.cbsa-asfc.gc.ca/menu-eng.html',
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

    response = requests.get('https://www.cbsa-asfc.gc.ca/import/menu-eng.html', headers=headers)
    print(response.text)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 将BeautifulSoup对象转换为字符串
    content_str = str(soup.find(name='section', attrs={'class': 'alert alert-info'}))
    data = {
        "_id": "https://www.cbsa-asfc.gc.ca/import/menu-eng.html",
        "标题": "Importing goods into Canada",
        "网站发布时间": "",
        "文章地址URL": "https://www.cbsa-asfc.gc.ca/import/menu-eng.html",
        "采集源名称": "海关",
        "正文": content_str,
        "HTML": response.text,
        "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": 0,
        "平台形式": "网站",
        "数据类型": "法规"
    }
    print(json.dumps(data))
    # save_articles(data)


def get_page2():
    url_list = [
        # "https://www.cbsa-asfc.gc.ca/import/origin-origine-eng.html",
        "https://www.cbsa-asfc.gc.ca/import/guide-eng.html",
        "https://www.cbsa-asfc.gc.ca/import/guide-2-eng.html",
        "https://www.cbsa-asfc.gc.ca/import/guide-3-eng.html",
        "https://www.cbsa-asfc.gc.ca/import/guide-4-eng.html",
        "https://www.cbsa-asfc.gc.ca/import/guide-5-eng.html",
        "https://www.cbsa-asfc.gc.ca/import/guide-6-eng.html",
    ]
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        # 'Connection': 'keep-alive',
        # 'Cookie': 'Apache=106.37.240.36.1748225352740317; _gid=GA1.3.1306163065.1748225644; _ga=GA1.1.617237689.1748225364; _ga_QTGHKKHBHH=GS2.1.s1748225364$o1$g1$t1748225969$j0$l0$h0',
        # 'Referer': 'https://www.cbsa-asfc.gc.ca/menu-eng.html',
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

    for url in url_list:
        response = requests.get(url=url, headers=headers)
        res_text = html.unescape(response.text)
        res_html = etree.HTML(res_text)
        title = res_html.xpath('//header/h1/text()')[0].strip()
        print(response.text)
        soup = BeautifulSoup(res_text, 'html.parser')

        archived = soup.find('section', id='archived')
        if archived:
            archived.decompose()

        archived_bnr = soup.find('section', id='archived-bnr')
        if archived_bnr:
            archived_bnr.decompose()

        div = soup.find(name='div', attrs={'class': 'gc-stp-stp brdr-bttm mrgn-tp-md mrgn-bttm-lg'})
        if div:
            div.decompose()

        nav = soup.find(name='nav', attrs={'class': 'mrgn-bttm-lg'})
        if nav:
            nav.decompose()

        # 将BeautifulSoup对象转换为字符串
        content_str = str(soup.find(name='main', attrs={'role': 'main'}))
        data = {
            "_id": url,
            "标题": title,
            "网站发布时间": "",
            "文章地址URL": url,
            "采集源名称": "海关",
            "正文": content_str,
            "HTML": res_text,
            "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": 0,
            "平台形式": "网站",
            "数据类型": "法规"
        }
        print(json.dumps(data))
        # save_articles(data)



def get_page3():

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        # 'Connection': 'keep-alive',
        # 'Cookie': 'Apache=106.37.240.36.1748225352740317; _gid=GA1.3.1306163065.1748225644; _ga=GA1.1.617237689.1748225364; _ga_QTGHKKHBHH=GS2.1.s1748225364$o1$g1$t1748225969$j0$l0$h0',
        # 'Referer': 'https://www.cbsa-asfc.gc.ca/menu-eng.html',
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

    response = requests.get(url="https://www.cbsa-asfc.gc.ca/publications/cn-ad/menu-eng.html", headers=headers)
    res_text = html.unescape(response.text)
    # print(res_text)
    res_html = etree.HTML(res_text)

    tr_list = res_html.xpath('//table[@class="wb-tables table table-condensed table-striped table-hover"]/tbody/tr')
    print(len(tr_list))
    for tr in tr_list:
        detail_link = tr.xpath('./th[1]/a/@href')
        if not detail_link:
            continue
        detail_url = urllib.parse.urljoin("https://www.cbsa-asfc.gc.ca/publications", detail_link[0])
        updateTime = "".join(tr.xpath('./td[3]/text()')).strip()
        if updateTime >= "2024-01-01":
            time.sleep(2)
            detail_res = requests.get(url=detail_url, headers=headers)
            detail_res_text = html.unescape(detail_res.text)
            # print(detail_res_text)
            detail_res_html = etree.HTML(detail_res_text)
            title = detail_res_html.xpath('//div[@class="container"]/h1/text()')[0].strip()
            publishTime = detail_res_html.xpath('//time[1]/@datetime')[0]
            print(publishTime, title)
            soup = BeautifulSoup(detail_res_text, 'html.parser')
            # 将BeautifulSoup对象转换为字符串
            mainContentOfPage = soup.find(name='main', attrs={'property': 'mainContentOfPage'})
            content_str = str(mainContentOfPage.find(name='div', attrs={'class': 'container'}))
            data = {
                "_id": detail_url,
                "标题": title,
                "网站发布时间": publishTime,
                "文章地址URL": detail_url,
                "采集源名称": "海关",
                "正文": content_str,
                "HTML": detail_res_text,
                "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": 0,
                "平台形式": "网站",
                "数据类型": "法规"
            }
            # print(json.dumps(data))
            save_articles(data)
            # return





if __name__ == '__main__':
    # metrics.init()

    # obj = CustomsGovtNZ()
    # obj.scheduler()
    #

    # get_page1()
    # get_page2()
    get_page3()
    metrics.close()
    MongoClient.close()
