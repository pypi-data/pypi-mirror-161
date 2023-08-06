# -*- coding: utf-8 -*-

import os; os.chdir("S:/siat")
from siat import *

#==============================================================================
if __name__=='__main__':
    yahoo_index='^VIX'
    start='19910101'
    end='20101231'
    freq='daily'

def get_index_investing(yahoo_index,start,end,freq='daily'):
    """
    功能：获得全球指数历史行情
    数据源：https://cn.investing.com/indices/
    输入：雅虎财经指数代码
    输出：历史行情df
    注意：
    """
    import pandas as pd
    freq_cvt=pd.DataFrame([
        ['daily','每日'],['weekly','每周'],['monthly','每月'],
        ], columns=['freq','freq_investing'])
    try:
        freq_investing=freq_cvt[freq_cvt['freq']==freq]['freq_investing'].values[0]
    except:
        #未查到
        freq_investing='每日'

    index_cvt=pd.DataFrame([
        ['^RUT','美国','罗素2000小盘股'],['^VIX','美国','VIX恐慌指数'],
        
        
        
        
        
        ], columns=['yahoo_index','country','investing_index'])

    try:
        country=index_cvt[index_cvt['yahoo_index']==yahoo_index]['country'].values[0]
        investing_index=index_cvt[index_cvt['yahoo_index']==yahoo_index]['investing_index'].values[0]
    except:
        #未查到
        return None
    
    
    import akshare as ak
    df = ak.index_investing_global(country=country, index_name=investing_index, \
                                   period=freq_investing, start_date=start, end_date=end)
    print(index_investing_global_df)            


df = ak.index_investing_global(country="美国", index_name="VIX恐慌指数", period="每月", start_date="2005-01-01", end_date="2020-06-05")
ak.index_investing_global_country_name_url("美国") 


 ak.index_investing_global(country="美国", index_name="VIX恐慌指数", period="每月", start_date="2005-01-01", end_date="2020-06-05")


index_investing_global_df = ak.index_investing_global(country="中国", index_name="富时中国A50指数", period="每日", start_date="20000101", end_date="20210909")
print(index_investing_global_df)


index_investing_global_df = ak.index_investing_global_from_url(url="https://www.investing.com/indices/ftse-epra-nareit-hong-kong", period="每日", start_date="19900101", end_date="20210909")
print(index_investing_global_df)