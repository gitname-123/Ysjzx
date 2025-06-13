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
from urllib.parse import unquote

# url_set = set()
class DbbaSacinfoOrg(object):

    def __init__(self):
        self.pk = None
        self.detailNo = None
        self.implementDate = None
        self.publishTime = None
        self.standardNo = None
        self.validStatus = None
        self.page = None
        self.detailUrl = None
        self.title = None
        self.column = None

    def scheduler(self):
        self.page = 1     # 由于数据量太多，目前只采集了2025以后的

        while True:
            if self.page > 5:
                logger.success(f'处理完毕')
                return

            try:
                logger.info(f'处理列表页：{self.page}')
                headers = {
                    'authority': 'dbba.sacinfo.org.cn',
                    'accept': 'application/json, text/javascript, */*; q=0.01',
                    'accept-language': 'zh-CN,zh;q=0.9',
                    'content-type': 'application/x-www-form-urlencoded',
                    # 'cookie': 'Hm_lvt_36f2f0446e1c2cda8410befc24743a9b=1747099941; HMACCOUNT=9E52F3EF47E956AF; JSESSIONID=46785CCA780E8789CA72ED41E4FA1071; Hm_lpvt_36f2f0446e1c2cda8410befc24743a9b=1747100134',
                    'origin': 'https://dbba.sacinfo.org.cn',
                    'referer': 'https://dbba.sacinfo.org.cn/stdList',
                    'sec-ch-ua': '"Chromium";v="109", "Not_A Brand";v="99"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-origin',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
                    'x-requested-with': 'XMLHttpRequest',
                }

                data = {
                    'current': f'{self.page}',
                    'size': '15',
                    'key': '',
                    'ministry': '',
                    'industry': '',
                    'pubdate': '',
                    'date': '',
                    'status': '',
                }

                response = requests.post(
                    'https://dbba.sacinfo.org.cn/stdQueryList',
                    data=data,
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
                if not response.text.__contains__("searchCount"):
                    logger.info(f'列表页没生成成功数据数据 -- 程序结束 --- {response.text}')
                    return
                res_dict = json.loads(response.text)

                for record in res_dict['records']:

                    self.title = record['chName']
                    self.pk = record['pk']
                    self.detailUrl = f"https://dbba.sacinfo.org.cn/stdDetail/{self.pk}"
                    self.publishTime = datetime.fromtimestamp(record['issueDate'] / 1000).strftime('%Y-%m-%d')
                    self.implementDate = datetime.fromtimestamp(record['actDate'] / 1000).strftime('%Y-%m-%d')
                    recordDate = datetime.fromtimestamp(record['recordDate'] / 1000).strftime('%Y-%m-%d')
                    self.standardNo = record["code"]
                    self.validStatus = record["status"]
                    logger.info(f'{self.publishTime} -- {self.implementDate} -- {self.detailUrl} --- {self.standardNo} --- {self.title}')

                    if recordDate < "2025-01-01":
                        logger.info(f'只采集近一年的数据：{self.publishTime}')
                        return

                    find_detail_url = mengniu_data_original_col.find_one({"_id": self.detailUrl})
                    if find_detail_url:
                        logger.info(f'已经采集过：{self.detailUrl}, {self.title}')
                        continue
                        # return
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
                time.sleep(1)
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

                publisher_xpath = response_html.xpath('//dt[contains(text(), "技术归口")]/following-sibling::dd[1]/text()')
                publisher = publisher_xpath[0].strip() if publisher_xpath else ""

                attr_list = []
                if response.text.__contains__("点击查看标准全文"):
                    fileName, filePath = self.get_pdf()
                    attr_list.append({"fileName": fileName, "filePath": filePath})
                else:
                    logger.info(f'这个标准没有附件：{self.detailUrl} --- {self.title}')
                data = {
                    "_id": self.detailUrl,
                    "标题": self.title,
                    "网站发布时间": self.publishTime,
                    "文章地址URL": self.detailUrl,
                    "采集源名称": "全国标准信息服务平台",
                    "正文": "",
                    "HTML": response.text,
                    "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": 0,
                    "平台形式": "网站",
                    "数据类型": "标准",
                    "B_标准编号": self.standardNo,
                    "B_标准名称": self.title,
                    "B_标准类别": "地方标准",
                    "B_发布日期": self.publishTime,
                    "B_标准状态": self.validStatus,
                    "B_实施日期": self.implementDate,
                    "B_颁发部门": publisher,
                    # "B_废止日期": B_废止日期,
                    # "B_标准介绍": B_标准介绍
                    "附件": json.dumps(attr_list, ensure_ascii=False)
                }
                if save_articles(data):
                    # metrics.emit_counter("详情页采集量", count=1, classify=f"全国标准信息服务平台-地方标准化")
                    pass
                # print(json.dumps(data, ensure_ascii=False))
                return

    # 下载附件 数英验证码  获取验证码并识别
    def get_pdf(self):
        logger.info(f'开始下载附件:{self.pk}')
        session = requests.Session()
        time_out_flag = False
        # 1. 创建DdddOcr对象
        ocr = ddddocr.DdddOcr(show_ad=False)
        retry = 0
        while retry < 9:
            cookies = {
                'Hm_lvt_36f2f0446e1c2cda8410befc24743a9b': f'{int(time.time())}',
                # 'HMACCOUNT': '5E3DCAD3DF824D60',
                # 'JSESSIONID': 'D6A057B7F3693CE209063BC0C108D27F',
                # 'Hm_lpvt_36f2f0446e1c2cda8410befc24743a9b': f'{int(time.time())}',
            }
            # time.sleep(1)
            try:
                if retry < 7:
                    proxies = get_proxies()
                    session.proxies = proxies
                else:
                    session.proxies = ""
                captcha_url = f"https://dbba.sacinfo.org.cn/portal/validate-code?pk={self.pk}"
                headers = {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "Host": "dbba.sacinfo.org.cn",
                    "Referer": f"https://dbba.sacinfo.org.cn/portal/online/{self.pk}",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                }

                pic_res = session.get(url=captcha_url, headers=headers, timeout=20, verify=False)
                with open('./validate-code.png', 'wb') as f:
                    f.write(pic_res.content)

                verifyCode = ocr.classification(pic_res.content)
                print("识别结果：", verifyCode)

                # 验证验证码
                verify_url = "https://dbba.sacinfo.org.cn/portal/validate-captcha/down"
                data = {
                    "captcha": verifyCode,
                    "pk": self.pk
                }
                headers = {
                    'host': 'dbba.sacinfo.org.cn',
                    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    # 'cookie': 'Hm_lvt_36f2f0446e1c2cda8410befc24743a9b=1747099941; HMACCOUNT=9E52F3EF47E956AF; JSESSIONID=4FC3D9A64EBD52D955EA64EAEA699B8C; Hm_lpvt_36f2f0446e1c2cda8410befc24743a9b=1747126087',
                    'origin': 'https://dbba.sacinfo.org.cn',
                    'referer': f'https://dbba.sacinfo.org.cn/portal/online/{self.pk}',
                    'sec-ch-ua': '"Chromium";v="109", "Not_A Brand";v="99"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-origin',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
                    'x-requested-with': 'XMLHttpRequest',
                    # "cookie": "Hm_lvt_36f2f0446e1c2cda8410befc24743a9b=1747099941; HMACCOUNT=9E52F3EF47E956AF; JSESSIONID=4FC3D9A64EBD52D955EA64EAEA699B8C; Hm_lpvt_36f2f0446e1c2cda8410befc24743a9b=1747126087"

                }
                verify_res = session.post(url=verify_url, headers=headers, data=data, timeout=20, verify=False, cookies=cookies)
                logger.info(f"验证结果：{verify_res.text}")

                if verify_res.text.__contains__("验证码错误"):
                    logger.error(f'验证失败，重试一次')
                    retry += 1
                    time.sleep(2)
                    continue
                # 下载pdf
                pdf_url = f"https://dbba.sacinfo.org.cn/portal/download/{json.loads(verify_res.text)['msg']}"
                headers = {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "Host": "dbba.sacinfo.org.cn",
                    "Referer": f'https://dbba.sacinfo.org.cn/portal/online/{self.pk}',
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                }
                pdf_res = session.get(url=pdf_url, headers=headers, cookies=cookies, timeout=30, verify=False)
                # print(pdf_res.text)
                # print(pdf_res.status_code)
                logger.info(pdf_res.headers)
                try:
                    filename = unquote(re.findall('filename=(.*?)\'', str(pdf_res.headers))[0])
                except:
                    logger.error(f'没有获取到附件名称：{self.detailUrl}')
                    filename = f'{self.standardNo}.pdf'
                logger.info(f'filename: {filename}')
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


def test_captcha():
    pk = "ccf03d706612dc293a9e0da713ba9eaf1fc7b57ce5704a4dfc0540531ff79b0c"
    detailUrl = f"https://dbba.sacinfo.org.cn/stdDetail/{pk}"

    # session = requests.Session()
    # session.cookies = {
    #         'Hm_lvt_36f2f0446e1c2cda8410befc24743a9b': '1747099941',
    #         'HMACCOUNT': '9E52F3EF47E956AF',
    #         # 'JSESSIONID': '4FC3D9A64EBD52D955EA64EAEA699B8C',
    #         'Hm_lpvt_36f2f0446e1c2cda8410befc24743a9b': '1747126087',
    #     }
    time_out_flag = False
    # 1. 创建DdddOcr对象
    ocr = ddddocr.DdddOcr(show_ad=False)
    retry = 0
    while retry < 5:
        cookies = {
            'Hm_lvt_36f2f0446e1c2cda8410befc24743a9b': f'{int(time.time())}',
            # 'HMACCOUNT': '5E3DCAD3DF824D60',
            # 'JSESSIONID': 'D6A057B7F3693CE209063BC0C108D27F',
            # 'Hm_lpvt_36f2f0446e1c2cda8410befc24743a9b': f'{int(time.time())}',
        }
        time.sleep(2)
        if not time_out_flag:
            proxies = get_proxies()
        #     # session.proxies = "" #  proxies
        else:
        #     session.proxies = ""
            proxies = ""
        #     pass
        # proxies = ""
        # # # 初次请求详情页
        # # pdf_url = detailUrl
        # headers = {
        #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        #     "Host": "dbba.sacinfo.org.cn",
        #     "Referer": "https://dbba.sacinfo.org.cn/stdList",
        #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        #     # "cookie": "Hm_lvt_36f2f0446e1c2cda8410befc24743a9b=1747099941; HMACCOUNT=9E52F3EF47E956AF; JSESSIONID=4FC3D9A64EBD52D955EA64EAEA699B8C; Hm_lpvt_36f2f0446e1c2cda8410befc24743a9b=1747126087"
        #     # "Connection": "keep-alive"
        # }
        # pdf_res = requests.get(url=detailUrl, headers=headers, timeout=10, cookies=cookies)
        # # 初次请求pdf
        # pdf_url = f"https://dbba.sacinfo.org.cn/portal/online/{pk}"
        # headers = {
        #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        #     "Host": "dbba.sacinfo.org.cn",
        #     "Referer": detailUrl,
        #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        #     # "cookie": "Hm_lvt_36f2f0446e1c2cda8410befc24743a9b=1747099941; HMACCOUNT=9E52F3EF47E956AF; Hm_lpvt_36f2f0446e1c2cda8410befc24743a9b=1747126087"
        #
        # }
        # session.headers = headers
        # pdf_res = requests.get(url=pdf_url, headers=headers, timeout=10)
        # print(pdf_res.cookies)
        captcha_url = f"https://dbba.sacinfo.org.cn/portal/validate-code?pk={pk}"
        headers = {
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            "Host": "dbba.sacinfo.org.cn",
            "Referer": f"https://dbba.sacinfo.org.cn/portal/online/{pk}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            # "cookie": "Hm_lvt_36f2f0446e1c2cda8410befc24743a9b=1747099941; HMACCOUNT=9E52F3EF47E956AF; JSESSIONID=4FC3D9A64EBD52D955EA64EAEA699B8C; Hm_lpvt_36f2f0446e1c2cda8410befc24743a9b=1747126087"

        }

        pic_res = requests.get(url=captcha_url, headers=headers, timeout=10, proxies=proxies)
        pic_cookies = pic_res.cookies.get_dict()
        print(pic_cookies)
        with open('./validate-code.png', 'wb') as f:
            f.write(pic_res.content)

        verifyCode = str(ocr.classification(pic_res.content).strip())
        print("识别结果：", verifyCode, len(verifyCode))

        # 验证验证码
        verify_url = "https://dbba.sacinfo.org.cn/portal/validate-captcha/down"
        # verify_url = "https://dbba.sacinfo.org.cn/portal/validate-captcha/read"
        data = {
            "captcha": verifyCode,
            "pk": pk
        }

        cookies.update(pic_cookies)
        print(cookies)

        headers = {
            'Host': 'dbba.sacinfo.org.cn',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            # 'cookie': 'Hm_lvt_36f2f0446e1c2cda8410befc24743a9b=1747185707; HMACCOUNT=5E3DCAD3DF824D60; JSESSIONID=D6A057B7F3693CE209063BC0C108D27F; Hm_lpvt_36f2f0446e1c2cda8410befc24743a9b=1747186752',
            'origin': 'https://dbba.sacinfo.org.cn',
            'referer': f'https://dbba.sacinfo.org.cn/portal/online/{pk}',
            'sec-ch-ua': '"Chromium";v="109", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }

        verify_res = requests.post(url=verify_url, headers=headers, cookies=cookies, data=data, timeout=10, proxies=proxies)
        logger.info(f"验证结果：{verify_res.text}")

        return
        if verify_res.text.__contains__("验证码错误"):
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


if __name__ == '__main__':
    # metrics.init()
    #
    obj = DbbaSacinfoOrg()
    obj.scheduler()
    # test_captcha()
    # test_list()

    # test_detail()
    # metrics.close()

    # get_captcha()

    MongoClient.close()
