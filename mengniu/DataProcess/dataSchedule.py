import time

import pymssql
# import pyodbc
from loguru import logger
from queue import Empty, Queue
from threading import Thread

import processingOriginalData
import uploadFile
import processingWechatData
import downloadFile

import sys
sys.path.append('../')
from tools.settings import db_mengniu_data_col, today


field_zh_en_mappings = [
    ("标题", "title"),
    ("网站发布时间", "publishTime"),
    ("文章地址URL", "detailUrl"),
    ("采集源名称", "sourceName"),
    ("正文", "content"),
    ("附件", "attachments"),
    ("采集时间", "downTime"),
    ("W_文章来源", "W_articleSource"),
    ("W_文章摘要", "W_articleAbstract"),
    ("W_地区", "W_Area"),
    ("W_行业", "W_industry"),
    ("F_法规名称", "F_statuteName"),
    ("F_发布文号", "F_publishNo"),
    ("F_专业属性", "F_specialtyAttr"),
    ("F_发布单位", "F_publisher"),
    ("F_发布日期", "F_publishDate"),
    ("F_生效日期", "F_effectDate"),
    ("F_废止日期", "F_annulDate"),
    ("F_有效性状态", "F_status"),
    ("F_属性", "F_attr"),
    ("F_备注", "F_remark"),
    ("B_标准编号", "B_standardNo"),
    ("B_标准名称", "B_standardName"),
    ("B_标准类别", "B_standardCategory"),
    ("B_发布日期", "B_publishDate"),
    ("B_标准状态", "B_status"),
    ("B_实施日期", "B_implementDate"),
    ("B_颁发部门", "B_publisher"),
    ("B_废止日期", "B_annulDate"),
    ("B_标准介绍", "B_standardAbstract"),
    ("CF_行政处罚决定文书号", "CF_No"),
    ("CF_当事人名称", "CF_Name"),
    ("CF_处罚日期", "CF_Date"),
    ("CF_处罚机关", "CF_Organ"),
    ("CF_处罚内容", "CF_Content"),
    ("CF_处罚种类", "CF_Type"),
    ("CF_处罚依据", "CF_Basis"),
    ("预警原因", "CF_ForewarningReason")
]


def exportData_to_SQL():

    dateStr = today + " 00:00:00"
    query_doc = {"export_status": 0}
    # query_doc = {"processTime": {"$gte": "2025-04-16 00:00:00"}}
    logger.info(f'开始导出数据至sql：从mongo中查询数据：{query_doc}')
    # query_doc = {}
    mongo_cursor = db_mengniu_data_col.find(query_doc)# .limit(10)
    results = list(mongo_cursor)
    mongo_cursor.close()
    logger.info(f'从mongo中查出{len(results)}条数据，准备存入sql')
    queue = Queue(maxsize=0)

    # 创建一个名为的新线程producer_thread并立即启动它


    threads = []
    # 可以调节线程数
    threadNum = 1
    # 创建一个名为的守护线程consumer并立即启动它。
    for result in results:
        queue.put(result)

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
            insert_data(task)

        except Empty:
            logger.info("queue is Empty")
            time.sleep(1)
            return
        except Exception as e:
            logger.error("consumer get_detail error:{} --- {}".format(e, task))
            time.sleep(0.1)
            queue.task_done()
        else:
            # logger.success(f'done: {task["_id"]}')
            # time.sleep(random.randint(4,8))
            queue.task_done()

