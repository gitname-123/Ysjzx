import hashlib
import json
import random
import re
import redis
import requests
import pymongo
from loguru import logger
from lxml import etree
import time
from threading import Thread
import warnings
from pymongo.errors import DuplicateKeyError
warnings.filterwarnings("ignore")
import html
import subprocess
from functools import partial
subprocess.Popen = partial(subprocess.Popen, encoding='utf-8')
from datetime import datetime, timedelta
from queue import Empty, Queue
from pathlib import Path
import sys
sys.path.append('/')
from tools.settings import mengniu_attachments_col
from tools.get_proxy import get_proxies
from curl_cffi import requests as requests_cffi


def download_file_common(task):

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        # "Accept-Encoding": "gzip, deflate, br",
        # "Accept-Language": "zh-CN,zh;q=0.9",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        # "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        # "X-Requested-With": "XMLHttpRequest",
        # "Host": "ftp.ncbi.nlm.nih.gov",
        # "Referer": "https://ntrl.ntis.gov/NTRL/"
    }

    # 附件链接地址url
    url = task.get("_id")
    # if url.__contains__("efsa.onlinelibrary.wiley.com"):
    #     headers["host"] = "efsa.onlinelibrary.wiley.com"
    query = {"_id": url}
    if str(url).endswith("html") or str(url).endswith("htm") or not str(url).startswith("http"):
        new_value = {"$set": {"downloadStatus": 500}}
        mengniu_attachments_col.update_one(query, new_value)
        logger.error(f'是 HTML：{url}')
        return

    retry = 0
    flag_403 = False
    while retry < 5:
        try:
            # print("采集.......")
            # headers["User-Agent"] = get_UA()
            # print(url)
            # url = "https://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_pdf/90/a1/jkms-22-698.PMC2693823.pdf"
            # headers["Host"] = re.findall('://(.*?)/', url)[0]
            # print(headers["Host"])
            if retry < 4:
                proxies = get_proxies()
            else:
                proxies = ""
            if flag_403:
                impersonate_list = [
                    "chrome110",
                    "chrome116",
                    "chrome119",
                    "chrome120",
                    "edge99",
                    "edge101"
                    # "chrome",
                ]
                impersonate = random.choice(impersonate_list)
                s = requests_cffi.Session()
                # url = "https://efsa.onlinelibrary.wiley.com/cms/asset/4ecf09d7-ec87-4aff-bf58-6ce4f968febd/efs28554-fig-0030-m.png"
                file_res = s.get(url, impersonate=impersonate, proxies=get_proxies())

            else:
                file_res = requests.get(url=url, headers=headers, timeout=30, proxies=proxies)    # , proxies=get_proxies()

        except Exception as e:
            logger.error("requests error:{} -- {}".format(e, url))
            time.sleep(2)
            retry += 1
        else:

            if file_res.status_code != 200:
                if file_res.status_code == 404:
                    if url.__contains__("file4.foodmate.net"):
                        location_url = file_res.url
                        if location_url:
                            url = location_url
                            headers["Host"] = "file4.foodmate.net"
                            retry += 1
                            continue
                        else:
                            time.sleep(10)
                            logger.error(f'下载状态码 404 但没获取到重定向的url：{url}')
                            retry += 1
                            continue
                elif file_res.status_code == 403 and file_res.text.__contains__("Just a moment"):
                    logger.error(f'res status code:403 --- {url}')
                    flag_403 = True
                    retry += 1

                else:
                    retry += 1
                    logger.error(f'file_res status_code:{file_res.status_code} -- 重试：{retry}')
                    continue

            try:
                file_path = task["filePath"].replace("./attachments", "../attachments")
                # file = open(file_path, "wb")
                # file.write(file_res.content)
                # file.close()
                # 目录地址
                dir_path = file_path.rsplit("/", 1)[0]
                # print(dir_path)
                # 创建目录
                Path(dir_path).mkdir(parents=True, exist_ok=True)

                logger.info(file_path)
                # 写入文件
                with open(file_path, "wb") as file:
                    file.write(file_res.content)

            except Exception as e:
                logger.error(f"保存文件 下载失败 error:{e} --- {url}")
                new_value = {"$set": {"downloadStatus": 412}}
                mengniu_attachments_col.update_one(query, new_value)
            else:
                new_value = {"$set": {"downloadStatus": 5}}
                mengniu_attachments_col.update_one(query, new_value)
                logger.success("下载成功:{}".format(file_path))
            break
    else:
        new_value = {"$set": {"downloadStatus": 403}}
        mengniu_attachments_col.update_one(query, new_value)
        logger.error(f'下载失败：{url}')


# 创建任务
def producer(queue):
    while True:

        # query_doc = {"$and": [{"downloadStatus": {"$ne": 5}}, {"采集源名称": "食品伙伴网-资讯-权威发布"}]}
        # query_doc = {"downloadStatus": {"$ne": 5}}
        query_doc = {"downloadStatus": 0}
        if queue.qsize() == 0:
            queue.join()
            cursor_data_list = []
            cursor = mengniu_attachments_col.find(query_doc).limit(1000)
            for cursor_data in cursor:
                cursor_data_list.append(cursor_data)
            cursor.close()
            if cursor_data_list:
                logger.info(f"put queue task -- total:{len(cursor_data_list)}")

                for doc_data in cursor_data_list:
                    queue.put(doc_data)
            else:
                logger.success("下载附件 任务处理完毕")
                return
            # return
        else:
            logger.info(f"queue size:{queue.qsize()}")
            time.sleep(5)


