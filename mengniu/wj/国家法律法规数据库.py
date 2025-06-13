# coding=utf8
import json
import re
import urllib
import requests
import time
import warnings
from bs4 import BeautifulSoup
warnings.filterwarnings("ignore")
from datetime import datetime
from loguru import logger
import sys
sys.path.append('../')
from tools.get_proxy import get_proxies
from tools.save import save_articles
from tools.settings import mengniu_data_original_col, MongoClient
import subprocess
from functools import partial
subprocess.Popen = partial(subprocess.Popen, encoding='utf-8')
from feapder.utils import metrics
from lxml import etree


# url_set = set()
class FLK_GOV(object):

    def __init__(self):
        self.data_id = "None"
        self.expiry = ""
        self.status = ""
        self.publisher = ""
        self.list_url = None
        self.column_domain = None
        self.page = None
        self.detail_url = None
        self.publish_time = None
        self.title = None
        self.column = None
        self.type_dict = {
            "1": "有效",

            "3": "尚未生效",
            "5": "已修改",
            "7": "",
            "9": "已废止",
        }

    def scheduler(self):
        column_list = [
            # # #政策法规
            # ("xffl", "国家法律法规数据库", "国家法律法规数据库-宪法"),
            ("flfg", "国家法律法规数据库", "国家法律法规数据库-法律"),
            ("xzfg", "国家法律法规数据库", "国家法律法规数据库-行政法规"),
            ("sfjs", "国家法律法规数据库", "国家法律法规数据库-司法解释"),
            ("dfxfg", "国家法律法规数据库", "国家法律法规数据库-地方性法规"),
        ]

        for self.column in column_list:
            self.column_domain = self.column[0]
            self.get_list()


    def get_list(self):
        logger.info(f'处理栏目：{self.column}')
        self.page = 1
        while True:
            if self.page > 1:
                logger.success(f'{self.column[2]} 处理完毕')
                return

            headers = {
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Host": "flk.npc.gov.cn",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            }
            try:
                time.sleep(2)
                self.list_url = f"https://flk.npc.gov.cn/api/?page={self.page}&type={self.column_domain}&searchType=title%3Bvague&sortTr=f_bbrq_s%3Bdesc&gbrqStart=&gbrqEnd=&sxrqStart=&sxrqEnd=&sort=true&size=10&_={int(time.time()*1000)}"
                # print(self.list_url)
                response = requests.get(
                    url=self.list_url,
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
                    if response.status_code == 404:
                        logger.info(f'404 {self.column} 列表页没数据了')
                        return
                    time.sleep(2)
                    continue
                # print(response.text)
                res_dict = json.loads(response.text)
                data_list = res_dict["result"]["data"]
                if data_list:
                    for data in data_list:

                        self.detail_url = "https://flk.npc.gov.cn" + str(data["url"]).strip(".")
                        self.data_id = data["id"]
                        self.title = data["title"]
                        self.publisher = data.get("office", "")
                        self.status = self.type_dict[data["status"]]
                        # 实施日期
                        self.expiry = data.get("expiry", "").split(" ")[0]
                        self.publish_time = data.get("publish", "").split(" ")[0]
                        logger.info(f'{self.publish_time} -- {self.detail_url} --- {self.title}')

                        if self.publish_time < "2024-01-01":
                            logger.info(f'只采集近一年的数据：{self.publish_time}')
                            return

                        find_detail_url = mengniu_data_original_col.find_one({"_id": self.detail_url})
                        if find_detail_url:
                            logger.info(f'已经采集过：{self.detail_url}, {self.title}')
                            continue
                            # return
                        self.get_detail()
                        # return
                    self.page += 1
                    # return
                else:
                    # print(len(data_list))
                    logger.info(f'列表页没 数据  -- 栏目结束 --- {response.text}')
                    return


    def get_detail(self):
        logger.info(f'process {self.column[2]} -- {self.page} -- {self.title} -- {self.detail_url}')
        post_data = {
            "id": self.data_id
        }
        while True:
            headers = {
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Host": "flk.npc.gov.cn",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            }
            try:
                # time.sleep(2)
                response = requests.post(
                    url="https://flk.npc.gov.cn/api/detail",
                    proxies=get_proxies(),
                    headers=headers,
                    data=post_data,
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
                post_res_dict = json.loads(response.text)
                body_list = post_res_dict["result"]["body"]
                # WORD    PDF
                pdf_url = ""
                file_type = ""
                file_url = ""
                for body in body_list:
                    file_type = body["type"]
                    if file_type not in ["WORD", "PDF"]:
                        continue
                    pdf_url = "https://wb.flk.npc.gov.cn" + body["path"]
                    file_url = body["url"]
                    if file_type == "WORD":
                        break
                if pdf_url:

                    attachment_list = [{"fileName": f"{self.title}.{pdf_url.split('.')[-1]}", "fileLink": pdf_url}]
                    file_content = get_count(file_url)

                    content_str = f'''<div class="content">
                    {file_content}
                    </div>'''
                    # print(content_str)
                else:
                    logger.error(f'file type not supported: {self.title} -- {self.detail_url}')
                    attachment_list = []
                    content_str = ""
                    # time.sleep(100000)


                data = {
                    "_id": self.detail_url,
                    "标题": self.title,
                    "网站发布时间": self.publish_time,
                    "文章地址URL": self.detail_url,
                    "采集源名称": self.column[1],
                    "正文": content_str,
                    "HTML": content_str,
                    "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": 0,
                    "平台形式": "网站",
                    "数据类型": "法规",
                    "F_法规名称": self.title,
                    # "F_发布文号": F_发布文号,
                    # "F_专业属性": F_专业属性,
                    "F_发布单位": self.publisher,
                    "F_发布日期": self.publish_time,
                    "F_生效日期": self.expiry,
                    # "F_废止日期": F_废止日期,
                    "F_有效性状态": self.status,
                    # "F_属性": F_属性,
                    # "F_备注": F_备注,
                    # "F_法规来源": F_法规来源,
                    # "F_法规摘要": F_法规摘要,
                    "附件": json.dumps(attachment_list, ensure_ascii=False)
                }
                if save_articles(data):
                    metrics.emit_counter("详情页采集量", count=1, classify=f"{self.column[1]}")
                # print(json.dumps(data, ensure_ascii=False))
                return

def get_count(url):
    url_cut = url.rsplit("/", 1)
    file_id = url_cut[-1].split(".")[0]
    while True:
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Host": "wb.flk.npc.gov.cn",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        }
        try:
            # time.sleep(2)
            url = f"https://wb.flk.npc.gov.cn{url_cut[0]}/{file_id[0]}/{file_id}/0/info.json?_={int(time.time() * 1000)}"
            # print(url)
            response = requests.get(
                url=url,
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
                # if response.status_code == 404:
                #     return
                # continue
            count = json.loads(response.text)["count"]
            logger.success(f'获取附件文档篇数成功：{count} --- {url}')
            file_content = ""
            for i in range(count):
                file_content += f'''    
    <div class="image-container">
        <img src="https://wb.flk.npc.gov.cn{url_cut[0]}/{file_id[0]}/{file_id}/0/d_96/{i}.png">
    </div>

            '''
            return file_content


if __name__ == '__main__':
    metrics.init()

    obj = FLK_GOV()
    obj.scheduler()
    # test_list()
    # test_detail()
    metrics.close()
    MongoClient.close()
