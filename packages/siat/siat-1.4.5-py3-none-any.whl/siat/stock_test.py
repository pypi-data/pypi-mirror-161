# -*- coding: utf-8 -*-

import os; os.chdir("S:/siat")
from siat import *
#==============================================================================
# AMZN, EBAY, SHOP, BABA, JD
tickers=["AMZN","EBAY","SHOP","BABA","JD"]
measure="Annual Ret%"
start="2022-1-1"
end="2022-7-31"

pair=tickers[0:2]
df12=compare_security(pair,measure,start,end)
df1=df12[0]
colname=list(df1)[0]
df1.rename(columns={colname:codetranslate(tickers[0])},inplace=True)
df2=df12[1]
df2.rename(columns={colname:codetranslate(tickers[1])},inplace=True)

pair=tickers[2:4]
df34=compare_security(pair,measure,start,end)
df3=df34[0]
df3.rename(columns={colname:codetranslate(tickers[2])},inplace=True)
df4=df34[1]
df4.rename(columns={colname:codetranslate(tickers[3])},inplace=True)

pair=[tickers[4],tickers[4]]
df56=compare_security(pair,measure,start,end)
df5=df56[0]
df5.rename(columns={colname:codetranslate(tickers[4])},inplace=True)

dflist=[df1,df2,df3,df4,df5]
import pandas as pd
from functools import reduce
dfs=reduce(lambda left,right:pd.merge(left,right,left_index=True,right_index=True),dflist)

y_label=measure
import datetime; today = datetime.date.today()
x_label=texttranslate("数据来源: 新浪/stooq,")+' '+str(today)
axhline_value=0
axhline_label=''
title_txt="Compare Multiple Securities Performance"
draw_lines(dfs,y_label,x_label,axhline_value,axhline_label,title_txt, \
               data_label=False,resample_freq='H',smooth=True)


def compare_msecurity(tickers,measure,start,end,axhline_value=0,axhline_label=''):
    """
    功能：比较并绘制多条证券指标曲线（多于2条），个数可为双数或单数
    注意：
    tickers中须含有2个及以上股票代码，
    measure为单一指标，
    axhline_label不为空时绘制水平线
    """
    num=len(tickers)
    if num <=2:
        print("  #Error(compare_msecurity): need more tickers")
        return None

    if not isinstance(measure,str): 
        print("  #Error(compare_msecurity): support only one measure")
        return None
        
    #循环获取证券指标
    loopn=int(len(tickers)/2)
    colname=''
    import pandas as pd
    dfs=pd.DataFrame()
    from functools import reduce
    for i in range(0,loopn):
        pair=tickers[i*2:i*2+2]
        #print(i,pair)
        
        dfi=compare_security(pair,measure,start,end,graph=False)

        dfi1=dfi[0]
        if colname == '':
            colname=list(dfi1)[0]
        dfi1.rename(columns={colname:codetranslate(tickers[i*2])},inplace=True)   

        dfi2=dfi[1]
        dfi2.rename(columns={colname:codetranslate(tickers[i*2+1])},inplace=True) 
        
        if len(dfs) == 0:
            dflist=[dfi1,dfi2]
        else:
            dflist=[dfs,dfi1,dfi2]
        dfs=reduce(lambda left,right:pd.merge(left,right,left_index=True,right_index=True),dflist)

    #判断奇偶数
    if (num % 2) == 0:
        even=True
    else:
        even=False
    i=loopn
    if not even:
        pair=[tickers[num-1],tickers[num-1]]  
        dfi=compare_security(pair,measure,start,end,graph=False)

        dfi1=dfi[0]
        dfi1.rename(columns={colname:codetranslate(tickers[i*2])},inplace=True)   

        dflist=[dfs,dfi1]
        dfs=reduce(lambda left,right:pd.merge(left,right,left_index=True,right_index=True),dflist)

    #绘制多条曲线
    y_label=measure
    import datetime; today = datetime.date.today()
    x_label=texttranslate("数据来源: 新浪/stooq,")+' '+str(today)
    axhline_value=0
    axhline_label=''
    title_txt=texttranslate("Compare Multiple Securities Performance")
    draw_lines(dfs,y_label,x_label,axhline_value,axhline_label,title_txt, \
                   data_label=False,resample_freq='H',smooth=True)

    return dfs

    
#==============================================================================
tickers1=["AMZN","EBAY","SHOP","BABA","JD"]
tickers2=["AMZN","EBAY","SHOP","BABA","JD","PDD"]
measure1="Annual Ret%"
measure2="Exp Ret%"
start="2022-1-1"
end="2022-7-31"
df=compare_msecurity(tickers1,measure1,start,end)
df=compare_msecurity(tickers1,measure2,start,end)

