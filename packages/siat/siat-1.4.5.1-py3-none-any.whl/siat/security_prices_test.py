# -*- coding: utf-8 -*-

import os; os.chdir('E:/siat')
from siat import *
#==============================================================================
df=ak.stock_zh_a_hist('000001',period="daily",start_date='20211201',end_date='20211231')

get_prices('000001.SS','2021-12-1','2021-12-31')
get_prices('000001.SZ','2021-12-1','2021-12-31')



#==============================================================================
#广泛测试
get_prices('000001.SS','2021-11-1','2021-11-5')
get_prices('600000.SS','2021-11-1','2021-11-5')
get_prices_ak('600000.SS','2021-11-1','2021-11-5')
get_price_ak_em('600000.SS','2021-11-1','2021-11-5')
get_price_ak_cn('600000.SS','2021-11-1','2021-11-5')

get_prices('399001.SZ','2021-11-1','2021-11-5')
get_prices('000002.SZ','2021-11-1','2021-11-5')

get_prices('430090.SZ','2021-11-1','2021-11-5')
get_prices('430090.BJ','2021-11-1','2021-11-5')
get_prices('830946.BJ','2021-11-1','2021-11-5')

get_prices('^GSPC','2021-11-1','2021-11-5')
get_prices('^DJI','2021-11-1','2021-11-5')
get_prices('^RUT','2021-11-1','2021-11-5') #替代
get_prices('^IXIC','2021-11-1','2021-11-5')
get_prices('^NDX','2021-11-1','2021-11-5')
get_prices('AAPL','2021-11-1','2021-11-5')
get_prices('AAPL.US','2021-11-1','2021-11-5')
get_prices('AAPL_PE.US','2021-11-1','2021-11-5')
get_prices('AAPL_PB.US','2021-11-1','2021-11-5')
get_prices('AAPL_MV.US','2021-11-1','2021-11-5')
get_prices('BABA','2021-11-1','2021-11-5')
get_prices('BABA.US','2021-11-1','2021-11-5')
get_prices('BABA_PE.US','2021-11-1','2021-11-5')
get_prices('BABA_PB.US','2021-11-1','2021-11-5')
get_prices('BABA_MV.US','2021-11-1','2021-11-5')
get_prices('MSFT','2021-11-1','2021-11-5')

get_prices('^N225','2021-11-1','2021-11-5')
get_prices('6758.T','2021-11-1','2021-11-5')
get_prices('7004.T','2021-11-1','2021-11-5')

get_prices('^BSESN','2021-11-1','2021-11-5')


get_prices('^GDAXI','2021-11-1','2021-11-5')
get_prices('BMW.DE','2021-11-1','2021-11-5')

get_prices('^FCHI','2021-11-1','2021-11-5')


get_prices('^FTSE','2021-11-1','2021-11-5')
get_prices('TCS.UK','2021-11-1','2021-11-5')

get_prices('^HSI','2021-11-1','2021-11-5')
get_prices('0700.HK','2021-11-1','2021-11-5')
get_price_ak_hk('0700.HK','2021-11-1','2021-11-5')
get_prices('00700.HK','2021-11-1','2021-11-5')
get_prices('82843.HK','2021-11-1','2021-11-5')




#==============================================================================
get_names('000002.SZ')
get_names('000002.SS')
get_names('430090.NQ')
get_names('830946.BJ')

df = ak.stock_zh_a_spot_em()


codetranslate('000002.SZ')
codetranslate('000002.SS')
codetranslate('430090.NQ')
codetranslate('830946.BJ')
#==============================================================================
#支持北交所历史行情：东方财富，.NQ? .BJ?
df1=ak.stock_zh_a_hist(symbol="000001",period="daily",start_date="20211101",end_date='20211126', adjust="")
df1['换手率'].plot()
df2=ak.stock_zh_a_hist(symbol="430090",period="daily",start_date="20210101",end_date='20211126', adjust="")
df3=ak.stock_zh_a_hist(symbol="830946",period="daily",start_date="20210101",end_date='20211126', adjust="")

#沪深京：股票代码-名称
df999 = ak.stock_info_a_code_name()
#查名称
df999[df999['code']=='430090']['name'].values[0]
#==============================================================================

df=security_price('00700.HK','2021-11-1','2021-11-20',power=6)
df=security_price('0700.HK','2021-11-1','2021-11-20',power=6)
df=security_price('00886.HK','2021-11-1','2021-11-20',power=6)
df=security_price('0886.HK','2021-11-1','2021-11-20',power=6)

