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
        # 'Cookie': 'BNES_=/gdmtLd3OcmuACfYC0gaImbQPBUwpBbWAVpuTSIgataQSfpN6qCn3t3A0+ViV5FO; BNES_=6DARdTCgSCNNvH8nUvl933eYp8MvXyjoxBf1C75BUfZaXaYa4ZvwSFXm0iK3mYZB; WSS_FullScreenMode=false; themeColor=1193c3; themeColor1=1193c3; themeColor2=0267b1; themeColor3=1f3d6c; themeColor4=000000; themeColor5=ff8a00; themeColor6=FFFFFF; sizeType=; fontSize=12; BNES_=q7r2nfg7rb8CClsJD1M5EoHcR+KWcvr9tpzBU4T/Xz4mjmJ/fW1/W5wwVVEFiBGg',
        # 'If-Modified-Since': 'Tue, 27 May 2025 01:50:00 GMT',
        'Referer': 'https://www.customs.gov.my/en/pages/main.aspx',
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

    response = requests.get('https://www.customs.gov.my/en/cp/Pages/cp_li.aspx', proxies=get_proxies(), headers=headers)
    print(response.text)
    return
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


def Prohibition_of_Imports ():

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        # 'Connection': 'keep-alive',
        # 'Cookie': 'BNES_=/gdmtLd3OcmuACfYC0gaImbQPBUwpBbWAVpuTSIgataQSfpN6qCn3t3A0+ViV5FO; BNES_=6DARdTCgSCNNvH8nUvl933eYp8MvXyjoxBf1C75BUfZaXaYa4ZvwSFXm0iK3mYZB; WSS_FullScreenMode=false; themeColor=1193c3; themeColor1=1193c3; themeColor2=0267b1; themeColor3=1f3d6c; themeColor4=000000; themeColor5=ff8a00; themeColor6=FFFFFF; sizeType=; fontSize=12; BNES_=q7r2nfg7rb8CClsJD1M5EoHcR+KWcvr9tpzBU4T/Xz4mjmJ/fW1/W5wwVVEFiBGg',
        # 'If-Modified-Since': 'Tue, 27 May 2025 01:50:00 GMT',
        'Referer': 'https://www.customs.gov.my/en/pages/main.aspx',
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
    url = "https://www.customs.gov.my/en/cp/Pages/cp_li.aspx"
    response = requests.get(url=url, headers=headers)
    print(response.text)
    res_text = html.unescape(response.text)
    res_html = etree.HTML(res_text)
    title = res_html.xpath('//span[@id="DeltaPlaceHolderPageTitleInTitleArea"]/text()')[0].strip()

    soup = BeautifulSoup(res_text, 'html.parser')

    article_content = soup.find(name='div', attrs={'class': 'article-content'})
    p_s = article_content.find_all(name='p')
    p_s[0].decompose()
    p_s[1].decompose()

    data = {
        "_id": url,
        "标题": title,
        "网站发布时间": "",
        "文章地址URL": url,
        "采集源名称": "海关",
        "正文": str(article_content),
        "HTML": res_text,
        "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": 0,
        "平台形式": "网站",
        "数据类型": "法规"
    }
    print(json.dumps(data))
    save_articles(data)


def Import_Procedure():

    data_list = [
        {"title": "Panduan Ringkas Prosedur Import", "url": "https://www.customs.gov.my/en/cp/Documents/Import/Import Procedure/Panduan Ringkas Prosedur Import 2023.pdf"},
        {"title": "Panduan Ejen Kastam Di Bawah Seksyen 90 Akta Kastam 1967", "url": "https://www.customs.gov.my/en/cp/Documents/Import/Import Procedure/PANDUAN EJEN KASTAM DI BAWAH SEKSYEN 90 AKTA KASTAM 1967 (22 April 2025).pdf"},
        {"title": "Due Diligence Dan Kod Etika Ejen Kastam", "url": "https://www.customs.gov.my/en/cp/Documents/Import/Import Procedure/Due Diligence Dan Kod Etika Ejen Kastam_23042025.pdf"},
        {"title": "Makluman Mengenai Duti Bagi Kenderaan Import Pelajar", "url": "https://www.customs.gov.my/en/cp/Documents/Import/Import Procedure/Makluman Mengenai Duti Bagi Kenderaan Import Pelajar.pdf"},
        {"title": "Garis Panduan Pelepasan Barangan Yang Dibawa Masuk Semula Dari Pelabuhan Kastam Dan Pelabuhan Zon Bebas", "url": "https://www.customs.gov.my/en/cp/Documents/Import/Import Procedure/Garis Panduan Pelepasan Barangan yang dibawa masuk semula dari pelabuhan kastam dan pelabuhan zon bebas.pdf"},
        {"title": "Prosedur Permohonan Lesen Mengimport RMK", "url": "https://www.customs.gov.my/en/cp/Documents/Import/Import Procedure/Prosedur Permohonan Lesen Mengimport RMK (update)_17102022_en1.pdf"},
    ]
    for data in data_list:
        title = data['title']
        url = data['url']
        save_data = {
            "_id": url,
            "标题": title,
            "网站发布时间": "",
            "文章地址URL": url,
            "采集源名称": "海关",
            "正文": "",
            "HTML": "",
            "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": 0,
            "平台形式": "网站",
            "数据类型": "法规",
            "附件": json.dumps([{"fileName": f'{url.split("/")[-1]}', "fileLink": url}])
        }
        print(json.dumps(save_data))
        save_articles(save_data)



if __name__ == '__main__':

    # Import_Procedure()
    Prohibition_of_Imports()

    MongoClient.close()
