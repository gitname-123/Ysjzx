import hashlib
import html
import json
import re
import urllib
from pathlib import Path

import requests
import time
import warnings
from bs4 import BeautifulSoup
from pymongo.errors import DuplicateKeyError

warnings.filterwarnings("ignore")
from datetime import datetime
from loguru import logger
from lxml import etree
import sys
sys.path.append('../')
from tools.get_proxy import get_proxies
from tools.settings import mengniu_data_original_col, MongoClient, today
import subprocess
from functools import partial
subprocess.Popen = partial(subprocess.Popen, encoding='utf-8')
# from feapder.utils import metrics
import ddddocr


# url_set = set()
class OpenStdSamrGov(object):

    def __init__(self):
        self.detailNo = None
        self.implementDate = None
        self.publishTime = None
        self.standardNo = None
        self.validStatus = None
        self.column_domain = None
        self.page = None
        self.detailUrl = None
        self.title = None
        self.column = None

    def scheduler(self):
        column_list = [
            ("1", "国家标准全文公开系统", "强制性国家标准"),
            ("2", "国家标准全文公开系统", "推荐性国家标准"),
            ("3", "国家标准全文公开系统", "指导性技术文件")
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
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',

            }
            try:
                logger.info(f'处理列表页：{self.column[2]} -- {self.page}')
                params = {
                    # 'r': '0.6676413040804456',
                    'page': f'{self.page}',
                    'pageSize': '10',
                    'p.p1': f'{self.column_domain}',
                    'p.p90': 'circulation_date',
                    'p.p91': 'desc',
                }
                response = requests.get(
                    'https://openstd.samr.gov.cn/bzgk/gb/std_list_type',
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

                response_html = etree.HTML(response.text)
                tr_list = response_html.xpath('//table[@class="table result_list table-striped table-hover"]/tbody[2]/tr')
                if not tr_list:
                    logger.info(f'列表页没 tr  -- 程序结束 --- {response.text}')
                    return
                logger.info(f'{self.column[2]} -- {self.page} -- 列表页数量：{len(tr_list)}')
                # return
                for tr in tr_list:
                    self.standardNo = tr.xpath('./td[2]/a/text()')[0].strip()
                    self.title = tr.xpath('./td[4]/a/text()')[0].strip()
                    self.detailNo = re.findall(r"showInfo\('([A-Z0-9]{32})'\);", tr.xpath('./td[4]/a/@onclick')[0].strip())[0]
                    self.detailUrl = f'https://openstd.samr.gov.cn/bzgk/gb/newGbInfo?hcno={self.detailNo}'
                    self.validStatus = tr.xpath('./td[5]/span/text()')[0].strip()
                    self.publishTime = tr.xpath('./td[6]/text()')[0].strip()
                    self.implementDate = tr.xpath('./td[7]/text()')[0].strip()
                    logger.info(f'{self.publishTime} -- {self.implementDate} -- {self.detailUrl} -- {self.validStatus} -- {self.title}')

                    if self.publishTime < "2024-01-01":
                        logger.info(f'只采集近一年的数据：{self.publishTime}')
                        return

                    find_detail_url = mengniu_data_original_col.find_one({"_id": self.detailUrl})
                    if find_detail_url:
                        if self.validStatus == find_detail_url["B_标准状态"]:
                            # logger.info(f'已经采集过 且内容无变化： {self.publish_time}, {self.detail_url}, {self.title}')
                            continue
                        else:
                            logger.info(f'已经采集过 内容有变 需要更新: {self.publishTime}, {self.detailUrl}, title: {self.title}, 新状态: {self.validStatus} :: 原状态：{find_detail_url["B_标准状态"]}')
                        # mengniu_data_original_col.update_one({"_id": self.detail_url}, {"$set": {"标题": self.title, "B_标准名称": self.title, "B_标准状态": self.F_有效性状态}})
                        # return
                    #     return
                    # return
                    self.get_detail()
                    # return
                self.page += 1
                # return

    def get_detail(self):
        logger.info(f'process detail: {self.detailUrl} --- {self.title}')
        while True:
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Language': 'zh-CN,zh;q=0.9',
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
                # print(response.text)
                # return
                response_html = etree.HTML(response.text)

                publisher_xpath = response_html.xpath('//div[contains(text(), "发布单位")]/following-sibling::div[1]/text()')
                publisher = publisher_xpath[0].strip() if publisher_xpath else ""
                attr_list = []
                if response.text.__contains__("下载标准"):
                    fileName, filePath = self.get_pdf()
                    attr_list.append({"fileName": fileName, "filePath": filePath})
                else:
                    logger.info(f'这个标准没有附件：{self.detailUrl} --- {self.title}')
                data = {
                    "_id": self.detailUrl,
                    "标题": self.title,
                    "网站发布时间": self.publishTime,
                    "文章地址URL": self.detailUrl,
                    "采集源名称": self.column[1],
                    "正文": "",
                    "HTML": response.text,
                    "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": 0,
                    "平台形式": "网站",
                    "数据类型": "标准",
                    "B_标准编号": self.standardNo,
                    "B_标准名称": self.title,
                    "B_标准类别": "国家标准",
                    "B_发布日期": self.publishTime,
                    "B_标准状态": self.validStatus,
                    "B_实施日期": self.implementDate,
                    "B_颁发部门": publisher,
                    # "B_废止日期": B_废止日期,
                    # "B_标准介绍": B_标准介绍
                    "附件": json.dumps(attr_list, ensure_ascii=False)
                }
                if save_articles(data):
                    # metrics.emit_counter("详情页采集量", count=1, classify=f"{self.column[2]}")
                    pass
                # print(json.dumps(data, ensure_ascii=False))
                return

    # 下载附件 数英验证码  获取验证码并识别
    def get_pdf(self):
        logger.info(f'开始下载附件')
        session = requests.Session()
        time_out_flag = False
        # 1. 创建DdddOcr对象
        ocr = ddddocr.DdddOcr(show_ad=False)
        retry = 0
        while retry < 5:
            try:
                if not time_out_flag:
                    proxies = get_proxies()
                    session.proxies = proxies
                else:
                    session.proxies = ""
                # 初次请求pdf
                pdf_url = f"http://c.gb688.cn/bzgk/gb/showGb?type=download&hcno={self.detailNo}"
                headers = {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "Host": "c.gb688.cn",
                    "Referer": f"http://c.gb688.cn/bzgk/gb/showGb?type=download&hcno={self.detailNo}",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                    # "cookie": "td_cookie=3453460512; JSESSIONID=A9E179E636743D501F0B754218320C9E"
                }
                pdf_res = session.get(url=pdf_url, headers=headers, timeout=10)

                captcha_url = f'http://c.gb688.cn/bzgk/gb/gc?_{int(time.time() * 1000)}'
                headers = {
                    # "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
                    "Host": "c.gb688.cn",
                    "Referer": f"http://c.gb688.cn/bzgk/gb/showGb?type=download&hcno={self.detailNo}",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                    # "cookie": "td_cookie=3453460512a"
                }

                pic_res = session.get(url=captcha_url, headers=headers, timeout=10)
                # session.cookies = pic_res.cookies
                # print(pic_res.content)
                # print(pic_res.status_code)
                # print(pic_res.cookies)

                with open('./gc.jpg', 'wb') as f:
                    f.write(pic_res.content)

                #
                # # 2. 读取图片
                # with open('./gc.jpg', 'rb') as f:
                #     img = f.read()

                # 3. 识别图片内验证码并返回字符串
                verifyCode = ocr.classification(pic_res.content)
                logger.info(f"识别结果：{verifyCode}")

                # 验证验证码
                verify_url = "http://c.gb688.cn/bzgk/gb/verifyCode"
                data = {
                    "verifyCode": verifyCode
                }
                verify_res = session.post(url=verify_url, headers=headers, data=data, timeout=10)
                logger.info(f"验证结果：{verify_res.text}")
                if verify_res.text.__contains__("error"):
                    logger.error(f'验证失败，重试一次')
                    retry += 1
                    time.sleep(2)
                    continue
                # 下载pdf
                pdf_url = f"http://c.gb688.cn/bzgk/gb/viewGb?hcno={self.detailNo}"
                headers = {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "Host": "c.gb688.cn",
                    "Referer": f"http://c.gb688.cn/bzgk/gb/showGb?type=download&hcno={self.detailNo}",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                    # "cookie": "td_cookie=3453460512; JSESSIONID=A9E179E636743D501F0B754218320C9E"
                }
                pdf_res = session.get(url=pdf_url, headers=headers, timeout=10)
                # print(pdf_res.text)
                # print(pdf_res.status_code)
                logger.info(pdf_res.headers)
                filename = re.findall('filename=(.*?)\'', str(pdf_res.headers))[0]
                # logger.info(f'filename: {filename}')
                dir_path = f'../attachments/{today.replace("-", "")}/website_attachments'
                Path(dir_path).mkdir(parents=True, exist_ok=True)
                filePath = f'''{dir_path}/{hashlib.md5(f'{self.detailUrl}{filename.split(".")[0]}'.encode('utf-8')).hexdigest()}.{filename.split(".")[-1]}'''
                # logger.info(f'filePath: {filePath}')
                with open(filePath, 'wb') as f:
                    f.write(pdf_res.content)
                filePath = filePath.replace('../', './')
                session.close()
                logger.success(f'附件下载成功：{filename}, {filePath}')
                return filename, filePath
            except Exception as e:
                logger.error(f'下载pdf error：{e}')
                if str(e).__contains__("timed out"):
                    time_out_flag = True
                    logger.error(f'time out 换本机ip重试')
                retry += 1
                time.sleep(2)
                continue
        else:
            logger.error(f'下载PDF {retry}次都失败了')
            time.sleep(10000)

def save_articles(doc):
    try:
        mengniu_data_original_col.insert_one(doc)
    except DuplicateKeyError:
        # logger.info("article 已存入该条数据:{}".format(doc["_id"]))
        mengniu_data_original_col.update_one({"_id": doc["_id"]}, {"$set": doc})
        logger.success("article 更新成功:{}".format(doc["_id"]))
        return True
    except Exception as e:
        logger.error("article db error:{} -- {}".format(e, doc["_id"]))
        return False
    else:
        logger.success("article 采集成功:{}".format(doc["_id"]))
        return True


def test_detail():
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        # 'Cache-Control': 'max-age=0',
        # 'Connection': 'keep-alive',
        # 'Cookie': 'Hm_lvt_50758913e6f0dfc9deacbfebce3637e4=1745397818; HMACCOUNT=5E3DCAD3DF824D60; Hm_lpvt_50758913e6f0dfc9deacbfebce3637e4=1745399366; JSESSIONID=14AFE8EADD0920427BB582E580069751; Hm_lvt_54db9897e5a65f7a7b00359d86015d8d=1742278119; Hm_lvt_50758913e6f0dfc9deacbfebce3637e4=1745397818,1745399010; Hm_lpvt_50758913e6f0dfc9deacbfebce3637e4=1745399010; HMACCOUNT=5E3DCAD3DF824D60',
        # 'Referer': 'https://openstd.samr.gov.cn/bzgk/gb/std_list_type?r=0.6676413040804456&page=2&pageSize=10&p.p1=1&p.p90=circulation_date&p.p91=desc',
        # 'Sec-Fetch-Dest': 'document',
        # 'Sec-Fetch-Mode': 'navigate',
        # 'Sec-Fetch-Site': 'same-origin',
        # 'Sec-Fetch-User': '?1',
        # 'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        # 'sec-ch-ua': '"Chromium";v="109", "Not_A Brand";v="99"',
        # 'sec-ch-ua-mobile': '?0',
        # 'sec-ch-ua-platform': '"Windows"',
    }

    params = {
        'hcno': '71D054118B5AD7FDAF8F83BCEDA0DA81',
    }
    response = requests.get(
        'https://openstd.samr.gov.cn/bzgk/gb/newGbInfo',
        proxies=get_proxies(),
        headers=headers,
        params=params,
    )
    print(response.text)
    print(response.status_code)


