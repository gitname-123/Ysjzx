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


class ttbzOrg(object):

    def __init__(self):
        self.session = None
        self.detailNo = None
        # self.implementDate = None
        # self.publishTime = None
        self.standardNo = None
        self.validStatus = None
        self.column_domain = None
        self.page = None
        self.detailUrl = None
        self.title = None
        self.column = None

    def scheduler(self):
        self.page = 1
        while True:
            try:
                if self.page > 10:
                    logger.info(f'处理完成 page {self.page}')
                    return
                logger.info(f'处理列表页： {self.page}')
                session = requests.Session()
                session.proxies = get_proxies()
                headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    # 'Connection': 'keep-alive',
                    # 'Cookie': 'ASP.NET_SessionId=sxfr03ususptf3ue14uvfsbz; __51cke__=; __51vcke__undefined=d18597d1-b8f5-5474-be1c-0274eaef4893; __51vuft__undefined=1747640053907; __jsluid_s=5d2c8c7ee29e18716df1f6d39ef0d0b2; __51uvsct__undefined=2; _d_id=3f259a251486099b285a37800b4431; __tins__18926186=%7B%22sid%22%3A%201747643142023%2C%20%22vd%22%3A%204%2C%20%22expires%22%3A%201747645040002%7D; __51laig__=8; __vtins__undefined=%7B%22sid%22%3A%20%22ab7496e7-07e1-5e8b-9127-b985c4ea9a87%22%2C%20%22vd%22%3A%204%2C%20%22stt%22%3A%2097874%2C%20%22dr%22%3A%205270%2C%20%22expires%22%3A%201747645040163%2C%20%22ct%22%3A%201747643240163%7D',
                    # 'Referer': 'https://www.ttbz.org.cn/Home/Standard/?CNL1Code=A',
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
                params = {
                    'CNL1Code': 'A',
                    'page': f'{self.page}',
                }
                response = session.get(
                    url='https://www.ttbz.org.cn/Home/Standard/',
                    params=params,
                    headers=headers,
                    timeout=10
                )
                headers = {
                    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Connection': 'keep-alive',
                    # 'Cookie': 'ASP.NET_SessionId=sxfr03ususptf3ue14uvfsbz; __51cke__=; __51vcke__undefined=d18597d1-b8f5-5474-be1c-0274eaef4893; __51vuft__undefined=1747640053907; __jsluid_s=5d2c8c7ee29e18716df1f6d39ef0d0b2; __51uvsct__undefined=2; __tins__18926186=%7B%22sid%22%3A%201747643142023%2C%20%22vd%22%3A%204%2C%20%22expires%22%3A%201747645040002%7D; __51laig__=8; __vtins__undefined=%7B%22sid%22%3A%20%22ab7496e7-07e1-5e8b-9127-b985c4ea9a87%22%2C%20%22vd%22%3A%204%2C%20%22stt%22%3A%2097874%2C%20%22dr%22%3A%205270%2C%20%22expires%22%3A%201747645040163%2C%20%22ct%22%3A%201747643240163%7D; _d_id=3f749a14456c8f4545b837800b4431',
                    'Referer': f'https://www.ttbz.org.cn/Home/Standard/?CNL1Code=A&page={self.page}',
                    'Sec-Fetch-Dest': 'image',
                    'Sec-Fetch-Mode': 'no-cors',
                    'Sec-Fetch-Site': 'same-origin',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
                    'sec-ch-ua': '"Chromium";v="109", "Not_A Brand";v="99"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                }
                response = session.get(
                    url='https://www.ttbz.org.cn/ValidCode/PageLoginVCode',
                    headers=headers,
                    timeout=10
                )
                # print(response.text)
                # print(response.status_code)
                with open('./PageLoginVCode.gif', 'wb') as f:
                    f.write(response.content)
                # 1. 创建DdddOcr对象
                ocr = ddddocr.DdddOcr(show_ad=False)
                #
                # # 2. 读取图片
                # with open('./gc.jpg', 'rb') as f:
                #     img = f.read()

                # 3. 识别图片内验证码并返回字符串
                verifyCode = ocr.classification(response.content)
                logger.info(f"识别结果：{verifyCode}")

                headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Connection': 'keep-alive',
                    # 'Cookie': 'ASP.NET_SessionId=sxfr03ususptf3ue14uvfsbz; __51cke__=; __51vcke__undefined=d18597d1-b8f5-5474-be1c-0274eaef4893; __51vuft__undefined=1747640053907; __jsluid_s=5d2c8c7ee29e18716df1f6d39ef0d0b2; __51uvsct__undefined=2; __tins__18926186=%7B%22sid%22%3A%201747643142023%2C%20%22vd%22%3A%205%2C%20%22expires%22%3A%201747645044930%7D; __51laig__=9; _d_id=3f799a251486173fa9983780478d31; __vtins__undefined=%7B%22sid%22%3A%20%22ab7496e7-07e1-5e8b-9127-b985c4ea9a87%22%2C%20%22vd%22%3A%205%2C%20%22stt%22%3A%20102783%2C%20%22dr%22%3A%204909%2C%20%22expires%22%3A%201747645045072%2C%20%22ct%22%3A%201747643245072%7D',
                    'Referer': f'https://www.ttbz.org.cn/Home/Standard/?CNL1Code=A&page={self.page}',
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
                params = {
                    'ps': '100',
                    'searchType': '',
                    'key': '',
                    'enTitle': '',
                    'stNo': '',
                    'stName': '',
                    'orgCode': '',
                    'orgName': '',
                    'stStatus': '',
                    'stSale': '',
                    'CNL1Code': 'A',
                    'CNL2Code': '',
                    'CNL3Code': '',
                    'ENL1Code': '',
                    'ENL2Code': '',
                    'ENL3Code': '',
                    'stOpen': '',
                    'pcode': verifyCode,
                    'page': f'{self.page}',
                }
                response = session.get(
                    url='https://www.ttbz.org.cn/Home/Standard',
                    params=params,
                    headers=headers,
                    timeout=10
                )
                # print(response.text)
                # print(response.status_code)

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

                tr_list = response_html.xpath('//table[@class="standard_list_table"][1]/tr')
                if len(tr_list) < 2:
                    logger.info(f'列表页没 tr  -- 不应该 -- 重试')   #  --- {response.text}
                    time.sleep(5)
                    continue
                logger.info(f'{self.page} -- 列表页数量：{len(tr_list)}')

                for tr in tr_list[1:]:
                    self.standardNo = tr.xpath('./td[3]/text()')[0].strip()
                    self.title = tr.xpath('./td[4]/text()')[0].strip()
                    # self.detailNo = re.findall(r"showInfo\('([A-Z0-9]{32})'\);", tr.xpath('./td[7]/a/@href')[0].strip())[0]
                    self.detailUrl = f'https://www.ttbz.org.cn{tr.xpath("./td[7]/a/@href")[0]}'
                    self.validStatus = tr.xpath('./td[6]/text()')[0].strip()
                    publishTime = tr.xpath('./td[5]/text()')[0].strip()
                    # self.implementDate = tr.xpath('./td[7]/text()')[0].strip()
                    logger.info(f'{publishTime} -- {self.detailUrl} -- {self.validStatus} -- {self.title}')

                    if publishTime < "2024-01-01":
                        logger.info(f'只采集近一年的数据：{publishTime}')
                        return
                    #
                    find_detail_url = mengniu_data_original_col.find_one({"_id": self.detailUrl})
                    if find_detail_url:
                        find_detail_url = mengniu_data_original_col.find_one({"_id": self.detailUrl})
                        if find_detail_url:
                            logger.info(f'已经采集过：{self.detailUrl}, {self.title}')
                            continue
                        # if self.validStatus == find_detail_url["B_标准状态"]:
                        #     logger.info(f'已经采集过 且内容无变化： {self.publish_time}, {self.detail_url}, {self.title}')
                        #     continue
                        # else:
                        #     logger.info(f'已经采集过 内容有变 需要更新: {self.publishTime}, {self.detailUrl}, title: {self.title}, 新状态: {self.validStatus} :: 原状态：{find_detail_url["B_标准状态"]}')
                        # # mengniu_data_original_col.update_one({"_id": self.detail_url}, {"$set": {"标题": self.title, "B_标准名称": self.title, "B_标准状态": self.F_有效性状态}})
                        # # return
                    self.get_detail()
                    # return
                self.page += 1
                # return



    def get_detail(self):
        # logger.info(f'process detail: {self.detailUrl} --- {self.title}')
        while True:
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            }
            try:
                # time.sleep(1)
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
                response_html = etree.HTML(response.text)

                publisher_xpath = response_html.xpath('//td[contains(text(), "起草单位")]/following-sibling::td[1]/span/text()')
                publisher = publisher_xpath[0].strip() if publisher_xpath else ""

                publishTime = response_html.xpath('//td[contains(text(), "发布日期")]/following-sibling::td[1]/span/text()')[0].strip().replace("年", "-").replace("月", "-").replace("日", "")

                implementDate_xpath = response_html.xpath('//td[contains(text(), "实施日期")]/following-sibling::td[1]/span/text()')
                implementDate = implementDate_xpath[0].strip().replace("年", "-").replace("月", "-").replace("日", "") if implementDate_xpath else ""

                print(publisher, publishTime, implementDate)
                attr_list = []

                # 标准文本
                standard_pdf_xpath = response_html.xpath('//td[contains(text(), "标准文本")]/following-sibling::td[1]/span/a/@href')
                if standard_pdf_xpath:
                    standard_pdf_viewUrl = urllib.parse.urljoin(self.detailUrl, standard_pdf_xpath[0])
                    fileName = f"{self.standardNo}.pdf"
                    filePath = self.get_pdf(standard_pdf_viewUrl, fileName)
                    attr_list.append({"fileName": fileName, "filePath": filePath})
                else:
                    logger.info(f'这个标准文本未公开：{self.detailUrl} --- {self.title}')

                # 标准公告
                Announcement_pdf_xpath = response_html.xpath('//td/a[contains(text(), "标准发布公告")]/@href')
                if Announcement_pdf_xpath:
                    Announcement_pdf_viewUrl = urllib.parse.urljoin(self.detailUrl, Announcement_pdf_xpath[0])
                    fileName = "标准发布公告.pdf"
                    filePath = self.get_pdf(Announcement_pdf_viewUrl, fileName)
                    attr_list.append({"fileName": fileName, "filePath": filePath})
                else:
                    logger.info(f'这个标准没有发布公告：{self.detailUrl} --- {self.title}')

                data = {
                    "_id": self.detailUrl,
                    "标题": self.title,
                    "网站发布时间": publishTime,
                    "文章地址URL": self.detailUrl,
                    "采集源名称": "全国团体标准信息平台",
                    "正文": "",
                    "HTML": response.text,
                    "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": 0,
                    "平台形式": "网站",
                    "数据类型": "标准",
                    "B_标准编号": self.standardNo,
                    "B_标准名称": self.title,
                    "B_标准类别": "团体标准",
                    "B_发布日期": publishTime,
                    "B_标准状态": self.validStatus,
                    "B_实施日期": implementDate,
                    "B_颁发部门": publisher,
                    # "B_废止日期": B_废止日期,
                    # "B_标准介绍": B_标准介绍
                    "附件": json.dumps(attr_list, ensure_ascii=False)
                }
                if save_articles(data):
                    # metrics.emit_counter("详情页采集量", count=1, classify="全国团体标准信息平台")
                    pass
                # print(json.dumps(data, ensure_ascii=False))
                return

    # 下载附件 数英验证码  获取验证码并识别
    def get_pdf(self, viewUrl, filename):
        logger.info(f'开始下载附件:{filename}')
        retry = 0
        session = requests.Session()
        while retry < 5:
            try:
                session.proxies = get_proxies()
                # 初次请求pdf
                headers = {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "Host": "www.ttbz.org.cn",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                    # "": "td_cookie=3453460512; JSESSIONID=A9E179E636743D501F0B754218320C9E"
                }
                view_pdf_res = session.get(url=viewUrl, headers=headers, timeout=10, verify=False)
                if view_pdf_res.status_code != 200:
                    logger.error(f'status_code != 200: {view_pdf_res.status_code} --- {view_pdf_res.text}')
                    time.sleep(100)
                    continue
                pdf_params = re.findall('PdfFileStreamGet/(.*?)&rnd', view_pdf_res.text)
                if pdf_params:
                    down_pdf_url = f"https://www.ttbz.org.cn/Home/PdfFileStreamGet/{pdf_params[0]}?rand={int(time.time() * 1000)}"
                    logger.info(f'down_pdf_url: {down_pdf_url}')
                else:
                    logger.error(f'没提取到pdf关键参数：{view_pdf_res.text}')
                    time.sleep(100)
                    continue
                headers = {
                    # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    # "Host": "c.gb688.cn",
                    # "Referer": viewUrl,
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                    # "cookie": "td_cookie=3453460512; JSESSIONID=A9E179E636743D501F0B754218320C9E"
                }
                pdf_res = session.get(url=down_pdf_url, headers=headers, timeout=10, verify=False)
                # pdf_res.encoding = "utf-8"
                # print(pdf_res.text)
                # print(pdf_res.status_code)
                logger.info(pdf_res.headers)
                # filename = re.findall('filename=(.*?)\'', str(pdf_res.headers))[0]
                # logger.info(f'filename: {filename}')
                if not pdf_res.text.__contains__("%PDF"):
                    logger.error(pdf_res.text)
                    logger.error(f'pdf返回异常')
                    time.sleep(100000)
                dir_path = f'../attachments/{today.replace("-", "")}/website_attachments'
                Path(dir_path).mkdir(parents=True, exist_ok=True)
                filePath = f'''{dir_path}/{hashlib.md5(f'{self.detailUrl}{filename.split(".")[0]}'.encode('utf-8')).hexdigest()}.{filename.split(".")[-1]}'''
                # logger.info(f'filePath: {filePath}')
                with open(filePath, 'wb') as f:
                    f.write(pdf_res.content)
                filePath = filePath.replace('../', './')

                logger.success(f'附件下载成功：{filename}, {filePath}')
                return filePath
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
            time.sleep(100)


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