def insert_data(result):
    # 处理食品伙伴网数据，如果有效性状态为空 且 标题 包含【草案】两个字，就将有效性状态改为"草案"
    sourceName = result["采集源名称"]
    title = result["标题"]
    F_status = result.get("F_有效性状态", "")
    if (not F_status) and sourceName.__contains__("食品伙伴网") and title.__contains__("草案"):
        result["F_有效性状态"] = "草案"

    sql_cursor = conn.cursor()
    sql_cursor.execute('select [detailUrl] from dbo.[Data_Content] where [detailUrl]=%s', result["文章地址URL"])
    find_result = sql_cursor.fetchone()
    arg = []
    for field_item in field_zh_en_mappings:
        field_zh_name = field_item[0]
        # field_en_name = field_item[1]
        arg.append(result.get(field_zh_name, ""))

    # 如果采集过 更新全部字段
    if find_result:
        sql = r"""UPDATE dbo.[Data_Content] SET [title]=%s,[publishTime]=%s,[detailUrl]=%s,[sourceName]=%s,[content]=%s,[attachments]=%s,[downTime]=%s,[W_articleSource]=%s,[W_articleAbstract]=%s,[W_Area]=%s,[W_industry]=%s,[F_statuteName]=%s,[F_publishNo]=%s,[F_specialtyAttr]=%s,[F_publisher]=%s,[F_publishDate]=%s,[F_effectDate]=%s,[F_annulDate]=%s,[F_status]=%s,[F_attr]=%s,[F_remark]=%s,[B_standardNo]=%s,[B_standardName]=%s,[B_standardCategory]=%s,[B_publishDate]=%s,[B_status]=%s,[B_implementDate]=%s,[B_publisher]=%s,[B_annulDate]=%s,[B_standardAbstract]=%s,[CF_No]=%s,[CF_Name]=%s,[CF_Date]=%s,[CF_Organ]=%s,[CF_Content]=%s,[CF_Type]=%s,[CF_Basis]=%s,[CF_ForewarningReason]=%s WHERE [detailUrl]=%s;"""
        # arg = [result["标题"], result["正文"], result["B_标准名称"], result["B_标准状态"],
        #        result["文章地址URL"]]  # result["正文"]
        arg.append(result["文章地址URL"])
        sql_cursor.execute(sql, tuple(arg))
        conn.commit()
        logger.success(f'sql更新数据成功：{result["文章地址URL"]}')
        db_mengniu_data_col.update_one({"_id": result["_id"]}, {"$set": {"export_status": 5}})
    else:

        # print(arg)
        # print(len(arg))
        try:
            sql = r"""INSERT INTO dbo.[Data_Content]([title],[publishTime],[detailUrl],[sourceName],[content],[attachments],[downTime],[W_articleSource],[W_articleAbstract],[W_Area],[W_industry],[F_statuteName],[F_publishNo],[F_specialtyAttr],[F_publisher],[F_publishDate],[F_effectDate],[F_annulDate],[F_status],[F_attr],[F_remark],[B_standardNo],[B_standardName],[B_standardCategory],[B_publishDate],[B_status],[B_implementDate],[B_publisher],[B_annulDate],[B_standardAbstract],[CF_No],[CF_Name],[CF_Date],[CF_Organ],[CF_Content],[CF_Type],[CF_Basis],[CF_ForewarningReason])VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"""
            sql_cursor.execute(sql, tuple(arg))
            conn.commit()
        except Exception as e:
            logger.error(f'insert error:{e} ---{result["标题"]}')
        else:
            logger.success(f'一条数据往sql存储成功：{result["标题"]}')
            db_mengniu_data_col.update_one({"_id": result["_id"]}, {"$set": {"export_status": 5}})
    sql_cursor.close()


def main_schedule():
    processingOriginalData.processingOriginalData_main()

    processingWechatData.processingWechatData_main()

    downloadFile.downloadFile_main()
    #
    uploadFile.uploadFile_main()
    #
    exportData_to_SQL()


if __name__ == '__main__':

    # conn_str = (
    #     r'DRIVER={SQL Server Native Client 10.0};'
    #     r'SERVER=101.42.46.118:1433;'
    #     r'DATABASE=mengniu;'
    #     r'UID=sa;'
    #     r'PWD=wfdata1!'
    # )
    # conn = pyodbc.connect(conn_str)
    server = '101.42.46.118:1433'
    user = 'sa'
    password = 'wfdata1!'
    database = 'mengniu'

    # 创建连接
    conn = pymssql.connect(server, user, password, database, tds_version='7.0')
    # cursor = conn.cursor()
    if conn:
        print("连接成功")

    main_schedule()  # 51843
    # exportData_to_SQL()

    conn.close()