# 消费任务
def consumer(queue):

    while True:
        task = {}
        try:
            task = queue.get()
            logger.info(f'process: {task["_id"]}')
            # if task["_id"].__contains__("down.foodmate.net"):
            #     download_file_standard(task)
            # else:
            download_file_common(task)

        except Empty:
            logger.info("queue is Empty")
            time.sleep(1)
            continue
        except Exception as e:
            logger.error("consumer get_detail error:{} --- {}".format(e, task))
            time.sleep(0.1)
            queue.task_done()
        else:
            # logger.success(f'done: {task["_id"]}')
            # time.sleep(random.randint(4,8))
            queue.task_done()


def downloadFile_main():
    logger.info(f'开始下载附件')

    # 通过调用Queue()构造函数创建一个新队列
    queue = Queue(maxsize=0)

    # 创建一个名为的新线程producer_thread并立即启动它
    producer_thread = Thread(
        target=producer,
        args=(queue,)
    )
    producer_thread.start()

    threads = []
    # 可以调节线程数
    threadNum = 10
    # 创建一个名为的守护线程consumer并立即启动它。
    for i in range(0, threadNum):
        t = Thread(target=consumer, args=(queue,), daemon=True)
        threads.append(t)
    for t in threads:
        t.start()
        time.sleep(0.5)

    # for t in threads:
    #     t.join()
    # join()使用线程的方法等待所有号码加入队列。
    producer_thread.join()
    # 调用队列的join()方法，等待队列上的所有任务完成。
    queue.join()

    logger.success(f'downloadFile main finish')


#
# if __name__ == '__main__':
#     downloadFile_main()

#     # MongoClient = pymongo.MongoClient("mongodb://39.98.35.147:27117/")
#     # db = MongoClient["db_mengniu"]
#     # mengniu_attachments_col = db["mengniu_attachments"]
#     # # mengniu_attachments_col = db["mengniu_attachments_20250224"]
#     #
#     # # mengniu_attachments_col = db["mengniu_attachments_test_wj"]
#     # # get_id_to_todo()
#     #
#     # main()
#     # #
#     # MongoClient.close()
#     # # # http://192.168.52.33/wcm/ZZZ/AppData/Roaming/Foxmail7/GBT%2024549-2009%20%20燃料电池电动汽车%20安全要求.pdf
#     # # a = ["标签标识", "产品超过保质期", "配料合规", "其他问题", "质量问题", "假冒伪劣", "生产经营许可", "食品分类", "产品超过保质期", "标签不完整或信息缺失", "生产日期保质期标识不规范", "产品中含有标准法规不允许使用的配料", "无中文标签", "超范围超限量使用食品添加剂/营养强化剂", "营养标签不规范", "假冒伪劣", "相关资质证明不全", "虚假宣传", "未标注食用限量或不适宜人群", "异物", "强调配料或营养成分但未标识含量", "非法进口", "执行标准问题", "无证生产", "配料标识不规范", "其他问题", "生虫", "其他方面标识不规范", "发霉变质", "厂商信息不规范", "普通食品声称具有某种功效功能", "实际贮存条件与标准不符", "质量指标不合格", "污染物超标", "超范围生产经营", "食品名称不规范", "涉及功效方面的标识不规范", "无保健品批文/批文过期", "广告语易引起歧义", "致敏物质", "召回", "停止食用", "停止供应及出售", "食品", "召回", "撤回", "预警", "食品安全", "异物", "毛发", "金属", "硬质塑料", "玻璃", "过敏原", "青储", "牧草", "饲料", "米黑根毛霉菌株M19-21生产的粘蛋白酶", "嗜热菌蛋白酶", "乳酸肠球菌NCIMB 11181", "戊糖片球菌DSM 23688", "尖孢镰刀菌", "金针菇渣", "蒜脱粉", "辣椒秸秆粉料", "羟丙基纤维素", "乙基纤维素", "微晶纤维素和羧甲基纤维素", "木质素磺酸盐", "L-赖氨酸", "L-赖氨酸盐酸盐和浓缩液态L-赖氨酸盐酸盐", "石斛原球茎", "呕吐毒素", "红三叶草异黄酮", "谷氨酸棒杆菌CGMCC 20437", "赤松的松树酊", "玉树油", "甜菜碱铁复合物", "肉桂提取物", "粘着剑菌CGMCC 21299", "磷酸", "肉桂皮精油和肉桂叶精油", "烟酸和烟酰胺", "八角萜", "副干酪乳杆菌ATCC PTA-6135", "里氏木霉DSM 32338", "烯酰吗啉", "酶β-淀粉酶", "丁香酊", "克萨斯柏木油", "银杏叶酊", "桉树酊", "发酵粘液乳杆菌NCIMB 30169", "香茅油", "乙氧基奎琳", "饲喂", "挤奶", "发情", "用药", "疫病疫情", "净含量", "标签", "感官", "理化", "污染物", "微生物", "农残", "农药残留", "兽残", "兽药残留", "生产", "加工", "物流", "终端"]
#     # #
#     # # print(len(a))