df=security_price('7203.T','2021-11-1','2021-11-20',power=6)
#==============================================================================
import sys
sys.path.insert(0,r'S:\siat\siat')
from security_prices import *

df=security_price('^HSI','2014-1-1','2016-12-31',power=6)
df=get_prices('0700.HK','2014-1-1','2016-12-31')
df=get_prices('^HSI','2014-1-1','2016-12-31')
df=get_prices('^GSPC','2014-1-1','2016-12-31')
df=get_prices('^DJI','2014-1-1','2016-12-31')
df=get_prices('^IXIC','2014-1-1','2016-12-31')
df=get_prices('^N225','2014-1-1','2016-12-31')
df=get_prices('^VIX','2014-1-1','2016-12-31')

df=get_prices('^RUT','2014-1-1','2016-12-31')

df=get_prices('600519.SS','2014-1-1','2016-12-31')
df=get_prices('000002.SZ','2014-1-1','2016-12-31')



df=get_index_fred('^GSPC','2014-1-1','2016-12-31')
df=get_index_fred('^DJI','2014-1-1','2016-12-31')

df=get_price_ak_cn('600340.SS','2021-1-1','2021-1-31')

zs=ak.index_investing_global_country_name_url("美国")
zsjg=ak.index_investing_global(country="美国", index_name="VIX恐慌指数", period="每日", start_date="2005-01-01", end_date="2020-06-05")

from siat import *
df=security_price('000300.SS','2014-1-1','2016-12-31',power=6)
df=security_price('000888.SZ','2014-1-1','2016-12-31',power=6)
df=get_price_ak_cn('000888.SZ','2014-1-1','2016-12-31')

portfolio={'Market':('China','^HSI'),'0823.HK':1.0}
pp=get_portfolio_prices(portfolio,'2021-7-1','2021-10-30')

#==============================================================================
p=security_price("BB","2015-1-10","2015-1-24",power=0)
p=security_price("LLY","2000-1-1","2003-12-31",power=10)
#==============================================================================
dfyf=get_prices_yf('AAPL','2020-1-1','2021-4-8',threads=False)

dfak=get_prices_ak('600519.SS','2020-1-1','2021-4-8')
dfak=get_prices_ak(['600519.SS','000002.SZ'],'2020-1-1','2021-4-8')


df=get_prices('AAPL','2020-1-1','2021-4-8',adj=False)
dfa=get_prices('AAPL','2020-1-1','2021-4-8',adj=True)
dfa_dif=dfa[dfa['Close']!=dfa['Adj Close']]

dfhy=get_prices('300401.SZ','2018-5-1','2018-5-30',adj=True)
dfyfhy=get_prices_yf('300401.SZ','2018-5-1','2018-5-30',threads=False)



ticker=['600011.SS']
start='2020-1-1'
end='2020-6-30'
pak=get_prices_ak(ticker,start,end)

pyf=get_price_yf(ticker,start,end)

pyh=p=get_prices_yahoo(ticker,start,end)

p=get_prices(ticker,start,end)

tickerlist=['600011.SS']
sharelist=[1]
p1=get_price_portfolio(tickerlist,sharelist,start,end)


if __name__=='__main__':
    tickerlist=['INTC','MSFT']
    sharelist=[0.6,0.4]
    fromdate='2020-11-1'
    todate='2021-1-31'

p2=get_prices_portfolio(tickerlist,sharelist,fromdate,todate)


if __name__=='__main__':
    tickerlist=['INTC','MSFT','uvwxyz']
    sharelist=[0.6,0.3,0.1]
    fromdate='2020-11-1'
    todate='2021-1-31'
    dfp1=get_prices_portfolio(tickerlist,sharelist,fromdate,todate)
    dfp2=get_prices_yf(tickerlist,fromdate,todate)
    dfp3=get_prices(tickerlist,fromdate,todate)
    
    prices=get_prices_yf(tickerlist,fromdate,todate)
    

if __name__=='__main__':
    df1=get_prices('INTC','2020-10-1','2021-1-31')
    df2=get_prices(['INTC'],'2020-10-1','2021-1-31')
    df3=get_prices(['XYZ'],'2020-10-1','2021-1-31')
    df4=get_prices(['INTC','MSFT'],'2020-10-1','2021-1-31')
    df5=get_prices(['INTC','UVW'],'2020-10-1','2021-1-31')
    df6=get_prices(['0988.HK','000858.SZ'],'2020-10-1','2021-1-31')
    df7=get_prices(['INTL','MSFT','0988.HK','000858.SZ'],'2020-10-1','2021-1-31')
    df8=get_prices(['000858.SZ','600519.SS'],'2020-10-1','2021-1-31')