def test_captcha():
    cookies = {
        '__51cke__': '',
        '__51uvsct__undefined': '1',
        '__51vcke__undefined': '711df26e-c8e6-507a-8c8f-75a0ec65beaf',
        '__51vuft__undefined': '1747017822263',
        'cckf_track_830188_LastActiveTime': '1747017834',
        'CCKF_visitor_id_830188': '1405169801',
        'cckf_track_830188_AutoInviteNumber': '0',
        'cckf_track_830188_ManualInviteNumber': '0',
        '__jsluid_s': '5f136789cda34b24a45b3943fc4412a2',
        'ASP.NET_SessionId': '01pst32k1ygtl5ulf3jfoclc',
        '__tins__18926186': '%7B%22sid%22%3A%201747019717019%2C%20%22vd%22%3A%205%2C%20%22expires%22%3A%201747021981951%7D',
        '__51laig__': '22',
        '__vtins__undefined': '%7B%22sid%22%3A%20%22dfb7503a-e28c-5f36-a463-8d812b6a4df2%22%2C%20%22vd%22%3A%2022%2C%20%22stt%22%3A%202360246%2C%20%22dr%22%3A%20392656%2C%20%22expires%22%3A%201747021982506%2C%20%22ct%22%3A%201747020182506%7D',
        '_d_id': 'ed65a114456c813bd80937807f03e3',
    }

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        # 'Cookie': '__51cke__=; __51uvsct__undefined=1; __51vcke__undefined=711df26e-c8e6-507a-8c8f-75a0ec65beaf; __51vuft__undefined=1747017822263; cckf_track_830188_LastActiveTime=1747017834; CCKF_visitor_id_830188=1405169801; cckf_track_830188_AutoInviteNumber=0; cckf_track_830188_ManualInviteNumber=0; __jsluid_s=5f136789cda34b24a45b3943fc4412a2; ASP.NET_SessionId=01pst32k1ygtl5ulf3jfoclc; __tins__18926186=%7B%22sid%22%3A%201747019717019%2C%20%22vd%22%3A%205%2C%20%22expires%22%3A%201747021981951%7D; __51laig__=22; __vtins__undefined=%7B%22sid%22%3A%20%22dfb7503a-e28c-5f36-a463-8d812b6a4df2%22%2C%20%22vd%22%3A%2022%2C%20%22stt%22%3A%202360246%2C%20%22dr%22%3A%20392656%2C%20%22expires%22%3A%201747021982506%2C%20%22ct%22%3A%201747020182506%7D; _d_id=ed65a114456c813bd80937807f03e3',
        'Referer': 'https://www.ttbz.org.cn/Home/Standard/?CNL1Code=A',
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

    response = requests.get('https://www.ttbz.org.cn/ValidCode/PageLoginVCode',
                            cookies=cookies,
                            headers=headers,
                            # proxies=get_proxies()
                            )
    print(response.text)
    print(response.status_code)

    with open('./PageLoginVCode.gif', 'wb') as f:
        f.write(response.content)


    # 1. 创建DdddOcr对象
    ocr = ddddocr.DdddOcr(show_ad=False)
    #
    # # 2. 读取图片
    # with open('./gc.jpg', 'rb') as f:
    #     img = f.read()

    # 3. 识别图片内验证码并返回字符串
    verifyCode = ocr.classification(response.content)
    print("识别结果：", verifyCode)


