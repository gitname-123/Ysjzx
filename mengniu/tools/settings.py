import time
import pymongo


MongoClient = pymongo.MongoClient("mongodb://39.98.35.147:27117/")

# 网站采集库
db = MongoClient["db_mengniu"]
# 采集原始数据库
mengniu_data_original_col = db["mengniu_data_original"]
# 最终提交数据库
db_mengniu_data_col = db["db_mengniu_data"]
# 附件库
mengniu_attachments_col = db["mengniu_attachments"]

# 微信公众号采集库
# todo_wechat_article_col = db["todo_mengniu_wechat_article"]
db = MongoClient["db_references_wj"]
# 微信公众号实时监听总库
db_wechat_article_monitor = db["db_wechat_article_monitor"]


# today = time.strftime("%Y-%m-%d", time.localtime())

# 服务器上 "2025-06-06"  "2025-06-07" 两个没有上传成功
today = "2025-05-21"

"""
压缩文件夹命令
feapder zip "D:\wangjing\Work\PycharmProjects\python311\wanfang\mengniu" .\mengniu.zip

生成requirements命令
pipreqs . --encoding=utf8 --force
"""