#==============================================================================
import akshare as ak

#上证综指
sh_df = ak.stock_zh_index_daily(symbol="sh000001")

#上证50指数
sh50_df = ak.stock_zh_index_daily(symbol="sh000016")

#上证100指数
sh100_df = ak.stock_zh_index_daily(symbol="sh000132")

#上证150指数
sh150_df = ak.stock_zh_index_daily(symbol="sh000133")

#上证180指数
sh180_df = ak.stock_zh_index_daily(symbol="sh000010")

#科创50指数
kc50_df = ak.stock_zh_index_daily(symbol="sh000688")

#沪深300指数
hs300_df = ak.stock_zh_index_daily(symbol="sh000300")

#大盘，中证100指数
zz100_df = ak.stock_zh_index_daily(symbol="sh000903")

#中盘，中证200指数
zz200_df = ak.stock_zh_index_daily(symbol="sh000904")

#小盘，中证500指数
zz500_df = ak.stock_zh_index_daily(symbol="sh000906")

#深证成指
sz_df = ak.stock_zh_index_daily(symbol="sz399001")

#交易所概况
sse_summary_df = ak.stock_sse_summary()
szse_summary_df = ak.stock_szse_summary()

stock_zh_index_daily_tx_df = ak.stock_zh_index_daily_tx(symbol="sh000001")

#==============================================================================
import os; os.chdir("S:/siat")
from siat.security_prices import *

df1=get_prices(['600519.SS','000858.SZ'],'2020-10-1','2021-1-31')
df2=get_prices(['0700.HK','000858.SZ'],'2020-10-1','2021-1-31')
df3=get_prices(['AAPL','MSFT'],'2020-10-1','2021-1-31')
df4=get_prices('399001.SZ','2020-10-1','2021-1-31')
df5=get_prices('000016.SS','2020-10-1','2021-1-31')

dfp1=get_prices_portfolio(['600519.SS','000858.SZ'],[1,2],'2020-10-1','2021-1-31')
dfp2=get_prices_portfolio(['0700.HK','000858.SZ'],[1,2],'2020-10-1','2021-1-31')
dfp3=get_prices_portfolio(['AAPL','MSFT'],[1,2],'2020-10-1','2021-1-31')


df600519=get_price_ak('600519.SS','2020-12-1','2021-2-5',adjust='none')
df600519hfq=get_price_ak('600519.SS','2020-12-1','2021-2-5',adjust='hfq')
df399001=get_price_ak('399001.SZ','2020-12-1','2021-2-5')
df000688=get_price_ak('000688.SS','2020-12-1','2021-2-5')
dfaapl=get_price_ak('AAPL','2020-12-1','2021-2-5')

df3=get_prices_yf(['AAPL','MSFT'],'2020-12-1','2021-1-31')



if __name__=='__main__':
    df1=get_prices('INTC','2020-10-1','2021-1-31')
    df2=get_prices(['INTC'],'2020-10-1','2021-1-31')
    df3=get_prices('XYZ','2020-10-1','2021-1-31')
    df3b=get_prices(['XYZ'],'2020-10-1','2021-1-31')
    df4=get_prices(['INTC','MSFT'],'2020-10-1','2021-1-31')
    df5=get_prices(['INTC','UVW123'],'2020-10-1','2021-1-31')
    df6=get_prices(['0988.HK','000858.SZ'],'2020-10-1','2021-1-31')
    df7=get_prices(['INTL','MSFT','0988.HK','000858.SZ'],'2020-10-1','2021-1-31')
    
if __name__=='__main__':
    tickerlist=['INTC','MSFT']
    sharelist=[0.6,0.4]
    fromdate='2020-11-1'
    todate='2021-1-31'
    dfp=get_prices_portfolio(tickerlist,sharelist,fromdate,todate)    
    
#==================================================================================


def test_yahoo():
    """
    测试雅虎网站是否可访问
    结果：网址可达，网页不可访问，无用
    """
    import pandas_datareader.data as web
    ticker='AAPL'
    start='2021-1-1'
    end='2021-1-11'
    try:
        appl = web.get_data_yahoo(ticker,start,end)
        return True
    except:
        return False  
    
if __name__=='__main__':
    test_yahoo()

