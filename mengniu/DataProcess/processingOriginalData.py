# coding=utf8
"""
处理数据脚本
主要功能：提取附件链接、下载附件、替换正文中附件、文件路径为相对路径
"""
import hashlib
import json
import re
import time
import urllib
from pathlib import Path
import html
import requests
from loguru import logger
from lxml import etree
import pymongo
from pymongo.errors import DuplicateKeyError
from queue import Empty, Queue
from threading import Thread

import warnings
# 忽略所有警告
warnings.filterwarnings("ignore")
import sys
sys.path.append('../')
from tools.settings import mengniu_data_original_col, mengniu_attachments_col, db_mengniu_data_col, today
from tools.get_proxy import get_proxies


file_suffix_list = ["zip", "xlsx", "xls", "rar", "pptx", "ppt", "png", "pdf", "jpg", "docx", "doc", "7z",]
not_src_suffix_list = ["html", "htm", "js", "php", "cn", "com"]

def get_mongo_data():
    # cursor = mengniu_data_original_col.find({"status": 0, "采集源名称": "食品伙伴网-资讯-权威发布"})
    # cursor = mengniu_data_original_col.find({"status": 0, "采集源名称": "欧盟食品安全风险评估中心信息"})
    # cursor = mengniu_data_original_col.find({"status": 0, "采集源名称": "国家市场监督管理局-行政处罚文书网"})
    # cursor = mengniu_data_original_col.find({"status": 0, "采集源名称": "杭州海关政府信息公开网-政府信息公开-技术性贸易措施动态"})
    # cursor = mengniu_data_original_col.find({"status": 0, "采集源名称": "牧通人才网"})
    # cursor = mengniu_data_original_col.find({"status": 0, "采集源名称": "世界卫生组织发布信息"})
    # cursor = mengniu_data_original_col.find({"status": 0, "采集源名称": "内蒙古自治区科技厅"})
    # cursor = mengniu_data_original_col.find({"$and": [{"status": 0}, {"$or": [{"采集源名称": "食品伙伴网-法规-国家法规"}, {"采集源名称": "食品伙伴网-法规-地方法规"}, {"采集源名称": "食品伙伴网-法规-国外法规"}, {"采集源名称": "食品伙伴网-法规-其他法规"}, {"采集源名称": "食品伙伴网-法规草案-国家法规草案"}, {"采集源名称": "食品伙伴网-法规草案-地方法规草案"}, {"采集源名称": "食品伙伴网-法规草案-其他法规草案"}]}]})
    # cursor = mengniu_data_original_col.find({"status": 0, "数据类型": "标准"})    # .limit(10)
    # cursor = mengniu_data_original_col.find({"status": 0, "采集源名称": "食品伙伴网-中国食品"})
    # cursor = mengniu_data_original_col.find({"status": 0, "采集源名称": "食品伙伴网-国际预警"})
    # cursor = mengniu_data_original_col.find({"status": 0, "采集源名称": "食品伙伴网-进出口"})
    # cursor = mengniu_data_original_col.find({"status": 0, "采集源名称": "中国食品科学技术学会"})
    # cursor = mengniu_data_original_col.find({"status": 0, "采集源名称": "美国疾病预防控制中心"})
    # cursor = mengniu_data_original_col.find({"status": 0, "采集源名称": "华盛顿卫生部食品回收及安全警示"})
    # cursor = mengniu_data_original_col.find({"status": 0, "采集源名称": "欧盟食品安全风险评估中心信息"})
    query_list = [
        # {"采集源名称": "食品伙伴网-资讯-权威发布"},
        # {"采集源名称": "欧盟食品安全风险评估中心信息"},
        # {"采集源名称": "国家市场监督管理局-行政处罚文书网"},
        # {"采集源名称": "杭州海关政府信息公开网-政府信息公开-技术性贸易措施动态"},
        # {"采集源名称": "牧通人才网"},
        # {"采集源名称": "世界卫生组织发布信息", "status": 0},
        # {"采集源名称": "内蒙古自治区科技厅"},
        # {"$and": [{"$or": [{"采集源名称": "食品伙伴网-法规-国家法规"}, {"采集源名称": "食品伙伴网-法规-地方法规"}, {"采集源名称": "食品伙伴网-法规-国外法规"}, {"采集源名称": "食品伙伴网-法规-其他法规"}, {"采集源名称": "食品伙伴网-法规草案-国家法规草案"}, {"采集源名称": "食品伙伴网-法规草案-地方法规草案"}, {"采集源名称": "食品伙伴网-法规草案-其他法规草案"}]}]},
        # {"数据类型": "标准", "status": 0},
        # {"采集源名称": "食品伙伴网-中国食品"},
        # {"采集源名称": "食品伙伴网-国际预警"},
        # {"采集源名称": "食品伙伴网-进出口"},
        # {"采集源名称": "中国食品科学技术学会"},
        # {"采集源名称": "美国疾病预防控制中心", "status": 0},
        # {"采集源名称": "华盛顿卫生部食品回收及安全警示"},
        # {"采集源名称": "欧盟食品安全风险评估中心信息"},
        # ### 20250221处理
        # {"status": 0, "采集源名称": "新京报"},
        # {"status": 0, "采集源名称": "CEFIC News"},
        # {"status": 0, "采集源名称": "ECETOC News"},
        # {"status": 0, "采集源名称": "European Commission Joint Research Center News"},
        # {"采集源名称": "ANSES"},
        # {"采集源名称": "EFSA Biological Hazards", "status": 0},
        # {"采集源名称": "EFSA Chemical Contaminants", "status": 0},
        # {"采集源名称": "EFSA Cross Cutting Science", "status": 0},
        # {"采集源名称": "EFSA Feed Materials", "status": 0},
        # {"采集源名称": "EFSA Food Ingredient & Packaging", "status": 0},
        # {"采集源名称": "EFSA GMO", "status": 0},
        # {"采集源名称": "EFSA Pesticides", "status": 0},
        # {"采集源名称": "EFSA Plant Health", "status": 0},
        # {"采集源名称": "食品伙伴网-食品安全合规服务", "status": 0},
        # {"采集源名称": "海关总署未准入境的食品信息", "status": 0},
        # {"采集源名称": "ATSDR News", "status": 0},
        # {"status": 0},
        # {"采集源名称": "Norwegian Scientific Committee for Food Safety", "status": 0},
        # {"数据类型": "标准", "status": 5},
        # {"采集源名称": "国家法律法规数据库", "status": 0},
        # {"采集源名称": "美国联邦法规", "status": 0},
        # {"_id": "https://www.fsc.go.jp/iken-bosyu/pc1_no_benzyladenine_070416.html", "status": 0},


        # {"采集源名称": "食品伙伴网首页-食品咨询-本站原创", "status": 0},
        # {"采集源名称": "食品伙伴网-质量管理", "status": 0},
        # {"采集源名称": "新西兰海关", "status": 0},
        # {"采集源名称": "海关", "status": 0},
        # {"采集源名称": "ACNFP Novel food assessment", "status": 0},
        # {"采集源名称": "新西兰初级产业部", "status": 0},
        # {"采集源名称": "ACMSF Home", "status": 0},
        # {"采集源名称": "食品、农业和轻工业部", "status": 0},
        # {"采集源名称": "健康促进局", "status": 0},
        # {"采集源名称": "欧洲食品安全局-开放页面", "status": 0, "网站发布时间": {"$gte": "2025-01-01"}}
        # {"采集源名称": "全国团体标准信息平台", "status": 0},
        # {"采集源名称": "全国标准信息服务平台", "status": 0},
        # {"采集源名称": "食品药品管理局（FDA）-食品版块", "status": 0},
    ]
    queue = Queue(maxsize=0)

    # 创建一个名为的新线程producer_thread并立即启动它


    threads = []
    # 可以调节线程数
    threadNum = 1
    # 创建一个名为的守护线程consumer并立即启动它。

    for query_doc in query_list:
        logger.info(f'process query doc: {query_doc}')
        cursor = mengniu_data_original_col.find(query_doc)# .limit(500)
        # cursor = mengniu_data_original_col.find({"_id": "https://www.efsa.europa.eu/en/news/nanotechnology-promoting-uses-new-assessment-methods"})

        # cursor = mengniu_data_original_col.find({"status": 0, "采集源名称": "杭州海关政府信息公开网-政府信息公开-技术性贸易措施动态"}).limit(1)
        # cursor = mengniu_data_original_col.find({"$or": [{"_id": "https://news.foodmate.net/2025/01/706718.html"}, {"_id": "https://news.foodmate.net/2025/01/706661.html"}]})

        data_list = list(cursor)
        cursor.close()
        logger.info(f'采集原始库获取到了{len(data_list)}条数据')

        for doc_data in data_list:
            # parse_data(doc_data)
            queue.put(doc_data)

    for i in range(0, threadNum):
        t = Thread(target=consumer, args=(queue,), daemon=True)
        threads.append(t)
    for t in threads:
        t.start()
        time.sleep(0.5)
    queue.join()
    # for t in threads:
    #     t.join()

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
            parse_data(task)

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