df=compare_msecurity(tickers2,measure1,start,end)
df=compare_msecurity(tickers2,measure2,start,end)
#==============================================================================

check_language()

info=get_stock_profile("AAPL","all")

info=get_stock_profile("momo","all")



#==============================================================================
price=security_price('AAPL','2022-6-1','2022-6-30')

moutai=security_price('600519.SH','2022-6-1','2022-6-30')


#==============================================================================
info=get_stock_profile("AAPL")
info=get_stock_profile("AAPL",info_type='officers')
info=get_stock_profile("AAPL",info_type='market_rates')
info=get_stock_profile("AAPL",info_type='fin_rates')

div=stock_dividend('600519.SS','2011-1-1','2020-12-31')

split=stock_split('600519.SS','1990-1-1','2022-12-31')

# Define names of companies for comparison
tickers=['AMZN','EBAY','SHOP','MELI','BABA','JD','VIPS','PDD']
# Comparing company performance
roa=compare_snapshot(tickers,'ROA',axisamp=1.2)

#==============================================================================
df=get_price('600519.SS','2022-1-1','2022-5-11')
dfoc=df[['Open','Close']]

import pandas_alive
dfoc_alive=dfoc.sum(axis = 1).fillna(0).plot_animated(filename = 'bar-chart .gif',kind = 'line', \
        period_label = { 'x':0.1,'y':0.9 }, \
        steps_per_period = 2,interpolate_period = True,period_length = 200)

dfoc_alive=dfoc.plot_animated(filename = 'line_chart.gif',kind = 'line',period_label = { 'x':0.25,'y':0.9 })




#==============================================================================
df=compare_stock(["JD", "BABA"], "Annual Price Volatility", "2020-1-1", "2020-12-31")
df=compare_stock(["AAPL", "MSFT"], "Annual Ret Volatility%", "2020-1-1", "2020-12-31")
df=compare_stock(["FB", "MSFT"], "Annual Ret LPSD%", "2020-1-1", "2020-12-31")




#==============================================================================
df=compare_stock("AAPL", ["Annual Ret%", "Daily Ret%"], "2021-10-1", "2021-12-31")

df=compare_stock(["000002.SZ", "600266.SS"], "Annual Ret%", "2021-1-1", "2021-6-30",loc1="lower right")

df=compare_stock(["JD", "AMZN"], "Exp Ret%", "2020-1-1", "2020-12-31")
#==============================================================================

df1,df2=compare_security(['^XU100','000300.SS'],'Exp Ret','2021-7-1','2021-12-31')
df1,df3=compare_security(['^XU100','^GSPC'],'Exp Ret','2021-7-1','2021-12-31')

#==============================================================================
info=get_stock_profile("FIBI.TA", info_type='officers')
info=get_stock_profile("TSLA", info_type='officers')

df=security_price('000300.SS','2014-1-1','2016-12-31',power=6)
#==============================================================================
# This trick does not work any more
import io
import pandas
from datetime import datetime
import requests

class YahooData:
  def fetch(ticker, start, end):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'
    }

    url = "https://query1.finance.yahoo.com/v7/finance/download/" + str(ticker)
    x = int(datetime.strptime(start, '%Y-%m-%d').strftime("%s"))
    y = int(datetime.strptime(end, '%Y-%m-%d').strftime("%s"))
    url += "?period1=" + str(x) + "&period2=" + str(y) + "&interval=1d&events=history&includeAdjustedClose=true"
    
    r = requests.get(url, headers=headers)
    pd = pandas.read_csv(io.StringIO(r.text), index_col=0, parse_dates=True)

    return pd

df = YahooData.fetch("TSLA", start="2021-01-01", end="2021-12-31")
print(df)

#==============================================================================
# This trick does not work any more
import pandas
from pandas_datareader import data as pdr
import yfinance as yfin
yfin.pdr_override()

df = pdr.get_data_yahoo("TSLA", start="2021-07-01", end="2021-07-14")
df2 = pdr.get_data_yahoo("TSLA", start="2021-7-1", end="2021-7-14")
print(df)
#==============================================================================
# This trick does not work any more
import numpy as np
import pandas as pd
import requests
from datetime import datetime, timedelta, date


result = requests.get('https://query1.finance.yahoo.com/v7/finance/download/BABA?period1=000000001&period2=9999999999&interval=1d&events=history&includeAdjustedClose=true')

f = open('file.csv', "w")
f.write(result.text)
f.close()