def test_pdf():
    session = requests.Session()
    session.proxies = get_proxies()
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        # 'Cookie': 'ASP.NET_SessionId=sxfr03ususptf3ue14uvfsbz; __51cke__=; __51vcke__undefined=d18597d1-b8f5-5474-be1c-0274eaef4893; __51vuft__undefined=1747640053907; __jsluid_s=5d2c8c7ee29e18716df1f6d39ef0d0b2; __51uvsct__undefined=2; _d_id=3f259a251486099b285a37800b4431; __tins__18926186=%7B%22sid%22%3A%201747643142023%2C%20%22vd%22%3A%204%2C%20%22expires%22%3A%201747645040002%7D; __51laig__=8; __vtins__undefined=%7B%22sid%22%3A%20%22ab7496e7-07e1-5e8b-9127-b985c4ea9a87%22%2C%20%22vd%22%3A%204%2C%20%22stt%22%3A%2097874%2C%20%22dr%22%3A%205270%2C%20%22expires%22%3A%201747645040163%2C%20%22ct%22%3A%201747643240163%7D',
        'Referer': 'https://www.ttbz.org.cn/Home/Standard/?CNL1Code=A',
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

    params = {
        'CNL1Code': 'A',
        'page': '2',
    }

    response = session.get('https://www.ttbz.org.cn/Home/Standard/',
                            params=params,
                            # cookies=cookies,
                            headers=headers,
                            # proxies=proxies
                            )
    print(response.text)
    print(response.status_code)
    print(response.headers)
    print(session.cookies)

    headers = {
        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        # 'Cookie': 'ASP.NET_SessionId=sxfr03ususptf3ue14uvfsbz; __51cke__=; __51vcke__undefined=d18597d1-b8f5-5474-be1c-0274eaef4893; __51vuft__undefined=1747640053907; __jsluid_s=5d2c8c7ee29e18716df1f6d39ef0d0b2; __51uvsct__undefined=2; __tins__18926186=%7B%22sid%22%3A%201747643142023%2C%20%22vd%22%3A%204%2C%20%22expires%22%3A%201747645040002%7D; __51laig__=8; __vtins__undefined=%7B%22sid%22%3A%20%22ab7496e7-07e1-5e8b-9127-b985c4ea9a87%22%2C%20%22vd%22%3A%204%2C%20%22stt%22%3A%2097874%2C%20%22dr%22%3A%205270%2C%20%22expires%22%3A%201747645040163%2C%20%22ct%22%3A%201747643240163%7D; _d_id=3f749a14456c8f4545b837800b4431',
        'Referer': 'https://www.ttbz.org.cn/Home/Standard/?CNL1Code=A&page=2',
        'Sec-Fetch-Dest': 'image',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="109", "Not_A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    response = session.get('https://www.ttbz.org.cn/ValidCode/PageLoginVCode',
                            headers=headers
                            )
    print(response.text)
    print(response.status_code)
    with open('./PageLoginVCode.gif', 'wb') as f:
        f.write(response.content)


    # 1. 创建DdddOcr对象
    ocr = ddddocr.DdddOcr(show_ad=False)
    #
    # # 2. 读取图片
    # with open('./gc.jpg', 'rb') as f:
    #     img = f.read()

    # 3. 识别图片内验证码并返回字符串
    verifyCode = ocr.classification(response.content)
    print("识别结果：", verifyCode)

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        # 'Cookie': 'ASP.NET_SessionId=sxfr03ususptf3ue14uvfsbz; __51cke__=; __51vcke__undefined=d18597d1-b8f5-5474-be1c-0274eaef4893; __51vuft__undefined=1747640053907; __jsluid_s=5d2c8c7ee29e18716df1f6d39ef0d0b2; __51uvsct__undefined=2; __tins__18926186=%7B%22sid%22%3A%201747643142023%2C%20%22vd%22%3A%205%2C%20%22expires%22%3A%201747645044930%7D; __51laig__=9; _d_id=3f799a251486173fa9983780478d31; __vtins__undefined=%7B%22sid%22%3A%20%22ab7496e7-07e1-5e8b-9127-b985c4ea9a87%22%2C%20%22vd%22%3A%205%2C%20%22stt%22%3A%20102783%2C%20%22dr%22%3A%204909%2C%20%22expires%22%3A%201747645045072%2C%20%22ct%22%3A%201747643245072%7D',
        'Referer': 'https://www.ttbz.org.cn/Home/Standard/?CNL1Code=A&page=2',
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

    params = {
        'ps': '100',
        'searchType': '',
        'key': '',
        'enTitle': '',
        'stNo': '',
        'stName': '',
        'orgCode': '',
        'orgName': '',
        'stStatus': '',
        'stSale': '',
        'CNL1Code': 'A',
        'CNL2Code': '',
        'CNL3Code': '',
        'ENL1Code': '',
        'ENL2Code': '',
        'ENL3Code': '',
        'stOpen': '',
        'pcode': verifyCode,
        'page': '2',
    }

    response = session.get('https://www.ttbz.org.cn/Home/Standard', params=params, headers=headers)
    print(response.text)
    print(response.status_code)

    proxies = get_proxies()
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        # 'Cookie': 'ASP.NET_SessionId=sxfr03ususptf3ue14uvfsbz; __51cke__=; __51uvsct__undefined=1; __51vcke__undefined=d18597d1-b8f5-5474-be1c-0274eaef4893; __51vuft__undefined=1747640053907; __jsluid_s=5d2c8c7ee29e18716df1f6d39ef0d0b2; _d_id=3fb3ee14456c8fbad7e737800b4431; __tins__18926186=%7B%22sid%22%3A%201747640053643%2C%20%22vd%22%3A%203%2C%20%22expires%22%3A%201747642793548%7D; __51laig__=3; __vtins__undefined=%7B%22sid%22%3A%20%224beec12d-e25f-5d45-aac4-d72b72fafd5e%22%2C%20%22vd%22%3A%203%2C%20%22stt%22%3A%20940326%2C%20%22dr%22%3A%20821721%2C%20%22expires%22%3A%201747642794231%2C%20%22ct%22%3A%201747640994231%7D',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="109", "Not_A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    response = requests.get('https://www.ttbz.org.cn/StandardManage/Detail/137500/', headers=headers, proxies=proxies)
    print(response.text)
    print(response.status_code)

    #
    # headers = {
    #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    #     'Accept-Language': 'zh-CN,zh;q=0.9',
    #     'Cache-Control': 'max-age=0',
    #     # 'Connection': 'keep-alive',
    #     # 'Cookie': '__51cke__=; __51vcke__undefined=711df26e-c8e6-507a-8c8f-75a0ec65beaf; __51vuft__undefined=1747017822263; CCKF_visitor_id_830188=1405169801; __jsluid_s=5f136789cda34b24a45b3943fc4412a2; ASP.NET_SessionId=01pst32k1ygtl5ulf3jfoclc; __51uvsct__undefined=2; __tins__18926186=%7B%22sid%22%3A%201747037609154%2C%20%22vd%22%3A%2014%2C%20%22expires%22%3A%201747040228005%7D; __51laig__=37; __vtins__undefined=%7B%22sid%22%3A%20%22755f5d0e-9d61-554d-8bf7-089d893c6aeb%22%2C%20%22vd%22%3A%2014%2C%20%22stt%22%3A%20818702%2C%20%22dr%22%3A%2018363%2C%20%22expires%22%3A%201747040228061%2C%20%22ct%22%3A%201747038428061%7D; _d_id=ed0e4414456c8f4042db3780478de3',
    #     # 'Sec-Fetch-Dest': 'document',
    #     # 'Sec-Fetch-Mode': 'navigate',
    #     # 'Sec-Fetch-Site': 'none',
    #     # 'Sec-Fetch-User': '?1',
    #     # 'Upgrade-Insecure-Requests': '1',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    #     'sec-ch-ua': '"Chromium";v="109", "Not_A Brand";v="99"',
    #     # 'sec-ch-ua-mobile': '?0',
    #     # 'sec-ch-ua-platform': '"Windows"',
    # }
    #
    # params = {
    #     'ftype': 'stn',
    #     'pms': '137500',
    # }
    #
    # response = requests.get('https://www.ttbz.org.cn/Pdfs/Index/',
    #                         params=params,
    #                         # cookies=cookies,
    #                         headers=headers,
    #                         proxies=get_proxies()
    #                         )


    headers = {
        'Referer': 'https://www.ttbz.org.cn/Scripts/pdf.worker.js?rnd=1747040072211',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    }

    params = {
        'rand': '1747040072223',
    }

    response = requests.get('https://www.ttbz.org.cn/Home/PdfFileStreamGet/c3RuLDEzNDE5MQ(eq)(eq)', params=params, proxies=get_proxies(),
                            headers=headers)
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

    obj = ttbzOrg()
    obj.scheduler()
    # test_captcha()
    # test_pdf()
    # test_list()

    # test_detail()
    # metrics.close()

    # get_captcha()

    MongoClient.close()
