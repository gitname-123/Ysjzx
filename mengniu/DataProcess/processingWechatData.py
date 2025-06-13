"""
从mongo 微信公众号实时监听表里获取任务 解析 下载附件
"""
import hashlib
import html
import json
import re
import time
import urllib
from pathlib import Path
from threading import Thread, Lock
from queue import Empty, Queue
import pymongo
import requests
import urllib3
from loguru import logger
from lxml import etree
from pymongo.errors import DuplicateKeyError
import warnings
warnings.filterwarnings("ignore")
import sys
sys.path.append('../')
from tools.settings import db_wechat_article_monitor, db_mengniu_data_col, today
# from tools.get_proxy import get_proxies


def parse_content(task):
    dateStr = today.replace("-", "")

    try:
        title = task["_id"]
        url = task["url"]
        publishTime = task["publishTime"]
        js_content_text = task["content"]
        content_html = etree.HTML(js_content_text)
        js_content = content_html.xpath('//div[@id="js_content"]')
        if js_content:
            # print(etree.tostring(js_content[0], encoding="utf-8").decode())
            # js_content_text = html.unescape(etree.tostring(js_content[0], encoding="utf-8").decode())
            # print(js_content_text)
            # return
            data_src_tag = js_content[0].xpath('//*[@data-src]')
            if data_src_tag:
                for data_src_item in data_src_tag:
                    data_src = None
                    data_type = None
                    data_src_xpath = data_src_item.xpath('./@data-src')
                    if data_src_xpath:
                        data_src = data_src_xpath[0]
                    else:
                        continue
                    if str(data_src).endswith(".js"):
                        continue
                    data_type_xpath = data_src_item.xpath('./@data-type')
                    if data_type_xpath:
                        data_type = data_type_xpath[0]
                    else:
                        logger.error(f'有 data-src 没有 data-type:{url} --- {data_src}')
                        # continue

                    file_content, Content_Type = download_file(url, data_src)

                    if file_content:
                        if not data_type and Content_Type:
                            data_type = str(Content_Type).split("/")[-1]
                        # data_src_format = data_src.replace("/", "").replace(".", "").replace("*", "").replace("?", "").replace(":", "").replace("<", "").replace(">", "").replace("|", "").replace("&", "").replace("=", "")
                        data_src_md5 = hashlib.md5(data_src.encode('utf-8')).hexdigest()
                        file_name = data_src_md5 + f'.{data_type}'

                        dir_path = '../attachments/{}/wechat_attachments'.format(dateStr)
                        Path(dir_path).mkdir(parents=True, exist_ok=True)
                        file_path = f'{dir_path}/{file_name}'
                        logger.info(file_path)

                        try:
                            with open(file_path, "wb") as file:
                                file.write(file_content)
                                # file.close()
                        except Exception as e:
                            logger.error(f"保存文件 下载失败 error:{e} --- {url} --- {data_src}")

                        else:
                            logger.success("文件下载成功:{}".format(file_path))
                            # 正文替换
                            # 有特殊字符 用re.sub替换失败
                            # js_content_text = re.sub(f'{data_src}', file_path, js_content_text)
                            js_content_text = js_content_text.replace(data_src, file_path.replace("../attachments", "./attachments"))
                    else:
                        logger.error(f'文章中的文件没有下载成功：{url} --- {data_src}')
                print(js_content_text)
            else:
                logger.info(f'文章中没有要下载的文件')

            data = {
                "_id": url,
                "标题": title,
                "网站发布时间": publishTime,
                "文章地址URL": url,
                "采集源名称": task["sourceName"],
                "正文": js_content_text,
                "采集时间": task["downtime"],
                # "W_文章来源": "",
                # "W_文章摘要": "",
                "export_status": 0,
                "附件": "",
                "processTime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            }
            # print(data)
            # print(json.dumps(data, ensure_ascii=False))
            save_data(data)
            query = {"_id": title}
            new_value = {"$set": {"status": 5}}
            db_wechat_article_monitor.update_one(query, new_value)

        else:
            logger.error(f'采集详情页没有js_conten：{url}')

        return
    except Exception as e:
        logger.error(f'parse content error:{e} --- {task["_id"]}')


def save_data(doc):
    try:
        db_mengniu_data_col.insert_one(doc)
    except DuplicateKeyError:
        logger.info("article 已存入该条数据:{}".format(doc["_id"]))
    except Exception as e:
        logger.error("save db error:{} -- {}".format(e, doc["_id"]))
    else:
        logger.success("解析数据完成:{}".format(doc["_id"]))


def download_file(article_url, url):

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    }

    retry = 0
    logger.info(f'正在下载文件：{url}')
    while retry < 3:
        try:
            # print("采集.......")
            # headers["User-Agent"] = get_UA()
            # print(url)
            # url = "https://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_pdf/90/a1/jkms-22-698.PMC2693823.pdf"
            file_res = requests.get(url=url, headers=headers, timeout=10, proxies=get_proxies(), verify=False)    #, proxies=
        except Exception as e:
            logger.error("requests error:{} -- {}".format(e, url))
            time.sleep(0.5)
            retry += 1
        else:
            if file_res.status_code != 200:
                retry += 2
                continue
            else:
                return file_res.content, file_res.headers.get("Content-Type", "")
    else:
        logger.error(f'公众号中的附件下载3次都失败了：{article_url} -- {url}')
        return None, None


# 创建任务
def producer(queue):
    while True:
        if queue.qsize() == 0:
            queue.join()
            cursor = db_wechat_article_monitor.find({"status": 0, "projectName": "蒙牛"})# .limit(1)
            cursor_data_list = list(cursor)
            cursor.close()
            if cursor_data_list:
                logger.info(f"put queue task -- total:{len(cursor_data_list)}")
                for doc_data in cursor_data_list:
                    queue.put(doc_data)
            else:
                logger.success("采集微信公众号详情页 任务处理完毕")
                return
            return
        else:
            logger.info(f"queue size:{queue.qsize()}")
            time.sleep(5)


# 消费任务
def consumer(queue):

    while True:
        task = {}
        try:
            task = queue.get()
            logger.info(f'process 微信公众号数据: {task["_id"]}')
            parse_content(task)
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


def processingWechatData_main():
    logger.info(f'开始处理公众号数据')
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
    #
    # for t in threads:
    #     t.join()

    # 调用队列的join()方法，等待队列上的所有任务完成。
    queue.join()

    # join()使用线程的方法等待所有号码加入队列。
    # producer_thread.join()

    logger.success(f'wechat_get_detail main finish')


if __name__ == '__main__':
    processingWechatData_main()
# #
#     # MongoClient = pymongo.MongoClient("mongodb://39.98.35.147:27117/")
#     # db = MongoClient["db_mengniu"]
#     # db_mengniu_data_col = db["db_mengniu_data"]
#     # todo_wechat_article_col = db["todo_mengniu_wechat_article"]
#     #
#     #
#     # wechat_get_detail_main()
#     # # from_mongo_get_task()
#     #
#     # MongoClient.close()