def test_list():
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        # 'Connection': 'keep-alive',
        # 'Cookie': 'Hm_lvt_50758913e6f0dfc9deacbfebce3637e4=1745397818; HMACCOUNT=5E3DCAD3DF824D60; Hm_lpvt_50758913e6f0dfc9deacbfebce3637e4=1745398225; JSESSIONID=14AFE8EADD0920427BB582E580069751; Hm_lvt_54db9897e5a65f7a7b00359d86015d8d=1742278119',
        # 'Referer': 'https://openstd.samr.gov.cn/bzgk/gb/std_list_type?p.p1=1&p.p90=circulation_date&p.p91=desc',
        # 'Sec-Fetch-Dest': 'document',
        # 'Sec-Fetch-Mode': 'navigate',
        # 'Sec-Fetch-Site': 'same-origin',
        # 'Sec-Fetch-User': '?1',
        # 'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        # 'sec-ch-ua': '"Chromium";v="109", "Not_A Brand";v="99"',
        # 'sec-ch-ua-mobile': '?0',
        # 'sec-ch-ua-platform': '"Windows"',
    }

    params = {
        # 'r': '0.6676413040804456',
        'page': '2',
        'pageSize': '10',
        'p.p1': '1',
        'p.p90': 'circulation_date',
        'p.p91': 'desc',
    }
    response = requests.get(
        'https://openstd.samr.gov.cn/bzgk/gb/std_list_type',
        params=params,
        proxies=get_proxies(),
        headers=headers,
    )
    print(response.text)
    print(response.status_code)


