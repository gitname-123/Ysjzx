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


# from tools.get_proxy import get_proxies
from tools.save import save_articles
from tools.settings import mengniu_data_original_col, MongoClient
# import subprocess
# from functools import partial
# subprocess.Popen = partial(subprocess.Popen, encoding='utf-8')
# from feapder.utils import metrics
# from tenacity import retry, stop_after_attempt, wait_fixed, before_sleep_log
# from dateutil import parser


# 按url获取特殊界面
def get_page1():
    headers = {
        'authority': 'bdfa.gov.bn',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'zh-CN,zh;q=0.9',
        # 'cookie': '_ga=GA1.1.1215510926.1748323882; _ga_Y8ELNQKD2L=GS2.1.s1748323881$o1$g1$t1748324501$j0$l0$h0',
        'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    }
    url = "https://bdfa.gov.bn/services-import-export-page/#importing-food-for-commercial"
    response = requests.get(url=url, headers=headers)
    print(response.text)
    res_html = etree.HTML(response.text)
    content = res_html.xpath('//div[@id="importing-food-for-commercial"]/following-sibling::div[1]')
    content_str = html.unescape(etree.tostring(content[0], encoding='utf-8').decode())

    data = {
        "_id": url,
        "标题": "IMPORTING FOOD FOR COMMERCIAL PURPOSES",
        "网站发布时间": "2023-03-07",
        "文章地址URL": url,
        "采集源名称": "食品局",
        "正文": content_str,
        # "HTML": response.text,
        "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": 0,
        "平台形式": "网站",
        "数据类型": "法规"
    }
    print(json.dumps(data))
    # save_articles(data)


def legislations():

    data_list = [
        {
            "title": "(No. S 45) – Brunei Darussalam Food Order, 2020 – Constitution Of Brunei Darussalam (Order Made Under Article 83(3))",
            "publishTime": "2020-12-21",
            "url": "https://www.agc.gov.bn/AGC%20Images/LAWS/Gazette_PDF/2020/EN/S045.pdf"
        },
        {
            "title": "Public Health (Food) Act (Chapter 182)",
            "publishTime": "",
            "url": "https://www.agc.gov.bn/AGC%20Images/LAWS/ACT_PDF/Cap.182.pdf"
        },
        {
            "title": "Public Health (Food) Regulations (R1, Chapter 182)",
            "publishTime": "",
            "url": "https://www.agc.gov.bn/AGC%20Images/LAWS/ACT_PDF/Cap182subRg1.pdf"
        },
        {
            "title": "Public Health (Food) Regulations (R1, Chapter 182) Amendment",
            "publishTime": "2020-12-31",
            "url": "https://www.agc.gov.bn/AGC%20Images/LAWS/Gazette_PDF/2020/EN/S047.pdf"
        },
        {
            "title": "(No. S 7) – Wholesome Meat Order, 2011 – Wholesome Meat (Slaughtering Centres) Regulations, 2011",
            "publishTime": "2011-02-17",
            "url": "https://bdfa.gov.bn/wp-content/uploads/2022/11/Wholesome-meat-slaughterhouse.pdf"
        },
        {
            "title": "(No. S 8) – Wholesome Meat Order, 2011 – Wholesome Meat (Transportation) Regulations, 2011",
            "publishTime": "2011-02-17",
            "url": "https://bdfa.gov.bn/wp-content/uploads/2022/11/wholesome-meat-transportation-regulations-2011.pdf"
        },
        {
            "title": "(No. S 9) – Wholesome Meat Order, 2011 – Wholesome Meat (Import, Export And Transhipment) Regulations, 2011",
            "publishTime": "2011-02-17",
            "url": "https://bdfa.gov.bn/wp-content/uploads/2022/11/Wholesome-meat-Import-export-transhipment-regulation-2011.pdf"
        },
        {
            "title": "(No. S 10) – Wholesome Meat Order, 2011 – Wholesome Meat (Fees) Regulations, 2011",
            "publishTime": "2011-02-17",
            "url": "https://bdfa.gov.bn/wp-content/uploads/2022/11/Wholesome-meat-fees-regulations-2011.pdf"
        },

    ]
    for data in data_list:
        title = data['title']
        url = data['url']
        save_data = {
            "_id": url,
            "标题": title,
            "网站发布时间": data["publishTime"],
            "文章地址URL": url,
            "采集源名称": "食品局",
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


def news():
    for page in range(1, 2):
        headers = {
            'authority': 'bdfa.gov.bn',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'zh-CN,zh;q=0.9',
            # 'cookie': '_ga=GA1.1.1215510926.1748323882; _ga_Y8ELNQKD2L=GS2.1.s1748323881$o1$g1$t1748324501$j0$l0$h0',
            'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        }

        response = requests.get(f'https://bdfa.gov.bn/news/page/{page}', headers=headers)
        res_text = html.unescape(response.text)
        print(res_text)

        res_html = etree.HTML(res_text)

        article_list = res_html.xpath('//div[@id="posts-container"]/div/article')
        print(len(article_list))

        for article in article_list:
            article_id = article.xpath('./@id')[0].strip()
            # print(article_id)
            # continue
            title = article.xpath('.//h2[@class="entry-title fusion-post-title"]/a/text()')[0].strip()
            detail_url = article.xpath('.//h2[@class="entry-title fusion-post-title"]/a/@href')[0].strip()

            # detail_url = urllib.parse.urljoin("https://www.cbsa-asfc.gc.ca/publications", detail_link[0])
            updateTime = article.xpath('.//span[@class="updated rich-snippet-hidden"]/text()')[0].strip().split("T")[0]
            logger.info(f'{updateTime} -- {detail_url} -- {title}')
            # continue
            #
            time.sleep(2)
            detail_res = requests.get(url=detail_url, headers=headers)
            detail_res_text = html.unescape(detail_res.text)
            # print(detail_res_text)
            detail_res_html = etree.HTML(detail_res_text)
            #
            # publishTime = detail_res_html.xpath('//time[1]/@datetime')[0]
            # print(publishTime, title)
            soup = BeautifulSoup(detail_res_text, 'html.parser')
            # # 将BeautifulSoup对象转换为字符串
            # mainContentOfPage = soup.find(name='main', attrs={'property': 'mainContentOfPage'})
            content_str = str(soup.find(name='div', attrs={'class': 'post-content'}))
            data = {
                "_id": detail_url,
                "标题": title,
                "网站发布时间": updateTime,
                "文章地址URL": detail_url,
                "采集源名称": "食品局",
                "正文": content_str,
                "HTML": detail_res_text,
                "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": 0,
                "平台形式": "网站",
                "数据类型": "法规"
            }
            # print(json.dumps(data, ensure_ascii=False))
            save_articles(data)
            # return


if __name__ == '__main__':
    # news()

    # get_page1()

    legislations()
    # metrics.close()
    # MongoClient.close()