df_daten = pd.read_csv('file.csv')
df_daten["Date"]= pd.to_datetime(df_daten["Date"])
df_daten.set_index('Date', inplace=True)

start_remove = pd.to_datetime('2001-1-1')
end_remove = pd.to_datetime('2021-7-1')
df_neu = df_daten.query('Date < @start_remove or Date > @end_remove')

#==============================================================================
p=security_price("BB","2015-1-10","2015-1-20")
p=security_price("LLY","2000-3-1","2003-12-31")


#==============================================================================
compare_stock(["000001.SS","399001.SZ"], "Close", "2010-1-1", "2021-5-29",twinx=True)
compare_stock(["000300.SS","000001.SS"], "Close", "2010-1-1", "2021-5-29",twinx=True)

compare_stock(["^HSI","000001.SS"], "Close", "2010-1-1", "2021-5-29",twinx=True)
compare_stock(["^N225","000001.SS"], "Close", "2010-1-1", "2021-5-29",twinx=True)
compare_stock(["^KS11","000001.SS"], "Close", "2010-1-1", "2021-5-29",twinx=True)
compare_stock(["^GSPC","000001.SS"], "Close", "2010-1-1", "2021-5-29",twinx=True)
compare_stock(["^DJI","^GSPC"], "Close", "2010-1-1", "2021-5-29",twinx=True)


compare_stock(["600583.SS","601808.SS"], "Close", "2021-1-1", "2021-5-29")
compare_stock(["600583.SS","600968.SS"], "Close", "2021-1-1", "2021-5-29")
#==============================================================================
fr1=get_stock_profile("0883.HK",info_type='fin_rates')
fr2=get_stock_profile("0857.HK",info_type='fin_rates')

fr1=get_stock_profile("1033.HK",info_type='fin_rates')
fr2=get_stock_profile("2883.HK",info_type='fin_rates')                      
fr3=get_stock_profile("SLB",info_type='fin_rates') 
fr4=get_stock_profile("2222.SR",info_type='fin_rates') 
fr5=get_stock_profile("HAL",info_type='fin_rates') 

info=get_stock_profile("AAPL",info_type='fin_rates')
info=get_stock_profile("AAPL",info_type='market_rates')
info=get_stock_profile("MSFT",info_type='fin_rates')
fs=get_stock_profile("AAPL",info_type='fin_statements')
#==============================================================================
compare_stock(["0883.HK","0857.HK"], "Close", "2010-1-1", "2021-5-18")
compare_stock(["0883.HK","0857.HK"], "Annual Ret%", "2010-1-1", "2021-5-18")
compare_stock(["0883.HK","0857.HK"], "Exp Ret%", "2010-1-1", "2021-5-18")
compare_stock(["0883.HK","0857.HK"], "Annual Ret Volatility%", "2010-1-1", "2021-5-18")
compare_stock(["0883.HK","0857.HK"], "Exp Ret Volatility%", "2010-1-1", "2021-5-18")

from siat.financials import *
compare_history(["0883.HK","0857.HK"], "Cashflow per Share")

tickers=["0883.HK","0857.HK","0386.HK",'XOM','2222.SR','OXY','BP','RDSA.AS']
cr=compare_snapshot(tickers,'Current Ratio')
pbr=compare_snapshot(tickers,'Price to Book')
atr=compare_tax(tickers)
emp=compare_snapshot(tickers,'Employees')
esg=compare_snapshot(tickers,'Total ESG')

tickers2=["0883.HK","0857.HK","0386.HK",'1024.HK','1810.HK','9988.HK','9618.HK','0700.HK']
cfps=compare_snapshot(tickers2,'Cashflow per Share')


from siat.beta_adjustment import *
atr=prepare_hamada_yahoo('XOM')

compare_stock(["000001.SS","^HSI"], "Close", "2010-1-1", "2021-5-18",twinx=True)
compare_stock(["000001.SS","^HSI"], "Exp Ret%", "2021-1-1", "2021-5-18")
compare_stock(["000001.SS","^HSI"], "Exp Ret Volatility%", "2021-1-1", "2021-5-18")

gg_cnooc=get_stock_profile("0883.HK",info_type='officers')
gg_sinopec=get_stock_profile("0386.HK",info_type='officers')
gg_slb=get_stock_profile('RDSA.AS',info_type='officers')
#==============================================================================
compare_stock(["FB", "MSFT"], "Annual Ret LPSD%", "2019-1-1", "2019-12-31")
compare_stock(["FB", "MSFT"], "Exp Ret LPSD%", "2019-1-1", "2019-12-31")

