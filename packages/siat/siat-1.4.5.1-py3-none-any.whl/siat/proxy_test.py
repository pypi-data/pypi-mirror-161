# -*- coding: utf-8 -*-

import pandas_datareader.data as web
import requests
import urllib

proxy_addr=['3.211.65.185:80',
            '47.52.3.320:443',
            '103.218.3.93:3128',
            '119.28.60.130:80',
            '203.174.112.13:3128',
            '123.176.103.44:80',
            '65.51.126.74:8080',
            '142.44.221.126:8080',
            '38.143.68.18:3128',
            '216.125.236.84:80',
            ]
#设置和测试代理1
headers = { "Accept":"application/json",
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            "Accept-Encoding":"none",
            "Accept-Language":"en-US,en;q = 0.8",
            "Connection":"keep-alive",
            "Referer":"https://cssspritegenerator.com",
            "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"
            }

for pa in proxy_addr:
    proxies = {'http': pa}
    with requests.Session() as s:
        s.headers = headers
        s.proxies.update(proxies)
    try:
        gspc = web.DataReader('^GSPC', 'yahoo', '2021-11-1', '2021-11-5', session=s)
    except:
        print("  Warning! Failed proxy",pa)
        continue
    else:
        print("  Success! Found workable proxy",pa)
        break
#设置和测试代理2
for pa in proxy_addr:
    proxies = {'http': pa}
    proxy_support = urllib.request.ProxyHandler(proxies)
    opener = urllib.request.build_opener(proxy_support)
    urllib.request.install_opener(opener)
    
    try:
        tsla = web.DataReader("TSLA", 'yahoo', '2021-11-1', '2021-11-5')
    except:
        print("  Warning! Failed proxy",pa)
        continue
    else:
        print("  Success! Found workable proxy",pa)
        break
    
#设置和测试代理3
for pa in proxy_addr: 
    proxies = {'http': pa}
    try:
        r = requests.get(f"http://httpbin.org/ip", proxies=proxies)
        rj=r.json()
    except:
        print("  Warning! Failed proxy",pa)
        continue
    else:
        print("  Success! Found workable proxy",pa)
        continue
    
#===========================================================================
import requests
import pandas as pd

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36'
}

#抓取代理服务器地址
i = 1000
url = f'https://www.kuaidaili.com/free/inha/{i}/'
r = requests.get(url, headers=headers)
r.encoding = 'u8'
ip_df, = pd.read_html(r.text)
ip_df