# 解析数据，提取正文中的附件、文件 至 附件下载表
def parse_data(doc_data):

    dateStr = today.replace("-", "")
    # print(doc_data)
    数据类型 = doc_data["数据类型"]

    _id = doc_data.get("_id")
    logger.info(f'process data:{_id}')
    # 标题 = doc_data.get("标题")
    # 网站发布时间 = doc_data.get("网站发布时间")
    # 文章地址URL = doc_data.get("文章地址URL")
    # 采集源名称 = doc_data.get("采集源名称")
    # 所属分类 = doc_data.get("所属分类")     # 与平台知识体系目录表对应的目录
    正文 = html.unescape(doc_data.get("正文"))

    # print(正文)

    附件_list = []

    # 正文之外的附件，不需要替换正文
    附件 = doc_data.get("附件", "")
    if 附件:
        附件_origin_list = json.loads(附件)
        for 附件_dict in 附件_origin_list:
            try:
                fileName = 附件_dict["fileName"]
                fileLink = 附件_dict.get("fileLink", "")
                # 采集时下载的附件
                filePath_spider = 附件_dict.get("filePath", "")
                if filePath_spider:
                    logger.info(f'采集时下载的附件： {fileName} --- {filePath_spider}')
                    file_data = {
                        "_id": f'{doc_data["_id"]}##**{fileName}',
                        "article_id": doc_data["_id"],
                        "filePath": filePath_spider,
                        "file_name_zh": fileName,
                        "downloadStatus": 5,
                        "downTime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        "平台形式": doc_data["平台形式"],
                        "采集源名称": doc_data["采集源名称"]
                    }
                    save_attachments(file_data)
                    附件_list.append({"file_path": filePath_spider, "file_name": fileName})
                    continue
                find_href = mengniu_attachments_col.find_one({"_id": fileLink})
                fileName_suffix = fileName.split(".")[-1]
                if not find_href:
                    if fileName_suffix.lower() in file_suffix_list:
                        # 文件名称前缀 用  detail_url + 文件中文名  转 md5
                        file_prefix_zh = fileName.rsplit(".", 1)[0]
                        file_prefix = hashlib.md5(f'{doc_data["_id"]}{file_prefix_zh}'.encode('utf-8')).hexdigest()

                        file_suffix = fileName_suffix
                        # file_name = f'{file_prefix}.{file_suffix}'

                        file_name_en = f'{file_prefix}.{file_suffix}'
                        file_name_zh = f'{file_prefix_zh}.{file_suffix}'
                        file_path = f'./attachments/{dateStr}/website_attachments/{file_name_en}'
                        logger.info(f'{file_name_en} --- {file_name_zh} --- {fileLink}')
                        file_data = {
                            "_id": fileLink,
                            "article_id": doc_data["_id"],
                            "filePath": file_path,
                            "file_name_zh": file_name_zh,
                            "downloadStatus": 0,
                            "downTime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            "平台形式": doc_data["平台形式"],
                            "采集源名称": doc_data["采集源名称"]
                        }
                        save_attachments(file_data)
                        附件_list.append({"file_path": file_path, "file_name": file_name_zh})

            except Exception as e:
                logger.error(f'解析正文外的附件error:{e} --- {doc_data["_id"]}')
                continue

    # 采集时间 = doc_data.get("采集时间")
    # 提交时间 = doc_data.get("")

    # # 文章字段
    # W_文章来源 = doc_data.get("W_文章来源", "")
    # W_文章摘要 = doc_data.get("W_文章摘要", "")
    #
    # # 法规字段
    # F_法规名称 = doc_data.get("F_法规名称", "")
    # F_发布文号 = doc_data.get("F_发布文号", "")
    # F_专业属性 = doc_data.get("F_专业属性", "")
    # F_发布单位 = doc_data.get("F_发布单位", "")
    # F_发布日期 = doc_data.get("F_发布日期", "")
    # F_生效日期 = doc_data.get("F_生效日期", "")
    # F_废止日期 = doc_data.get("F_废止日期", "")
    # F_有效性状态 = doc_data.get("F_有效性状态", "")
    # F_属性 = doc_data.get("F_属性", "")
    # F_备注 = doc_data.get("F_备注", "")
    #
    # # 标准字段
    # B_标准编号 = doc_data.get("B_标准编号", "")
    # B_标准名称 = doc_data.get("B_标准名称", "")
    # B_标准类别 = doc_data.get("B_标准类别", "")
    # B_发布日期 = doc_data.get("B_发布日期", "")
    # B_标准状态 = doc_data.get("B_标准状态", "")
    # B_实施日期 = doc_data.get("B_实施日期", "")
    # B_颁发部门 = doc_data.get("B_颁发部门", "")
    # B_废止日期 = doc_data.get("B_废止日期", "")
    # B_标准介绍 = doc_data.get("B_标准介绍", "")
    # B_附件 = doc_data.get("B_标准介绍", "")
    #
    # # 处罚字段
    # CF_行政处罚决定文书号 = doc_data.get("CF_行政处罚决定文书号", "")
    # CF_当事人名称 = doc_data.get("CF_当事人名称", "")
    # CF_处罚日期 = doc_data.get("CF_处罚日期", "")
    # CF_处罚机关 = doc_data.get("CF_处罚机关", "")
    # CF_处罚内容 = doc_data.get("CF_处罚内容", "")
    # CF_处罚种类 = doc_data.get("CF_处罚种类", "")
    # CF_处罚依据 = doc_data.get("CF_处罚依据", "")
    # CF_附件 = doc_data.get("CF_附件", "")

    # 处理标准的附件

    if 数据类型 == "标准" and doc_data["采集源名称"].__contains__("食品伙伴网-标准"):
        if not doc_data["网站发布时间"]:
            doc_data["网站发布时间"] = doc_data["B_发布日期"]
        # doc_data["正文"] = doc_data["B_标准介绍"]
        res_html = etree.HTML(doc_data.get("HTML"))
        # origin_title = "".join([title_text.strip() for title_text in res_html.xpath('//div[@class="title2"]/span//text()')])
        # doc_data["标题"] = origin_title
        # print(origin_title)

        # find_detail_url = db_mengniu_data_col.find_one({"_id": _id})
        # if find_detail_url:
        #     doc_data["processTime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        #     logger.info("article 已存入该条数据:{}".format(doc_data["_id"]))
        #     db_mengniu_data_col.update_one({"_id": doc_data["_id"]}, {
        #         "$set": {"标题": doc_data["标题"], "正文": doc_data["正文"], "B_标准名称": doc_data["B_标准名称"],
        #                  "B_标准状态": doc_data["B_标准状态"], "processTime": doc_data["processTime"]}})
        #     mengniu_data_original_col.update_one({"_id": doc_data["_id"]}, {"$set": {"status": 5}})
        #     return

        pdf_url_xpath = res_html.xpath('//div[@class="downk"]/a[@class="telecom"]/@href')
        if pdf_url_xpath:
            pdf_url = str(pdf_url_xpath[0])

            file_content, location_url = download_file_standard(pdf_url)

            if file_content:
                # 只要有更新，标准就重新下载, 标准这块不是统一下载  所以 ../开头
                dir_path = f'../attachments/{dateStr}/website_attachments'
                Path(dir_path).mkdir(parents=True, exist_ok=True)
                file_prefix_zh = location_url.split('/')[-1]
                file_prefix = hashlib.md5(f'{doc_data["_id"]}{file_prefix_zh}'.encode('utf-8')).hexdigest()
                file_suffix = file_prefix_zh.split('.')[-1]
                file_path = f'{dir_path}/{file_prefix}.{file_suffix}'
                logger.info(f'标准 附件：{file_path}')

                try:
                    with open(file_path, "wb") as file:
                        file.write(file_content)
                        # file.close()
                except Exception as e:
                    logger.error(f'保存文件 下载失败 error:{e} --- {doc_data["_id"]} --- {pdf_url}')
                    return
                else:
                    logger.success("文件下载成功:{}".format(file_path.replace("../attachments", "./attachments")))
                    附件_list.append({"file_path": file_path.replace("../attachments", "./attachments"), "file_name": file_prefix_zh})

            else:
                logger.error(f'文章中的文件没有下载成功：{doc_data["_id"]} --- {pdf_url}')
                return
        else:
            logger.error(f'这个标准 没附件：{doc_data["_id"]} --- {doc_data["标题"]}')

    if 正文 and not doc_data["采集源名称"].__contains__("食品伙伴网-标准"):
        # 替换正文中的图片等附件链接
        content_html = etree.HTML(正文)

        # 解析附件 a标签 href
        a_list = content_html.xpath("//a")
        for a_tag in a_list:
            # file_prefix = ""
            # file_suffix = ""
            href = a_tag.attrib.get('href', "")
            # 附件中文名称
            a_text = a_tag.text
            if not a_text:
                continue
            else:
                if a_text.strip():
                    a_text = a_text.strip()
                else:
                    continue
            a_text_suffix = a_text.split(".")[-1]
            if href:
                href_link = urllib.parse.urljoin(doc_data["_id"], href)
                # 已下载过的附件就不下载了
                find_href = mengniu_attachments_col.find_one({"_id": href_link})
                if not find_href:
                    if a_text_suffix.lower() in file_suffix_list:

                        # 文件名称前缀 用  detail_url + 文件中文名  转 md5
                        file_prefix_zh = a_text.rsplit(".", 1)[0]
                        file_prefix = hashlib.md5(f'{doc_data["_id"]}{file_prefix_zh}'.encode('utf-8')).hexdigest()

                        file_suffix = a_text_suffix
                        # file_name = f'{file_prefix}.{file_suffix}'
                    else:
                        # logger.info(f'文件名后缀 不在 已知列表中：{a_text_suffix}')
                        href_suffix = href.split("?")[0].split(".")[-1]
                        if href_suffix.lower() in file_suffix_list:
                            # file_prefix = a_text if a_text else href.split("/")[-1].split(".")[0]
                            file_prefix_zh = a_text.rsplit(".", 1)[0]
                            file_prefix = hashlib.md5(f'{doc_data["_id"]}{file_prefix_zh}'.encode('utf-8')).hexdigest()
                            file_suffix = href_suffix
                            # file_name = f'{file_prefix}.{file_suffix}'
                        else:
                            # logger.error(f'a_text 和 href都没有获取到 后缀：{href} -- {a_text}')
                            continue


                    file_name_en = f'{file_prefix}.{file_suffix}'
                    file_name_zh = f'{file_prefix_zh}.{file_suffix}'
                    file_path = f'./attachments/{dateStr}/website_attachments/{file_name_en}'
                    logger.info(f'{file_name_en} --- {file_name_zh} --- {href_link}')
                else:
                    file_path = find_href["filePath"]
                    file_name_en = find_href["filePath"].split("/")[-1]
                    file_name_zh = find_href["file_name_zh"]
                    logger.info(f'找到已下载过的附件文件：{file_name_en} --- {file_name_zh} --- {href_link}')

                # 去除特殊字符 由于不需要本地存储中文名称的附件，暂时先不清洗特殊字符
                # file_name_zh = re.sub('[/|<|:|\||>|\|"|*|?|\\\]', "", file_name_zh).strip()

                正文 = 正文.replace(href, file_path)
                # 附件 = 附件 + ";" + file_path if 附件 else file_path
                附件_list.append({"file_path": file_path, "file_name": file_name_zh})

                # 存储附件信息
                file_data = {
                    "_id": href_link,
                    "article_id": doc_data["_id"],
                    "filePath": file_path,
                    "file_name_zh": file_name_zh,
                    "downloadStatus": 0,
                    "downTime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                    "平台形式": doc_data["平台形式"],
                    "采集源名称": doc_data["采集源名称"]
                }
                save_attachments(file_data)
                # print(json.dumps(file_data, ensure_ascii=False))
            else:
                logger.error(f'a 标签没有 href属性')
                continue

        # 提取正文中的图片
        img_list = content_html.xpath("//img")
        for img_tag in img_list:
            src = img_tag.attrib.get('src', "")
            src_original = src
            if src:

                if src.endswith('lazy.gif'):
                    src_original = img_tag.get('original', "")
                src_link = urllib.parse.urljoin(doc_data["_id"], src_original)
                find_src = mengniu_attachments_col.find_one({"_id": src_link})
                if not find_src:
                    src_suffix = src_original.split("?")[0].split(".")[-1]
                    if len(src_suffix) > 4:
                        logger.error(f'url 中无法判断文件类型：{doc_data["_id"]} --- {src_link}')
                        continue
                    if src_suffix not in not_src_suffix_list:
                        src_name = hashlib.md5(src_link.encode('utf-8')).hexdigest()
                        src_path = f'./attachments/{dateStr}/website_attachments/{src_name}.{src_suffix}'
                    else:
                        continue
                else:
                    src_path = find_src["filePath"]

                正文 = 正文.replace(src, src_path)
                img_data = {
                    "_id": src_link,
                    "article_id": doc_data["_id"],
                    "filePath": src_path,
                    "file_name_zh": "",
                    "downloadStatus": 0,
                    "downTime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                    "平台形式": doc_data["平台形式"],
                    "采集源名称": doc_data["采集源名称"]
                }
                save_attachments(img_data)
                # print(json.dumps(img_data, ensure_ascii=False))
            else:
                logger.info(f'img 没有 src属性 --- {doc_data["_id"]}')

    del doc_data["status"]
    del doc_data["平台形式"]
    # del doc_data["采集时间"]
    del doc_data["数据类型"]
    try:
        del doc_data["HTML"]
    except KeyError:
        pass
    try:
        del doc_data["downtime"]
    except KeyError:
        pass
    # 处理法规摘要，因平台提取的是W_文章摘要  所以F_法规摘要替换为W_文章摘要
    F_法规摘要 = doc_data.get("F_法规摘要", None)
    if F_法规摘要:
        doc_data["W_文章摘要"] = F_法规摘要
    doc_data["export_status"] = 0
    doc_data["正文"] = 正文
    doc_data["附件"] = json.dumps(附件_list, ensure_ascii=False)
    doc_data["processTime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    try:
        db_mengniu_data_col.insert_one(doc_data)
    except DuplicateKeyError:
        logger.info(f'article 已存入该条数据: {doc_data["_id"]}')
        db_mengniu_data_col.update_one({"_id": doc_data["_id"]}, {"$set": doc_data})
        logger.success(f'processing data 更新数据成功：{doc_data["_id"]}')
        mengniu_data_original_col.update_one({"_id": doc_data["_id"]}, {"$set": {"status": 5}})
    except Exception as e:
        logger.error("save db error:{} -- {}".format(e, doc_data["_id"]))
    else:
        logger.success("解析数据完成:{}".format(doc_data["_id"]))
        mengniu_data_original_col.update_one({"_id": doc_data["_id"]}, {"$set": {"status": 5}})
    # print(json.dumps(doc_data, ensure_ascii=False))
    # save_data(doc_data)
    # print(正文)


def download_file_standard(url):

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Referer": url,
        "Host": "down.foodmate.net",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Accept-Encoding": "gzip, deflate"
    }

    retry = 0
    logger.info(f'正在下载文件：{url}')
    while retry < 5:
        try:
            # print("采集.......")
            # headers["User-Agent"] = get_UA()
            # print(url)
            # url = "https://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_pdf/90/a1/jkms-22-698.PMC2693823.pdf"
            time.sleep(1)
            file_res = requests.get(url=url, headers=headers, timeout=30, verify=False, proxies=get_proxies())    #
        except Exception as e:
            logger.error("requests error:{} -- {}".format(e, url))
            time.sleep(0.5)
            retry += 1
        else:
            if file_res.status_code == 404:
                location_url = file_res.url
                if location_url:
                    url = location_url
                    headers["Host"] = "file4.foodmate.net"
                    continue
                else:
                    time.sleep(1000)
                    logger.error(f'没获取到重定向的url：{url}')
                    continue
            elif file_res.status_code != 200:
                retry += 1
                time.sleep(100)
                logger.error(f'status != 200 :{url}')
                continue
            else:
                return file_res.content, url
    else:
        return None, None