#==============================================================================
price=stock_price("600519.SS","2020-6-10","2020-7-10")

compare_stock("MSFT", ["Open", "Close"], "2020-3-16", "2020-3-31")
price = stock_price("GOOG", "2019-7-1", "2019-12-31")

prices = compare_stock(["DAI.DE","BMW.DE"], "Close", "2020-1-1", "2020-3-31")
compare_stock("7203.T", ["High", "Low"], "2020-3-1", "2020-3-31")

compare_stock(["FB", "TWTR"], "Daily Ret%", "2020-3-1", "2020-3-31")
compare_stock("CDI.PA", ["Daily Ret", "log(Daily Ret)"], "2020-1-1", "2020-3-31")

compare_stock("IBM", ["Annual Ret%", "Daily Ret%"], "2019-1-1", "2019-12-31")

compare_stock(["000002.SZ", "600266.SS"], "Annual Ret%", "2020-1-1", "2020-3-31")
compare_stock(["BABA", "JD"], "Annual Ret%", "2020-1-1", "2020-3-31")
compare_stock(["0700.HK", "1810.HK"], "Annual Ret%", "2019-10-1", "2019-12-31")
compare_stock(["MSFT", "AAPL"], "Annual Ret%", "2019-1-1", "2020-3-31")

info=stock_ret("MSFT", "2010-1-1", "2020-12-31", type="Exp Ret%")
compare_stock(["JD", "AMZN"], "Exp Adj Ret%", "2019-1-1", "2020-12-31")

pv=stock_price_volatility("000002.SZ", "2019-1-1", "2020-12-31", "Weekly Price Volatility")
pv=stock_price_volatility("000002.SZ", "2019-1-1", "2020-12-31", "Annual Price Volatility")
compare_stock(["JD", "BABA"], "Annual Price Volatility", "2019-1-1", "2019-12-31")

compare_stock(["JD", "BABA"], "Exp Price Volatility", "2019-1-1", "2019-12-31")

info=stock_ret_volatility("AAPL", "2019-1-1", "2019-12-31", "Weekly Ret Volatility%")
info=stock_ret_volatility("AAPL", "2019-1-1", "2019-12-31", "Annual Ret Volatility%",power=0)
info=stock_ret_volatility("AAPL", "2019-1-1", "2019-12-31", "Exp Ret Volatility%")

compare_stock(["AAPL", "MSFT"], "Annual Ret Volatility%", "2019-1-1", "2019-12-31")

compare_stock(["AAPL", "MSFT"], "Exp Ret Volatility%", "2019-1-1", "2019-12-31")

compare_stock("QCOM", ["Annual Ret LPSD%", "Annual Ret Volatility%"], "2019-1-1", "2019-12-31")

compare_stock("QCOM", ["Exp Ret LPSD%", "Exp Ret Volatility%"], "2019-1-1", "2019-12-31")

compare_stock("QCOM", ["Exp Ret LPSD%", "Exp Ret%"], "2019-1-1", "2019-12-31")

compare_stock(["FB", "MSFT"], "Annual Ret LPSD%", "2019-1-1", "2019-12-31")

#==============================================================================
price = stock_price("GOOG", "2019-7-1", "2019-12-31")
prices = compare_stock(["DAI.DE","BMW.DE"], "Close", "2020-1-1", "2020-3-31")
info=candlestick_demo("005930.KS", "2020-1-13", "2020-1-17")
info=candlestick("TCS.NS", "2020-3-1", "2020-3-31")
info=candlestick("0700.HK","2020-2-1","2020-3-31",mav=2,volume=True,style='blueskies')

compare_stock(["FB", "TWTR"], "Daily Ret%", "2020-3-1", "2020-3-31")

compare_stock("UBSG.SW", ["Daily Ret", "log(Daily Ret)"], "2020-1-1", "2020-1-10")
compare_stock("CDI.PA", ["Daily Ret", "log(Daily Ret)"], "2020-1-1", "2020-3-31")

compare_stock("IBM", ["Annual Ret%", "Daily Ret%"], "2019-1-1", "2019-12-31")
compare_stock(["000002.SZ", "600266.SS"], "Annual Ret%", "2020-1-1", "2020-3-31")
compare_stock(["BABA", "JD"], "Annual Ret%", "2020-1-1", "2020-3-31")
compare_stock(["0700.HK", "1810.HK"], "Annual Ret%", "2019-10-1", "2019-12-31")
compare_stock(["MSFT", "AAPL"], "Annual Ret%", "2019-1-1", "2020-3-31")

