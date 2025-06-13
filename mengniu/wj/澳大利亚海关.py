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



def get_page2():
    headers = {
        'Accept': 'application/json;odata=verbose',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        # 'Cookie': 'monsido=13C1748236386887; _ga=GA1.1.70691151.1748236387; WSS_FullScreenMode=false; _ga_SMECKNEEVP=GS2.1.s1748243698$o2$g1$t1748244250$j0$l0$h0',
        'Origin': 'https://www.abf.gov.au',
        'Referer': 'https://www.abf.gov.au/importing-exporting-and-manufacturing/trade-and-goods-compliance/goods-compliance-update',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        # 'X-RequestDigest': '0x22FC3B22914F399BA81725E9C6C016A034A15590E0F161B4071CFB22D686AA0DCD3EEB5D71E85663B0A4CD924945D747FD438033E8038761D3AE37DA0CA6AF9B,26 May 2025 07:20:02 -0000',
        'sec-ch-ua': '"Chromium";v="109", "Not_A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    json_data = {
        'webUrl': '/trade-and-goods-compliance-subsite',
        'libraryName': 'ComplianceNewsletters',
    }

    response = requests.post(
        'https://www.abf.gov.au/_layouts/15/api/Data.aspx/GetPDFForms',
        # cookies=cookies,
        headers=headers,
        json=json_data,
        proxies=get_proxies(),
        timeout=10
    )
    print(response.text)
    print(response.status_code)

    res_dict = json.loads(response.text)

    data = res_dict['d']['data'][-1]
    name = data['name']
    title = data['title']
    if title:
        # 客户需求
        title = title + " -- A newsletter for industry on the ABF’s national goods compliance program and the application of trade and customs laws."
    else:
        logger.error(f'没获取到title')

    description = data['description']
    print(description)
    updated = datetime.strptime(data['updated'], '%d/%m/%Y').strftime('%Y-%m-%d')

    description_html = etree.HTML(description)

    content_div = description_html.xpath('//div[@class="col-sm-3"]')
    content_str = html.unescape(etree.tostring(content_div[0], encoding="utf-8").decode())
    pdf_link = urllib.parse.urljoin("https://www.abf.gov.au/", content_div[1].xpath('./a/@href')[0])
    print(title, pdf_link)
    print(content_str)

    data = {
        "_id": f"https://www.abf.gov.au/importing-exporting-and-manufacturing/trade-and-goods-compliance/goods-compliance-update#{name}",
        "标题": title,
        "网站发布时间": updated,
        "文章地址URL": f"https://www.abf.gov.au/importing-exporting-and-manufacturing/trade-and-goods-compliance/goods-compliance-update#{name}",
        "采集源名称": "海关",
        "正文": content_str,
        "HTML": response.text,
        "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": 0,
        "平台形式": "网站",
        "数据类型": "法规",
        "附件": json.dumps([{"fileName": f'{name}.pdf', "fileLink": pdf_link}])
    }
    print(json.dumps(data))
    save_articles(data)

if __name__ == '__main__':

    get_page2()
    metrics.close()
    MongoClient.close()
