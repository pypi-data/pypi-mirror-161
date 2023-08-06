# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

def kpl_stock_concept():
    """
    功能：抓取开盘啦网站的概念股明细
    """
    import pandas as pd
    import json
    import requests
    import random
    
    url = 'https://pchq.kaipanla.com/w1/api/index.php'
    concept_label = []
    label_df = pd.DataFrame()

    # 获取概念ID
    #USER_AGENTS列表，随即使用，以便避过反爬虫机制
    ua_list = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
    ]
    session=requests.Session()
    for i in range(0,500,5):
        param1 = {'c': 'PCArrangeData', 'a': 'GetZSIndexPlate', 'SelType': 2, 'ZSType': 5, 'PType': 2, 'POrder': 1,
                       'PStart': '', 'PEnd': '', 'PIndex': i, 'Pst': 15, 'UserID': '399083','Token': '2292739880d01bd81e169e90a1898ebe'}

        html1 = json.loads(session.post(url=url, headers={'User-Agent': random.choice(ua_list)}, data=param1).text)
        if len(html1['plates']['list']) != 0:
            label_df = label_df.append(html1['plates']['list'],ignore_index=True)
        else:
            break
    label_df = label_df.iloc[:,0:2]
    label_df.columns = ['label','concept']

    # 获取概念股明细
    stock_df = pd.DataFrame()
    label_list=label_df['label'].tolist()
    concept_list=label_df['label'].tolist()
    for label in label_df['label'].tolist():
        pos=label_list.index(label)
        print("Processing",concept_list[pos],"\b,",pos+1,"of",len(label_list))
        for j in range(0,500,5):
            param2 = {'c': 'PCArrangeData', 'a': 'GetZSIndexPlate', 'SelType': 3, 'LType': 6, 'LOrder': 1,
                             'LStart': '', 'LEnd': '', 'LIndex': j, 'Lst': 15, 'PlateID': label, 'UserID': '399083',
                             'Token': '2292739880d01bd81e169e90a1898ebe'}

            html2 = json.loads(session.post(url=url, headers={'User-Agent': random.choice(ua_list)}, data=param2).text)
            #print(html2)
            if len(html2['stocks']['list']) != 0:
                data = pd.DataFrame(html2['stocks']['list'])
                #print(data)
                data['label'] = label
                stock_df = stock_df.append(data, ignore_index=True)
            else:
                break

    stock_df = stock_df.iloc[:, [0, 1, 13]]
    stock_df.columns = ['scode', 'sname','label']

    stock_concept_detail_df = pd.merge(stock_df, label_df)

    stock_concept_detail_df.rename({'symbol': 'scode', 'name': 'sname', '板块': 'concept'}, axis='columns', inplace=True)

    stock_concept_detail_df = stock_concept_detail_df[['scode', 'sname', 'concept']]
    stock_concept_detail_df['scode'] = stock_concept_detail_df['scode'].apply(lambda x: (x + ".SH") if x.startswith('6') == True else (x + ".SZ"))
    stock_concept_detail_df.drop_duplicates(inplace=True)

    stock_concept_detail_df.sort_values(by=['scode'],inplace=True)
    #print(stock_concept_detail_df.head(5))
    print('Completed.')
    return stock_concept_detail_df



