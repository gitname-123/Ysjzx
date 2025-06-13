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


def exportData_to_SQL():

    query_doc = {"$and":[{"F_法规摘要":{"$exists": True}}, {"F_法规摘要": {"$ne": ""}}]}
    # query_doc = {"processTime": {"$gte": "2025-04-16 00:00:00"}}
    logger.info(f'开始导出数据至sql：从mongo中查询数据：{query_doc}')
    # query_doc = {}
    mongo_cursor = db_mengniu_data_col.find(query_doc, {"_id": 1, "F_法规摘要": 1, "标题": 1, "采集源名称": 1})# .limit(1)
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
    sql_cursor = conn.cursor()

    sourceName = result["采集源名称"]
    F_法规摘要 = result["F_法规摘要"]
    if not F_法规摘要:
        logger.error(f'没有法规摘要：{result["_id"]}')
        return
    # logger.info(f'{sourceName} -- {result["_id"]}')

    sql = r"""UPDATE dbo.[Data_Content] SET [W_articleAbstract]=%s WHERE [detailUrl]=%s;"""
    arg = (F_法规摘要, result["_id"])
    sql_cursor.execute(sql, tuple(arg))
    conn.commit()
    sql_cursor.close()


def main_schedule():

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