# 下载附件 数英验证码  获取验证码并识别
def get_captcha():
    proxies = get_proxies()
    session = requests.Session()
    session.proxies = proxies

    #
    # # 下载pdf
    # pdf_url = "http://c.gb688.cn/bzgk/gb/showGb?type=download&hcno=77D340458DC2306E0FCBBBC5A2766BF8"
    # headers = {
    #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    #     "Host": "c.gb688.cn",
    #     "Referer": "https://openstd.samr.gov.cn/",
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    #     # "cookie": "td_cookie=3453460512; JSESSIONID=A9E179E636743D501F0B754218320C9E"
    # }
    # pdf_res = session.get(url=pdf_url, headers=headers)
    # print(pdf_res.status_code)
    #
    # 下载pdf
    pdf_url = "http://c.gb688.cn/bzgk/gb/showGb?type=download&hcno=2B5FB91F00A1C10AE3750A6DEF40C749"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Host": "c.gb688.cn",
        "Referer": "http://c.gb688.cn/bzgk/gb/showGb?type=download&hcno=2B5FB91F00A1C10AE3750A6DEF40C749",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        # "cookie": "td_cookie=3453460512; JSESSIONID=A9E179E636743D501F0B754218320C9E"
    }
    pdf_res = session.get(url=pdf_url, headers=headers)
    # print(pdf_res.status_code)

    captcha_url = f'http://c.gb688.cn/bzgk/gb/gc?_{int(time.time() * 1000)}'
    headers = {
        # "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "Host": "c.gb688.cn",
        "Referer": "http://c.gb688.cn/bzgk/gb/showGb?type=download&hcno=2B5FB91F00A1C10AE3750A6DEF40C749",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        # "cookie": "td_cookie=3453460512a"
    }
    pic_res = session.get(url=captcha_url, headers=headers, timeout=10)
    # session.cookies = pic_res.cookies
    print(pic_res.content)
    print(pic_res.status_code)
    print(pic_res.cookies)

    with open('./gc.jpg', 'wb') as f:
        f.write(pic_res.content)


    # start = time.time()  # 开始时间

    # 1. 创建DdddOcr对象
    ocr = ddddocr.DdddOcr(show_ad=False)
    #
    # # 2. 读取图片
    # with open('./gc.jpg', 'rb') as f:
    #     img = f.read()

    # 3. 识别图片内验证码并返回字符串
    verifyCode = ocr.classification(pic_res.content)
    print("识别结果：", verifyCode)

    # end = time.time()
    # print("耗时：%s 秒" % str(start - end))

    # 验证验证码
    verify_url = "http://c.gb688.cn/bzgk/gb/verifyCode"
    data = {
        "verifyCode": verifyCode
    }
    verify_res = session.post(url=verify_url, headers=headers, data=data, timeout=10)
    print(verify_res.text)

    # # 下载pdf
    # pdf_url = "http://c.gb688.cn/bzgk/gb/url"
    # headers = {
    #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    #     "Host": "c.gb688.cn",
    #     "Referer": "http://c.gb688.cn/bzgk/gb/showGb?type=download&hcno=77D340458DC2306E0FCBBBC5A2766BF8",
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    #     # "cookie": "td_cookie=3453460512; JSESSIONID=A9E179E636743D501F0B754218320C9E"
    # }
    # pdf_res = session.get(url=pdf_url, headers=headers)
    # # print(pdf_res.text)
    # print(pdf_res.status_code)


    # 下载pdf
    pdf_url = "http://c.gb688.cn/bzgk/gb/viewGb?hcno=2B5FB91F00A1C10AE3750A6DEF40C749"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Host": "c.gb688.cn",
        "Referer": "http://c.gb688.cn/bzgk/gb/showGb?type=download&hcno=2B5FB91F00A1C10AE3750A6DEF40C749",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        # "cookie": "td_cookie=3453460512; JSESSIONID=A9E179E636743D501F0B754218320C9E"
    }
    pdf_res = session.get(url=pdf_url, headers=headers, timeout=10)
    print(pdf_res.text)
    print(pdf_res.status_code)
    print(pdf_res.headers)
    filename = re.findall('filename=(.*?)\'', str(pdf_res.headers))[0]

    with open(f'./{filename}', 'wb') as f:
        f.write(pdf_res.content)



if __name__ == '__main__':
    # metrics.init()
    #
    obj = OpenStdSamrGov()
    obj.scheduler()
    # test_list()

    # test_detail()
    # metrics.close()

    # get_captcha()

    MongoClient.close()
