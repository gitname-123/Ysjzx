
from wanfang.common.get_proxy import get_proxies
from curl_cffi import requests as requests_cffi
import requests

headers = {
    'authority': 'efsa.onlinelibrary.wiley.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'zh-CN,zh;q=0.9',
    'sec-ch-ua': '"Chromium";v="109", "Not_A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
}

# response = requests.get(
#     'https://efsa.onlinelibrary.wiley.com/cms/asset/4ecf09d7-ec87-4aff-bf58-6ce4f968febd/efs28554-fig-0030-m.png',
#     headers=headers,
#     proxies=get_proxies()
# )
s = requests_cffi.Session()
url = "https://efsa.onlinelibrary.wiley.com/cms/asset/4ecf09d7-ec87-4aff-bf58-6ce4f968febd/efs28554-fig-0030-m.png"
response = s.get(url, impersonate="chrome110", proxies=get_proxies())

print(response.text)
print(response.status_code)
