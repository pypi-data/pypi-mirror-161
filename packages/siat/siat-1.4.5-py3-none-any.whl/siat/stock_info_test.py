# -*- coding: utf-8 -*-

import os; os.chdir("S:/siat/siat")

import akshare as ak
from siat.common import *

zs=ak.index_investing_global_country_name_url("中国")
df = ak.index_investing_global(country="中国", index_name="上证指数", period="每日", start_date="2021-01-01", end_date="2021-06-05")
print(index_investing_global_df)

df=ak.stock_us_daily(symbol='^DJI', adjust="")


#==============================================================================
if __name__=='__main__':
    symbol='AAPL'
    fromdate='2020-12-1'
    todate='2021-1-31'

def get_price_ak_us(symbol, fromdate, todate, adjust=""):
    """
    抓取单个美股股价
    """
    
    #检查日期期间
    result,start,end=check_period(fromdate,todate)
    if not result:
        print("  #Error(get_price_ak_us): invalid date period from",fromdate,'to',todate)
        return None  
    
    import akshare as ak
    print("  Searching info in Sina Finance for",symbol,"... ...")
    try:
        df=ak.stock_us_daily(symbol=symbol, adjust="")
    except:
        print("  #Warning(get_price_ak_us): no info found for",symbol)
        return None
    else:
        print("  Successfully retrieved",len(df),"records for",symbol)
    
    #选取时间范围
    df1=df[df.index >=start]    
    df2=df1[df1.index <=end] 
    
    df2.rename(columns={'open':'Open','high':'High','low':'Low','close':'Close','volume':'Volume'},inplace=True)
    df2['Ticker']=symbol
    
    return df2

#==============================================================================
if __name__=='__main__':
    symbol='0700.HK'
    fromdate='2020-12-1'
    todate='2021-1-31'

def get_price_ak_hk(symbol, fromdate, todate, adjust=""):
    """
    抓取单个港股股价
    """
    
    #检查日期期间
    result,start,end=check_period(fromdate,todate)
    if not result:
        print("  #Error(get_price_ak_hk): invalid date period from",fromdate,'to',todate)
        return None  
    
    import akshare as ak
    print("  Searching info in Sina Finance for",symbol,"... ...")
    symbol1 = symbol.strip('.HK')
    symbol2 = symbol1.strip('.hk')
    symbol3='0'+symbol2
    try:
        df=ak.stock_hk_daily(symbol=symbol3, adjust="")
    except:
        print("  #Warning(get_price_ak_hk): no info found for",symbol)
        return None
    else:
        print("  Successfully retrieved",len(df),"records for",symbol)
    
    #选取时间范围
    df1=df[df.index >=start]    
    df2=df1[df1.index <=end] 
    
    df2.rename(columns={'open':'Open','high':'High','low':'Low','close':'Close','volume':'Volume'},inplace=True)
    df2['Ticker']=symbol
    
    return df2

if __name__=='__main__':
    df=get_price_ak_hk(symbol, fromdate, todate)
#==============================================================================
def str_replace(str1):
    """
    删除给定字符串中的子串
    """
    replist=['Ltd.','Ltd','Co.','LTD.','CO.',' CO','LTD','Inc.','INC.', \
             'CORPORATION','Corporation','LIMITED','Limited','Company', \
             'COMPANY','(GROUP)','Corp.','CORP','GROUP','Group']
    
    for rc in replist:
        str2=str1.replace(rc, '')
        str1=str2
    
    twlist=[' ',',','，']    
    for tw in twlist:
        str2 = str2.strip(tw)
    
    return str2
    
#==============================================================================
def get_all_stock_names():
    """
    获得股票代码和名称：中国A股、港股、美股
    """
    import akshare as ak
    import pandas as pd
    
    #上证A股
    df_ss=ak.stock_info_sh_name_code()
    df_ss.rename(columns={'COMPANY_ABBR':'CNAME','ENGLISH_ABBR':'ENAME','LISTING_DATE':'LISTING'},inplace=True)
    df_ss['SYMBOL']=df_ss['COMPANY_CODE']+'.SS'
    df_ss_1=df_ss[['SYMBOL','CNAME','ENAME','LISTING']]    
    
    #深证A股
    df_sz=ak.stock_info_sz_name_code(indicator="A股列表")
    df_sz['SYMBOL']=df_sz['A股代码']+'.SZ'
    df_sz.rename(columns={'A股简称':'CNAME','英文名称':'ENAME','A股上市日期':'LISTING'},inplace=True)
    df_sz_1=df_sz[['SYMBOL','CNAME','ENAME','LISTING']]    
    
    #美股
    df_us=ak.get_us_stock_name()
    df_us['LISTING']=' '
    df_us.rename(columns={'symbol':'SYMBOL','name':'ENAME','cname':'CNAME'},inplace=True)
    df_us_1=df_us[['SYMBOL','CNAME','ENAME','LISTING']] 
    
    #港股
    df_hk=ak.stock_hk_spot()
    df_hk['LISTING']=' '
    last4digits=lambda x:x[1:5]
    df_hk['symbol1']=df_hk['symbol'].apply(last4digits)
    df_hk['SYMBOL']=df_hk['symbol1']+'.HK'
    df_hk.rename(columns={'name':'CNAME','engname':'ENAME'},inplace=True)
    df_hk_1=df_hk[['SYMBOL','CNAME','ENAME','LISTING']] 
    
    #合成
    df=pd.concat([df_ss_1,df_sz_1,df_us_1,df_hk_1])
    df.sort_values(by=['SYMBOL'], ascending=True, inplace=True )
    df.reset_index(drop=True,inplace=True)
    
    rep=lambda x:str_replace(x)
    df['CNAME']=df['CNAME'].apply(rep)
    df['ENAME']=df['ENAME'].apply(rep)
    
    #保存:应保存在文件夹S:/siat/siat中，重新生成siat轮子
    df.to_pickle('stock_info.pickle')

    """
    #读出文件
    with open('stock_info.pickle','rb') as test:
        df = pickle.load(test)
    """
    
    return df
#==============================================================================
if __name__=='__main__':
    symbol='0700.HK'
def get_names(symbol):
    """
    从文件中查询证券代码的短名称
    """
    import pickle
    with open('stock_info.pickle','rb') as test:
        df = pickle.load(test)  
        
    df1=df[df['SYMBOL']==symbol]
    if len(df1)==0:
        return None
    else:
        name=df1['CNAME'].values[0]   
    
    return name
#==============================================================================
# 股票预测插件
from stocker import Stocker
amazon=Stocker("AMZN")
amazon.plot_stock()
model,model_data=amazon.create_prophet_model(days=90)
amazon.evaluate_prediction()
