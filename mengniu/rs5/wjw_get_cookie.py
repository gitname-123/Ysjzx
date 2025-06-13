import re
import requests
from loguru import logger
import subprocess
from functools import partial
subprocess.Popen = partial(subprocess.Popen, encoding='utf-8')
import execjs

def get_rs_cookies(response):
    rs_ck1 = response.cookies.get_dict()
    logger.success("第一次请求的返回cookies=====>{}", rs_ck1)

    meta_content = re.findall(r'<meta content="(.*?)">', response.text)[0]
    rs_ts_code_url_path = re.findall(
        r'<script type="text/javascript" charset="iso-8859-1" src="(.*?)" r=\'m\'></script>', response.text)
    rs_ts_code_url = "http://www.nhc.gov.cn" + rs_ts_code_url_path[0]
    func_code = re.findall(r'<script type="text/javascript" r=\'m\'>(.*?)</script>', response.text)[0]

    logger.info(f"meta_content获取成功=====>{meta_content}")
    # print(rs_func_code_url)
    # print(ts_code)

    rs_ts_code_text = requests.get(rs_ts_code_url).text
    with open('rs5/rs_func.js', 'w', encoding='utf-8') as f:
        f.write(func_code)
    with open("rs5/rs_ts.js", "w", encoding="utf-8") as f:
        f.write(rs_ts_code_text)

    logger.warning("js文件写入本地成功")

    js_code = open("rs5/rs_main.js", "r", encoding="utf-8").read()
    js_code = js_code.replace("meta_content_replace", meta_content)
    rs5_ck2 = execjs.compile(js_code).call("get_cookie").split(";")[0]

    rs_ck = {rs5_ck2.split("=")[0]: rs5_ck2.split("=")[1]}
    rs_ck.update(rs_ck1)
    logger.success(f"瑞树最终的ck=====>{rs_ck}")
    return rs_ck

