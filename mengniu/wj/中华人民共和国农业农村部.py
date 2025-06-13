import urllib
import requests
import time
import warnings
from bs4 import BeautifulSoup
warnings.filterwarnings("ignore")
from datetime import datetime
from loguru import logger
from lxml import etree
import sys
sys.path.append('../')
from tools.get_proxy import get_proxies
from tools.save import save_articles
from tools.settings import mengniu_data_original_col, MongoClient
import subprocess
from functools import partial
subprocess.Popen = partial(subprocess.Popen, encoding='utf-8')
from feapder.utils import metrics


# url_set = set()
class MoaGov(object):

    def __init__(self):
        self.list_url = None
        self.column_domain = None
        self.page = None
        self.detail_url = None
        self.publish_time = None
        self.title = None
        self.column = None

    def scheduler(self):
        column_list = [
            # # #政策法规
            ("zcfg/fl", "中华人民共和国农业农村部", "农业农村部-政策法规-法律"),
            ("zcfg/xzfg", "中华人民共和国农业农村部", "农业农村部-政策法规-行政法规"),
            ("zcfg/gfxwj", "中华人民共和国农业农村部", "农业农村部-政策法规-部门规章"),
            ("zcfg/nybgz", "中华人民共和国农业农村部", "农业农村部-政策法规-规范性文件"),
            ("zcfg/qnhnzc", "中华人民共和国农业农村部", "农业农村部-政策法规-政策"),
            # # 通知公告
            ("tzgg_1/bl", "中华人民共和国农业农村部", "农业农村部-通知公告-部令"),
            ("tzgg_1/gg", "中华人民共和国农业农村部", "农业农村部-通知公告-公告"),
            ("tzgg_1/tz", "中华人民共和国农业农村部", "农业农村部-通知公告-通知"),
            ("tzgg_1/tfw", "中华人民共和国农业农村部", "农业农村部-通知公告-其他"),

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
            if self.page == 1:
                page_arg = "index"
            else:
                page_arg = f"index_{self.page - 1}"
            headers = {
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Host': 'www.moa.gov.cn',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            }
            try:
                # time.sleep(2)
                self.list_url = f'http://www.moa.gov.cn/gk/{self.column_domain}/{page_arg}.htm'
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

                response.encoding = 'utf-8'
                # print(response.text)
                response_html = etree.HTML(response.text)
                li_list = response_html.xpath('//ul[@class="commonlist"]/li')
                if not li_list:
                    logger.info(f'列表页没 li  -- 程序结束 --- {response.text}')
                    return
                logger.info(f'column:{self.column[2]} --- {self.page} --- 列表页数量：{len(li_list)}')
                for li in li_list:
                    self.title = ''.join([title_text.strip() for title_text in li.xpath('./a//text()') if title_text])
                    if not self.title:
                        logger.error(f'没获取到title')
                        # time.sleep(100000)
                        continue

                    self.detail_url = urllib.parse.urljoin(self.list_url, li.xpath('./a/@href')[0])
                    if not str(self.detail_url).endswith('htm'):
                        logger.error(f'详情页链接异常{self.detail_url}')
                        time.sleep(10)
                        continue
                    self.publish_time = li.xpath('./span/text()')[0]
                    logger.info(f'{self.publish_time} -- {self.detail_url} --- {self.title}')

                    # # if self.detail_url not in url_set:
                    # #     url_set.add(self.detail_url)
                    # # else:
                    # #     logger.error(f'出现重复数据：{self.detail_url} --- {self.column_domain} -- {self.page}')
                    #
                    # # self.publish_time = li.xpath('./span[@class="f_r px11 f_gray"]/text()')[0].split(' ')[0]
                    # # if self.publish_time < "2024-01-01":
                    # #     logger.info(f'只采集近一年的数据：{self.publish_time}')
                    # #     return
                    #
                    find_detail_url = mengniu_data_original_col.find_one({"_id": self.detail_url})
                    if find_detail_url:
                        logger.info(f'已经采集过：{self.detail_url}, {self.title}')
                        # continue
                        return
                        # return
                    self.get_detail()
                    # return
                self.page += 1
                # return

    def get_detail(self):
        logger.info(f'process {self.column[2]} -- {self.page} -- {self.title} -- {self.detail_url}')
        while True:
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                # 'Connection': 'keep-alive',
                # 'Cookie': 'td_cookie=2477801757; bc08_f0d8_saltkey=VVoM94Jk; bc08_f0d8_lastvisit=1740034105; td_cookie=2327170393; bc08_f0d8_lastact=1740703541%09api.php%09js; Hm_lvt_2aeaa32e7cee3cfa6e2848083235da9f=1740442869,1740550832,1740637704,1740703542; HMACCOUNT=5E3DCAD3DF824D60; __51cke__=; Hm_lpvt_2aeaa32e7cee3cfa6e2848083235da9f=1740704390; __tins__18962677=%7B%22sid%22%3A%201740703544056%2C%20%22vd%22%3A%2014%2C%20%22expires%22%3A%201740706189897%7D; __51laig__=14',
                # 'Referer': 'http://info.foodmate.net/reading/list-4.html',
                'Upgrade-Insecure-Requests': '1',
                'Host': 'www.moa.gov.cn',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            }
            try:
                # time.sleep(2)
                # self.detail_url = "http://www.moa.gov.cn/govpublic/ZZYGLS/202410/t20241016_6464460.htm"
                response = requests.get(
                    url=self.detail_url,
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
                    if response.status_code == 404:
                        return
                    continue
                response.encoding = "utf-8"
                # res_text = html.unescape(response.text)
                # print(res_text)
                # return
                response_html = etree.HTML(response.text)

                if not response.text.__contains__("gsj_htmlcon_bot"):
                    logger.error(f'正文中没有 gsj_htmlcon_bot:{response.status_code} --- {response.text}')
                    # time.sleep(100)
                    return
                    # continue

                publish_time = response_html.xpath('//p[@class="pubtime"]/text()')[0].replace('发布时间：', '').strip().replace('年', '-').replace('月', '-').replace('日', '')
                if publish_time:
                    self.publish_time = publish_time
                # 来源
                F_法规来源_xpath = response_html.xpath('//p[@class="pubtime source"]/text()')
                F_法规来源 = F_法规来源_xpath[0].replace('来源：', '').strip() if F_法规来源_xpath else ""

                # 用BeautifulSoup解析HTML
                soup = BeautifulSoup(response.text, 'html.parser')

                jiedu = soup.find('p', id='jdlj')
                if jiedu:
                    jiedu.decompose()
                # 将BeautifulSoup对象转换为字符串
                content_str = str(soup.find(name='div', attrs={'class': 'gsj_htmlcon_bot'}))

                fujian_content_soup = soup.find(name='div', attrs={'class': 'nyb_fj nyb_fj1'})

                content_str = content_str + '\n' + str(fujian_content_soup) if fujian_content_soup else content_str

                # content_div = response_html.xpath('//div[@id="gsj_htmlcon_bot"]')
                # content_str = html.unescape(etree.tostring(content_div[0], encoding="utf-8").decode())
                # print(content_str)
                # print(W_文章来源)

                # 获取法规相关信息 文章头部表格信息内容
                content_head_div = response_html.xpath('//div[@class="content_head mhide"]')
                if content_head_div:

                    F_发布文号_xpath = content_head_div[0].xpath('.//dt[contains(text(), "文　　号")]/following-sibling::dd[1]/text()')
                    F_发布文号 = F_发布文号_xpath[0].strip() if F_发布文号_xpath else ""

                    F_发布日期_xpath = content_head_div[0].xpath('.//dt[contains(text(), "发布日期")]/following-sibling::dd[1]/text()')
                    F_发布日期 = F_发布日期_xpath[0].strip().replace('年', '-').replace('月', '-').replace('日', '') if F_发布日期_xpath else ""

                    F_发布单位_xpath = content_head_div[0].xpath('.//dt[contains(text(), "信息所属单位")]/following-sibling::dd[1]/text()')
                    F_发布单位 = F_发布单位_xpath[0].strip() if F_发布单位_xpath else ""

                    F_生效日期_xpath = content_head_div[0].xpath('.//dt[contains(text(), "生效日期")]/following-sibling::dd[1]/text()')
                    F_生效日期 = F_生效日期_xpath[0].strip().replace('年', '-').replace('月', '-').replace('日', '') if F_生效日期_xpath else ""

                    F_法规摘要_xpath = content_head_div[0].xpath('.//dt[contains(text(), "内容概述")]/following-sibling::dd[1]/text()')
                    F_法规摘要 = F_法规摘要_xpath[0].strip() if F_法规摘要_xpath else ""
                    logger.info(f'{F_发布文号} -- {F_发布日期} -- {F_发布单位} -- {F_生效日期} --{self.detail_url}')

                else:
                    F_发布文号 = ""
                    F_发布单位 = ""
                    F_发布日期 = ""
                    F_生效日期 = ""
                    F_法规摘要 = ""

                data = {
                    "_id": self.detail_url,
                    "标题": self.title,
                    "网站发布时间": self.publish_time,
                    "文章地址URL": self.detail_url,
                    "采集源名称": self.column[1],
                    "正文": content_str,
                    "HTML": response.text,
                    "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": 0,
                    "平台形式": "网站",
                    "数据类型": "法规",
                    "F_法规名称": self.title,
                    "F_发布文号": F_发布文号,
                    # "F_专业属性": F_专业属性,
                    "F_发布单位": F_发布单位,
                    "F_发布日期": F_发布日期,
                    "F_生效日期": F_生效日期,
                    # "F_废止日期": F_废止日期,
                    # "F_有效性状态": self.F_有效性状态,
                    # "F_属性": F_属性,
                    # "F_备注": F_备注,
                    "F_法规来源": F_法规来源,
                    "F_法规摘要": F_法规摘要,
                }
                if save_articles(data):
                    metrics.emit_counter("详情页采集量", count=1, classify=f"{self.column[2]}")
                # print(json.dumps(data, ensure_ascii=False))
                return


def test_detail():
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        # 'Cache-Control': 'max-age=0',
        # 'Connection': 'keep-alive',
        # 'Cookie': '__jsluid_s=972b6f40b84c65a0c078361aabe9b6d2; Hm_lvt_54db9897e5a65f7a7b00359d86015d8d=1741853185; HMACCOUNT=57289C7935A0865A; Hm_lpvt_54db9897e5a65f7a7b00359d86015d8d=1741853514; _jsearchq=%u8D22%u653F%3A',
        # 'If-Modified-Since': 'Thu, 13 Mar 2025 01:27:55 GMT',
        # 'If-None-Match': 'W/"67d2349b-7525"',
        # 'Sec-Fetch-Dest': 'document',
        # 'Sec-Fetch-Mode': 'navigate',
        # 'Sec-Fetch-Site': 'none',
        # 'Sec-Fetch-User': '?1',
        # 'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        # 'sec-ch-ua': '"Chromium";v="109", "Not_A Brand";v="99"',
        # 'sec-ch-ua-mobile': '?0',
        # 'sec-ch-ua-platform': '"Windows"',
    }

    response = requests.get(
        'https://www.samr.gov.cn/zw/zfxxgk/fdzdgknr/zljds/art/2025/art_954e41dd22994ecfa93ee90683694362.html',
        proxies=get_proxies(),
        headers=headers,
    )
    print(response.text)
    print(response.status_code)


def test_list():
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        # 'Cookie': 'td_cookie=3952993517; http_waf_cookie=1bfd932e-d6d8-40a7f7b00de9d33aab5a96c907150c6eddd4; _yfxkpy_ssid_10002896=%7B%22_yfxkpy_firsttime%22%3A%221742177788867%22%2C%22_yfxkpy_lasttime%22%3A%221742177788867%22%2C%22_yfxkpy_visittime%22%3A%221742177788867%22%2C%22_yfxkpy_cookie%22%3A%2220250317101628871929084572760521%22%7D; wdcid=2a696930f98ec506; wdses=61fb3059393b9407; _trs_uv=m8cftbna_299_2ql1; _trs_ua_s_1=m8cftbna_299_6cdi; wdlast=1742178914',
        # 'Referer': 'http://www.moa.gov.cn/gk/zcfg/fl/index_1.htm',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    }

    response = requests.get('http://www.moa.gov.cn/gk/zcfg/fl/index_1.htm', proxies=get_proxies(), headers=headers,
                            verify=False)
    response.encoding = 'utf-8'
    print(response.text)
    print(response.status_code)


def test_detail_2():
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        # 'Connection': 'keep-alive',
        # 'Cookie': 'td_cookie=3953236211; http_waf_cookie=1bfd932e-d6d8-40a7f7b00de9d33aab5a96c907150c6eddd4; wdcid=2a696930f98ec506; wdses=61fb3059393b9407; _trs_uv=m8cftbna_299_2ql1; _trs_ua_s_1=m8cftbna_299_6cdi; wdlast=1742179631; _yfxkpy_ssid_10002896=%7B%22_yfxkpy_firsttime%22%3A%221742177788867%22%2C%22_yfxkpy_lasttime%22%3A%221742177788867%22%2C%22_yfxkpy_visittime%22%3A%221742179630845%22%2C%22_yfxkpy_cookie%22%3A%2220250317101628871929084572760521%22%7D',
        # 'Referer': 'http://www.moa.gov.cn/govpublic/YYJ/202411/t20241119_6466464.htm',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    }

    response = requests.get(
        'http://www.moa.gov.cn/govpublic/YYJ/202411/t20241119_6466464.htm',
        proxies=get_proxies(),
        headers=headers,
        verify=False,
    )
    response.encoding = 'utf-8'
    print(response.text)
    print(response.status_code)


if __name__ == '__main__':
    metrics.init()

    obj = MoaGov()
    obj.scheduler()
    # test_list()
    # test_detail()
    metrics.close()
    MongoClient.close()