info=stock_ret("MSFT", "2010-1-1", "2020-12-31", type="Exp Ret%")

compare_stock(["JD", "AMZN"], "Exp Adj Ret%", "2019-1-1", "2020-12-31")


pv=stock_price_volatility("000002.SZ", "2019-1-1", "2020-12-31", "Weekly Price Volatility")
pv=stock_price_volatility("000002.SZ", "2019-1-1", "2020-12-31", "Annual Price Volatility")

compare_stock(["JD", "BABA"], "Annual Price Volatility", "2019-1-1", "2019-12-31")

compare_stock(["JD", "BABA"], "Exp Price Volatility", "2019-1-1", "2019-12-31")

info=stock_ret_volatility("AAPL", "2019-1-1", "2019-12-31", "Weekly Ret Volatility%")
info=stock_ret_volatility("AAPL", "2019-1-1", "2019-12-31", "Annual Ret Volatility%")
info=stock_ret_volatility("AAPL", "2019-1-1", "2019-12-31", "Exp Ret Volatility%")

compare_stock(["AAPL", "MSFT"], "Annual Ret Volatility%", "2019-1-1", "2019-12-31")
compare_stock(["AAPL", "MSFT"], "Exp Ret Volatility%", "2019-1-1", "2019-12-31")

compare_stock("QCOM", ["Annual Ret LPSD%", "Annual Ret Volatility%"], "2019-1-1", "2019-12-31")
compare_stock("QCOM", ["Exp Ret LPSD%", "Exp Ret Volatility%"], "2019-1-1", "2019-12-31")
compare_stock("QCOM", ["Exp Ret LPSD%", "Exp Ret%"], "2019-1-1", "2019-12-31")

compare_stock(["FB", "MSFT"], "Annual Ret LPSD%", "2019-1-1", "2019-12-31")


#==============================================================================
dfr=stock_ret('AAPL','2020-1-1','2021-4-8',type="Daily Adj Ret%")


compare_stock(["000002.SZ", "600266.SS"], "Annual Ret%", "2020-1-1", "2020-3-31")
compare_stock(["BABA", "JD"], "Annual Ret%", "2020-1-1", "2020-3-31")
compare_stock(["0700.HK", "1810.HK"], "Annual Ret%", "2020-1-1", "2020-3-31")
compare_stock(["MSFT", "AAPL"], "Annual Ret%", "2019-1-1", "2020-3-31")

info=stock_ret("MSFT", "2010-1-1", "2020-3-31", type="Exp Ret%")




#==============================================================================
vix=security_price("^VIX", "2020-1-1", "2021-3-31",power=15)
vix=security_price("^VIX", "2021-1-1", "2021-3-31",power=10)

compare_security(['^VIX','^GSPC'],'Close','2011-1-1','2020-12-31',twinx=True)


compare_stock("AAPL", ["Close", "Adj Close"], "2019-1-1", "2019-12-31")
compare_stock("000002.SZ", ["Close", "Adj Close"], "2019-1-1", "2019-7-31")



pricedf=get_price('^HSI',"1991-1-1","2021-2-28")


df=security_price('AAPL','2021-1-1','2021-1-31',datatag=True,power=4)

info=get_stock_profile("AAPL")
info=get_stock_profile("MSFT",info_type='officers')
info=get_stock_profile("AAPL",info_type='officers')
info=stock_info('AAPL')
sub_info=stock_officers(info)

div=stock_dividend('600519.SS','2011-1-1','2020-12-31')
split=stock_split('600519.SS','2000-1-1','2020-12-31')

ticker='AAPL'
info=stock_info(ticker)
info=get_stock_profile("AAPL",info_type='officers')

info=get_stock_profile("AAPL")

info=get_stock_profile("MSFT",info_type='officers')
info=get_stock_profile("GS",info_type='officers')

info=stock_info('JD')
sub_info=stock_officers(info)
info=get_stock_profile("JD",info_type='officers')

info=stock_info('BABA')
sub_info=stock_officers(info)
info=get_stock_profile("BABA",info_type='officers')

info=stock_info('0700.HK')
sub_info=stock_officers(info)
info=get_stock_profile("0700.HK",info_type='officers')

info=stock_info('600519.SS')
sub_info=stock_officers(info)
info=get_stock_profile("600519.SS",info_type='officers')

info=get_stock_profile("0939.HK",info_type='risk_esg')


market={'Market':('China','^HSI')}
stocks={'0700.HK':3,'9618.HK':2,'9988.HK':1}
portfolio=dict(market,**stocks)
esg=portfolio_esg2(portfolio)



