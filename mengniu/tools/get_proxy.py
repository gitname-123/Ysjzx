import json
import requests
from fake_useragent import UserAgent
from loguru import logger
import redis
import time

#
# def get_proxies():
#     # # 青果按量代理
#     # url = "https://proxy.qg.net/allocate?Key=I35FUR4G&Num=1&AreaId=&Isp=&DataFormat=txt&DataSeparator=%5Cr%5Cn&Detail=0&Pool=1"
#     # url = "https://share.proxy.qg.net/get?key=8ZPU95MD&num=1&area=&isp=0&format=txt&seq=\r\n&distinct=true"
#     # ip = requests.get(url=url).text
#     # # ip = "117.24.80.51:60221"
#     # proxies = {
#     #     "http": "http://{}".format(ip),
#     #     "https": "http://{}".format(ip)
#     # }
#     # print(ip)
#     ip = "http://ng001.weimiaocloud.com:9003"
#     proxies = {
#         "http": ip,
#         "https": ip
#     }
#     return proxies


# 随机获取浏览器标识
def get_UA():
    try:
        # User_Agent = UserAgent().random
        User_Agent = UserAgent().chrome
        # print(User_Agent)
        return User_Agent
    except Exception as e:
        logger.error("获取随机UA报错:{}".format(e))
        User_Agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        return User_Agent


# redis_pool = redis.ConnectionPool(host='127.0.0.1', db=0, port=6379, decode_responses=True, max_connections=100)


redis_pool = redis.ConnectionPool(
    host='39.98.206.224',
    port=39941,
    password='Ysjzx221.!@#',
    db=0,
    decode_responses=True,
    max_connections=500
)



log_max_length = 1000

def get_proxies():
    conn = redis.Redis(connection_pool=redis_pool)
    while True:
        ip = conn.rpop("proxy:proxy_wj")
        if ip:
            proxies = {
                "http": "http://{}".format(ip),
                "https": "http://{}".format(ip)
            }
            conn.close()
            return proxies
        else:
            logger.error("ip池空啦")
            time.sleep(1)
print('实例化redis连接池')