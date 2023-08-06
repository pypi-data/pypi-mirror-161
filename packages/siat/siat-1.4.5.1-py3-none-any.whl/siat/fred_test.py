# -*- coding: utf-8 -*-

import pandas as pd
#if you get an error after executing the code, try adding below:
pd.core.common.is_list_like = pd.api.types.is_list_like

import pandas_datareader.data as web
import datetime

start = datetime.datetime(2021, 1, 1)
end = datetime.datetime(2021, 11, 30)

sp500 = web.DataReader(['sp500'], 'fred', start, end)
djia = web.DataReader(['djia'], 'fred', start, end)

hk50 = web.DataReader(['hk50'], 'fred', start, end) #失败

def get_index_fred(ticker,start,end):
    """
    功能：替代雅虎不能用的临时解决方案，获取标普500、道琼斯等指数
    """
    yahoolist=['^GSPC','^DJI','^VIX','^IXIC','^N225','^NDX']
    fredlist=['sp500','djia','vixcls','nasdaqcom','nikkei225','nasdaq100']
    
    if not (ticker in tidailist):
        return None
    
    import pandas as pd
    import pandas_datareader.data as web
    if ticker in yahoolist:
        pos=yahoolist.index(ticker)
        id=fredlist[pos]
        
        df = web.DataReader([id], 'fred', start, end)
        df.rename(columns={id:'Close'},inplace=True)
    
    #删除空值记录
    df.dropna(inplace=True)
    
    return df
