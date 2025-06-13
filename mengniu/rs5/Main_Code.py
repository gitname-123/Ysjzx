from loguru import logger
import subprocess
from functools import partial
subprocess.Popen = partial(subprocess.Popen, encoding="utf-8")
import requests,re,execjs
from wanfang.common.get_proxy import get_proxies


headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
}
response = requests.get("http://www.nhc.gov.cn/wjw/xinw/xwzx.shtml", headers=headers, verify=False)
rs_ck1_dict=response.cookies.get_dict()
logger.success("第一次请求的返回cookies=====>{}",rs_ck1_dict)
# logger.error("请求内容=====>{}",response.text)
meta_content=re.findall(r'<meta content="(.*?)">',response.text)[0]
rs_ts_code_url_path=re.findall(r'<script type="text/javascript" charset="iso-8859-1" src="(.*?)" r=\'m\'></script>',response.text)
rs_ts_code_url="http://www.nhc.gov.cn"+rs_ts_code_url_path[0]
func_code=re.findall(r'<script type="text/javascript" r=\'m\'>(.*?)</script>',response.text)[0]
#
logger.debug("meta_content获取成功=====>{}",meta_content)
# print(rs_func_code_url)
# print(ts_code)

rs_ts_code_text=requests.get(rs_ts_code_url).text
with open('rs_func.js', 'w', encoding='utf-8') as f:
    f.write(func_code)
with open("rs_ts.js", "w", encoding="utf-8") as f:
    f.write(rs_ts_code_text)

logger.warning("js文件写入本地成功")

js_code=open("./rs_main.js", "r", encoding="utf-8").read()
js_code=js_code.replace("meta_content_replace", meta_content)
rs5_ck2=execjs.compile(js_code).call("get_cookie").split(";")[0]

rs5_ck2_name=rs5_ck2.split("=")[0]
rs5_ck2_value=rs5_ck2.split("=")[1]
rs_ck={rs5_ck2_name:rs5_ck2_value}
rs_ck.update(rs_ck1_dict)
logger.debug("瑞树最终的ck=====>{}",rs_ck)


# rs_ck = {'sVoELocvxVW0T': '5ReuESbIQnt3qqqDYzvroOqYm2g8srZnCHM.7OLceHMHmMxicy6IhareIBw2g9L.FvBpi7w52wmvrPNHp01949d8n3XU9k7xqOBQ4RHspUVljHbKp83enieic6NTlxQjxN6YZ_GNfjr77FkmewCNM9D8P.jr6ZYFuYqJDob16uASa', 'sVoELocvxVW0S': '5ckZEtPUpfVd5xu0SJ0z_FkqU3t22xtkgIwfC8PKmLy6DTDsiwV1pV7Unlciypqm86i3dJJGihjv_3ixUzeu4YA', 'insert_cookie': '91349450'}

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Referer": "http://www.nhc.gov.cn/wjw/xinw/xwzx.shtml",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
}
cookies = {
    "sVoELocvxVW0S": "5ShzRBA3RThagmobEjjkRITvIbFn.4MfM_g0sttQW0kt8AkmxH09bRr90Xs1aaTkuLcR7hdK8jG.4PgKfMaL0bG",
    "insert_cookie": "96260894",
    "sVoELocvxVW0T": "5Rej7CDIF.mQqqqDY.OWzoGtkkLY3tp2ygEq.zmmfHfiJIbK0rj8NzUS46cmtjjBeNoYQdpj0CMABZaI2SwJBaE37U3ForWVZKHqcYb1L0m4qK_dgzReKsFfbVRBG8BZYjMtjWK_BtaLVzBlhb9gRtZKJh7PBBep3hay2b3oGNS8c.2BebDFAb.WqpK1Y8JS8ld_U0qYowJ5asGJW13JQAWzKd2xdmRptagRDRSFTg83q"
}
response = requests.get("http://www.nhc.gov.cn/wjw/gfxwjj/list_6.shtml", headers=headers, cookies=rs_ck, verify=False, proxies=get_proxies())
if response.status_code==200:
    logger.success("响应码=====>{}",response)
    logger.success("瑞树请求成功=====>{}",response.text)
else:
    logger.error("瑞树请求失败=====>{}",response)


# response = requests.get("http://www.nhc.gov.cn/xcs/s7852/202405/e7cc97ec3c134a0ca5e36d72ef41781a.shtml", headers=headers, cookies=rs_ck, verify=False, proxies=get_proxies())
# if response.status_code==200:
#     logger.success("响应码=====>{}",response)
#     logger.success("瑞树请求成功=====>{}",response.text)
# else:
#     logger.error("瑞树请求失败=====>{}",response)
#