def save_attachments(doc):
    try:
        mengniu_attachments_col.insert_one(doc)
    except DuplicateKeyError:
        logger.info("附件地址已存入该条数据:{}".format(doc["_id"]))

    except Exception as e:
        logger.error("save 附件地址 error:{} -- {}".format(e, doc["_id"]))
        # https://www.miit.gov.cn/datainfo/cpgg/art/2021/art_7cd4cf2ac3924fb89441b069c6fa9690.html
    else:
        logger.success("附件地址存储成功:{}".format(doc["_id"]))


def processingOriginalData_main():
    logger.info(f'开始processing_data')
    get_mongo_data()

    logger.success(f'processing_data main finish')


# if __name__ == '__main__':
#     processingOriginalData_main()
#     MongoClient = pymongo.MongoClient("mongodb://39.98.35.147:27117/")
#     db = MongoClient["db_mengniu"]
#     mengniu_data_original_col = db["mengniu_data_original"]
#     db_mengniu_data_col = db["db_mengniu_data"]
#     # db_mengniu_data_col = db["db_mengniu_data_online"]
#     # db_mengniu_data_col = db["db_mengniu_data_test_20250217"]
#     mengniu_attachments_col = db["mengniu_attachments"]
#
#     # db_mengniu_data_col = db["db_mengniu_data_test_wj"]
#     # mengniu_attachments_col = db["mengniu_attachments_test_wj"]
#     get_mongo_data()

