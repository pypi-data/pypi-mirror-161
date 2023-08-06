# -*- coding: utf-8 -*-
"""
版权：王德宏，北京外国语大学国际商学院
功能：提供CMAT资本市场与投资管理分析工具包的精选公共函数，便于各个插件直接引用或复制
版本：1.10，2019-10-9
"""

#==============================================================================
#屏蔽所有警告性信息
import warnings; warnings.filterwarnings('ignore')
#==============================================================================
#以下使用雅虎财经数据源
#==============================================================================
def check_period(fromdate,todate):
    """
    功能：根据开始/结束日期检查期间日期的合理性
    输入参数：
    fromdate：开始日期。格式：YYYY-MM-DD
    enddate：开始日期。格式：YYYY-MM-DD
    输出参数：
    validity：期间合理性。True-合理，False-不合理
    start：开始日期。格式：datetime类型
    end：结束日期。格式：datetime类型
    """
    import pandas as pd
    try:
        start=pd.to_datetime(fromdate)
    except:
        print("Error #1(check_period): invalid date:",fromdate)
        return None,None,None         
    try:
        end=pd.to_datetime(todate)
    except:
        print("Error #2(check_period): invalid date:",todate)
        return None,None,None          
    if start > end:
        print("Error #3(check_period): invalid period: from",fromdate,"to",todate)
        return None,None,None     

    return True,start,end

#==============================================================================
def get_prices_yahoo(ticker,fromdate,todate):
    """
    功能：从雅虎财经抓取股票股价或指数价格或投资组合价值，使用pandas_datareader
    输入：股票代码或股票代码列表，开始日期，结束日期
    ticker: 股票代码或者股票代码列表。
    大陆股票代码加上后缀.SZ或.SS，港股代码去掉前导0加后缀.HK
    fromdate: 样本开始日期。
    todate: 样本结束日期。既可以是今天日期，也可以是一个历史日期   
    
    输出：股票价格序列，按照日期升序排列。原汁原味的抓取数据
    *Close price adjusted for splits.
    **Adjusted close price adjusted for both dividends and splits. 
    """
    #检查期间合理性
    result,start,end=check_period(fromdate,todate)
    if result is None:
        print("Error #1(get_prices_yahoo): incorrect date or invalid period!")        
        return None         
    
    #抓取雅虎股票价格
    from pandas_datareader import data
    try:
        prices=data.DataReader(ticker,'yahoo',start,end)
    except:
        print("Error #2(get_prices_yahoo): failed to get stock prices!")        
        print("Information:",ticker,fromdate,todate) 
        print("Possible reasons:")
        print("  1)internet connection problems.")
        print("  2)incorrect stock code.")
        print("  3)stock delisted or suspended during the period.")
        return None            
    if len(prices)==0:
        print("Error #3(get_prices_yahoo): fetched empty stock data!")
        print("Possible reasons:")
        print("  1)internet connection problems.")
        print("  2)incorrect stock code.")
        print("  3)stock delisted or suspended during the period.")
        return None         
    
    #去掉比起始日期更早的样本
    price2=prices[prices.index >= start]
    #去掉比结束日期更晚的样本
    price2=price2[price2.index <= end]
    
    #按日期升序排序，近期的价格排在后面
    sortedprice=price2.sort_index(axis=0,ascending=True)

    return sortedprice


#==============================================================================
def cvt_yftickerlist(ticker):
    """
    功能：转换pandas_datareader的tickerlist为yfinance的格式
    输入参数：单一股票代码或pandas_datareader的股票代码列表

    输出参数：yfinance格式的股票代码列表
    """
    #如果不是股票代码列表，直接返回股票代码
    if not isinstance(ticker,list): return ticker,False
    
    #如果是股票代码列表，但只有一个元素
    if len(ticker)==1: return ticker[0],False
    
    #如果是股票代码列表，有两个及以上元素
    yftickerlist=ticker[0]
    for t in ticker[1:]:
        yftickerlist=yftickerlist+' '+t
    
    return yftickerlist,True


if __name__=='__main__':
    tl1,islist=cvt_yftickerlist('AAPL')
    tl1,islist=cvt_yftickerlist(['AAPL'])
    tl1,islist=cvt_yftickerlist(['AAPL','MSFT'])
    tl1,islist=cvt_yftickerlist(['AAPL','MSFT','0700.hk'])
    print(tl1)

#==============================================================================
def get_prices_yf(ticker,start,end):
    """
    功能：从雅虎财经抓取股价，使用yfinance(对非美股抓取速度快，但有时不太稳定)
    输入：股票代码或股票代码列表，开始日期，结束日期
    ticker: 股票代码或股票代码列表。大陆股票代码加上后缀.SZ或.SS，港股代码去掉前导0加后缀.HK
    start: 样本开始日期，尽量远的日期，以便取得足够多的原始样本，yyyy-mm-dd
    end: 样本结束日期，既可以是今天日期，也可以是一个历史日期
    
    输出：指定收盘价格序列，最新日期的股价排列在前
    """
    
    #仅为调试用的函数入口参数，正式使用前需要注释掉！
    """
    ticker=['AAPL','MSFT']
    start='2019-10-1'
    end='2019-10-10'
    """
    #---------------------------------------------
   
    #转换日期
    r,startdate,enddate=check_period(start,end)
    if r is None:
        print("Error #1(get_prices_yf): invalid time period")
        return None        
        
    #抓取雅虎股票价格
    import yfinance as yf
    try:
        ticker1,islist=cvt_yftickerlist(ticker)
        if not islist: 
            stock=yf.Ticker(ticker1)
            #下载单一股票的股价
            p=stock.history(start=start,end=end)
        else: 
            #下载股票列表的股价
            p=yf.download(ticker1,start=start,end=end,progress=False)
        
    except:
        print("Error #1(get_prices_yf): server not responsed!")
        return None
    
    if len(p) == 0:
        print("Error #2(get_prices_yf): server reached but returned no data!")
        return None
    
    #去掉比起始日期更早的样本
    price=p[p.index >= startdate]
    #去掉比结束日期更晚的样本
    price2=price[price.index <= enddate]
    
    #按日期升序排序，近期的价格排在后面
    sortedprice=price2.sort_index(axis=0,ascending=True)

    #返回日期升序的股价序列    
    return sortedprice

if __name__=='__main__':
    df1=get_prices_yf('AAPL','2019-10-1','2019-10-8')
    df2=get_prices_yf(['AAPL'],'2019-10-1','2019-10-8')
    df3=get_prices_yf(['AAPL','MSFT'],'2019-10-1','2019-10-8')
    df4=get_prices_yf(['AAPL','MSFT','IBM'],'2019-10-1','2019-10-8')

#==============================================================================
def get_stock_prices(ticker,fromdate,todate):
    """
    功能：从雅虎财经抓取股票股价或指数价格
    输入：股票代码或股票代码列表，开始日期，结束日期
    ticker: 股票代码。大陆股票代码加上后缀.SZ或.SS，港股代码去掉前导0加后缀.HK
    fromdate: 样本开始日期，尽量远的日期，以便取得足够多的原始样本
    todate: 样本结束日期，既可以是今天日期，也可以是一个历史日期
    
    输出：股票价格序列，按照日期升序排列。标记股票代码、星期几和收盘价调整标志
    *Close price adjusted for splits.
    **Adjusted close price adjusted for both dividends and splits.
    """
    
    #仅为调试用的函数入口参数，正式使用前需要注释掉！
    #ticker='AAPL'
    #fromdate='2019-9-1'
    #todate='2019-9-15'
    #---------------------------------------------
    
    #抓取股票价格
    prices=get_prices_yahoo(ticker,fromdate,todate)
    if prices is None:
        print("Error #2(get_stock_prices): failed to get stock prices!")        
        return None         

    #提取日期和星期几
    prices['Date']=prices.index.strftime("%Y-%m-%d")
    prices['Weekday']=prices.index.weekday+1
    
    #标记股票代码
    try:
        stocklist=False
        prices['Stock']=ticker      #单个股票代码
    except:
        stocklist=True
        prices['Stock']=str(ticker) #股票代码列表
    
    #标记收盘价是否经过调整(股票分拆分红)
    if not stocklist:   #若为股票列表不做此步
        prices['Adjustment']=prices.apply(lambda x: \
              False if x['Close']==x['Adj Close'] else True,axis=1)
        stockdf=prices[['Stock','Date','Weekday', \
                    'Open','Close','Adj Close','Volume','Adjustment']]  
    else:
        stockdf=prices[['Stock','Date','Weekday', \
                    'Open','Close','Adj Close','Volume']]         
    return stockdf
    

if __name__=='__main__':
    df1=get_stock_prices('601857.SS','2012-01-01','2019-12-31')
    df2=get_stock_prices('MSFT','01/01/2015','06/30/2019')
    df2[df2.Date == '06/28/2019']
    df2[(df2.Date>='03/20/2019') & (df2.Date<='03/29/2019')]    
    df3=get_stock_prices('^GSPC','1/1/2015','6/30/2019')    
    df4=get_stock_prices('002504.SZ','01/01/2015','06/30/2019')
    df5=get_stock_prices('000001.SS','01/01/2015','07/16/2019')    
    df6=get_stock_prices('0700.HK','01/01/2015','06/30/2019')

#==============================================================================
def get_portfolio_prices(tickerlist,sharelist,fromdate,todate):
    """
    功能：抓取投资组合的每日价值
    输入：股票代码列表，份额列表，开始日期，结束日期
    tickerlist: 股票代码列表
    sharelist：持有份额列表，与股票代码列表一一对应
    fromdate: 样本开始日期。格式：'YYYY-MM-DD'
    todate: 样本结束日期。既可以是今天日期，也可以是一个历史日期    
    
    输出：投资组合的价格序列，按照日期升序排列
    """
    
    #仅为调试用的函数入口参数，正式使用前需要注释掉！
    #tickerlist=['AAPL','MSFT']
    #sharelist=[2,1]
    #fromdate='2019-8-1'
    #todate  ='2019-8-31'
    #---------------------------------------------
    
    #检查股票列表个数与份额列表个数是否一致
    if len(tickerlist) != len(sharelist):
        print("Error #1(get_portfolio_prices): numbers of stocks and shares mismatch.")
        return None        
    
    #从雅虎财经抓取股票价格
    p=get_prices_yahoo(tickerlist,fromdate,todate)
    
    import pandas as pd
    #计算投资者的开盘价
    op=p['Open']
    #计算投资组合的价值
    oprice=pd.DataFrame(op.dot(sharelist))
    oprice.rename(columns={0: 'Open'}, inplace=True)    

    #计算投资者的收盘价
    cp=p['Close']
    #计算投资组合的价值
    cprice=pd.DataFrame(cp.dot(sharelist))
    cprice.rename(columns={0: 'Close'}, inplace=True) 
    
    #计算投资者的调整收盘价
    acp=p['Adj Close']
    #计算投资组合的价值
    acprice=pd.DataFrame(acp.dot(sharelist))
    acprice.rename(columns={0: 'Adj Close'}, inplace=True) 

    #合成开盘价、收盘价和调整收盘价
    ocprice=pd.merge(oprice,cprice,how='inner',left_index=True,right_index=True)
    prices=pd.merge(ocprice,acprice,how='inner',left_index=True,right_index=True)

    #提取日期和星期几
    prices['Date']=prices.index.strftime("%Y-%m-%d")
    prices['Weekday']=prices.index.weekday+1

    prices['Portfolio']=str(tickerlist)
    prices['Shares']=str(sharelist)
    prices['Adjustment']=prices.apply(lambda x: \
          False if x['Close']==x['Adj Close'] else True, axis=1)

    stockdf=prices[['Portfolio','Shares','Date','Weekday', \
                    'Open','Close','Adj Close','Adjustment']]  

    return stockdf  


#==============================================================================
#以下专门处理tushare数据源
#==============================================================================
def convert_date_ts(y4m2d2):
    """
    功能：日期格式转换，YYYY-MM-DD-->YYYYMMDD，用于tushare
    输入：日期，格式：YYYY-MM-DD
    输出：日期，格式：YYYYMMDD
    """
    import pandas as pd
    try: date1=pd.to_datetime(y4m2d2)
    except:
        print("Error #1(convert_date_tushare): invalid date:",y4m2d2)
        return None 
    else:
        date2=date1.strftime('%Y')+date1.strftime('%m')+date1.strftime('%d')
    return date2

if __name__ == '__main__':
    convert_date_ts("2019/11/1")

#==============================================================================
def init_ts():
    """
    功能：初始化tushare pro，登录后才能下载数据
    """
    import tushare as ts
    #设置token
    token='49f134b05e668d288be43264639ac77821ab9938ff40d6013c0ed24f'
    pro=ts.pro_api(token)
    
    return pro
#==============================================================================
def get_stock_prices_ts(ticker,fromdate,todate):
    """
    功能：从tushare抓取大陆股票股价
    特别注意：只能处理大陆股票和指数价格，不能处理投资组合价值，与雅虎财经的函数不同
    输入：股票代码，开始日期，结束日期
    ticker: 股票代码。也可以是股指代码
    股票代码加上后缀.SZ或.SH
    fromdate: 样本开始日期。
    todate: 样本结束日期。既可以是今天日期，也可以是一个历史日期     
    
    输出：股票价格序列，按照日期升序排列。
    """
    #仅为调试使用，完成后应注释掉
    #ticker='601857.SS'
    #fromdate='2019-8-1'
    #todate='2019-12-31'
    
    #检查期间合理性
    result,start,end=check_period(fromdate,todate)
    if result is None:
        print("Error #1(get_stock_prices_ts): invalid date period!")        
        return None         
    
    #转换日期格式为tushare
    start=convert_date_ts(fromdate)
    end=convert_date_ts(todate)
    #转换股票代码.SS为.SH(tushare使用.SH而不是雅虎的.SS)
    ticker1=ticker.upper()
    try: ticker2=ticker1.replace('.SS','.SH')
    except: pass
    
    #初始化tushare
    pro=init_ts()    
    #抓取tushare股票价格    
    try:
        prices=pro.daily(ts_code=ticker2,start_date=start,end_date=end)
    except:
        print("Error #2(get_stock_prices_ts): failed to get stock prices!")        
        print("Information:",ticker2,fromdate,todate) 
        print("Possible reasons:")
        print("  1)internet connection problems.")
        print("  2)incorrect stock code.")
        print("  3)stock delisted or suspended during the period.")
        return None            

    #未出错，但也未能抓取到数据，可能ticker是指数代码
    if len(prices)==0:
        try:
            prices=pro.index_daily(ts_code=ticker2,start_date=start,end_date=end)
        except:
            print("Error #3(get_stock_prices_ts): failed to get index prices!")        
            print("Information:",ticker2,fromdate,todate) 
            print("Possible reasons:")
            print("  1)internet connection problems.")
            print("  2)data source server busy.")            
    if len(prices)==0:
        print("Error #4(get_stock_prices_ts): fetched empty index data!")
        print("Information:",ticker2,fromdate,todate) 
        return None  
    
    #按照雅虎财经格式改列名
    prices.rename(columns={'ts_code':'Stock','open':'Open','high':'High', \
            'low':'Low','close':'Close', \
            'amount':'Amount'}, inplace = True)
    #修改交易日期格式为YYYY-MM-DD
    prices['YYYY']=prices.apply(lambda x:x['trade_date'][0:4],axis=1)
    prices['MM']=prices.apply(lambda x:x['trade_date'][4:6],axis=1)
    prices['DD']=prices.apply(lambda x:x['trade_date'][6:8],axis=1)
    prices['Date']=prices['YYYY']+'-'+prices['MM']+'-'+prices['DD']
    #将交易量从手改为股，1手=100股
    prices['Volume']=prices['vol']*100    
    
    #设置索引    
    import pandas as pd
    prices['DateIndex']=pd.to_datetime(prices['Date'])
    prices.set_index('DateIndex',inplace=True)
    #提取星期
    prices['Weekday']=prices.index.weekday+1

    #按日期升序排序，近期的价格排在后面
    price2=prices.sort_index(axis=0,ascending=True)   
 
    #去掉比起始日期更早的样本
    price2=price2[price2.index >= start]
    #去掉比结束日期更晚的样本
    price2=price2[price2.index <= end]  

    #只保留需要的列
    stockdf=price2[['Stock','Date','Weekday','Open','Close','Volume']]     
 
    return stockdf    


#==============================================================================
def get_portfolio_prices_ts(tickerlist,sharelist,fromdate,todate):
    """
    功能：从tushare抓取投资组合的每日价值
    输入：股票代码列表，份额列表，开始日期，结束日期
    tickerlist: 仅限大陆股票代码列表
    sharelist：持有份额列表，与股票代码列表一一对应
    fromdate: 样本开始日期。格式：'YYYY-MM-DD'
    todate: 样本结束日期。既可以是今天日期，也可以是一个历史日期    
    
    输出：投资组合的价格序列，按照日期升序排列
    """
    
    #仅为调试用的函数入口参数，正式使用前需要注释掉！
    #tickerlist=['601857.SH','000002.SZ']
    #sharelist=[2,1]
    #fromdate='2019-8-1'
    #todate  ='2019-8-31'
    #---------------------------------------------
    
    #检查股票列表个数与份额列表个数是否一致
    if len(tickerlist) != len(sharelist):
        print("Error #1(get_portfolio_prices): numbers of stocks and shares mismatch.")
        return None   

    import pandas as pd
    #循环抓取投资组合中的各个成分股，分别存入开盘价、收盘价和调整收盘价字典
    dict_open={}
    dict_close={}
    for t in tickerlist:
        p=get_stock_prices_ts(t,fromdate,todate)
        if p is None:
            print("Error #2(get_portfolio_prices_ts): fetch stock prices failed.")
            print("Information:",t,fromdate,todate)
            return None
        
        p_open=p.copy()
        p_open2=pd.DataFrame(p_open['Open'])
        p_open2.rename(columns={'Open':t},inplace = True)       
        dict_open[t]=p_open2
        
        p_close=p.copy()
        p_close2=pd.DataFrame(p_close['Close'])
        p_close2.rename(columns={'Close':t},inplace = True)       
        dict_close[t]=p_close2

    #合成各个成分股的开盘价、收盘价    
    for t in tickerlist:
        if t == tickerlist[0]: #第一个成分股
            p_open3=dict_open[t]
            p_close3=dict_close[t]
        else:
            p_open3=pd.merge(p_open3,dict_open[t],how='inner', \
                             left_index=True,right_index=True)
            p_close3=pd.merge(p_close3,dict_close[t],how='inner', \
                             left_index=True,right_index=True)   

    #计算投资组合的开盘价
    oprice=pd.DataFrame(p_open3.dot(sharelist))
    oprice.rename(columns={0:'Open'},inplace=True)    

    #计算投资者的收盘价
    cprice=pd.DataFrame(p_close3.dot(sharelist))
    cprice.rename(columns={0:'Close'},inplace=True) 

    #合成开盘价、收盘价
    prices=pd.merge(oprice,cprice,how='inner',left_index=True,right_index=True)

    #提取日期和星期几
    prices['Date']=prices.index.strftime("%Y-%m-%d")
    prices['Weekday']=prices.index.weekday+1

    prices['Portfolio']=str(tickerlist)
    prices['Shares']=str(sharelist)

    stockdf=prices[['Portfolio','Shares','Date','Weekday','Open','Close']]  

    return stockdf            

#==============================================================================
#以下专门处理fama_french因子数据源
#==============================================================================
def get_ff_factors(start,end,scope='US',factor='FF3',freq='daily'):
    
    import pandas as pd
    s=pd.DataFrame([
        ['US','FF3','monthly','F-F_Research_Data_Factors',0],
        ['US','FF3','yearly','F-F_Research_Data_Factors',1],
        ['US','FF3','weekly','F-F_Research_Data_Factors_weekly',0],
        ['US','FF3','daily','F-F_Research_Data_Factors_daily',0],
        ['US','FF5','monthly','F-F_Research_Data_5_Factors_2x3',0],
        ['US','FF5','yearly','F-F_Research_Data_5_Factors_2x3',1],
        ['US','FF5','daily','F-F_Research_Data_5_Factors_2x3_daily',0],  
        ['US','Mom','monthly','F-F_Momentum_Factor',0],
        ['US','Mom','yearly','F-F_Momentum_Factor',1],
        ['US','Mom','daily','F-F_Momentum_Factor_daily',0],  
        ['US','ST_Rev','monthly','F-F_ST_Reversal_Factor',0],
        ['US','ST_Rev','yearly','F-F_ST_Reversal_Factor',1],
        ['US','ST_Rev','daily','F-F_ST_Reversal_Factor_daily',0],    
        ['US','LT_Rev','monthly','F-F_LT_Reversal_Factor',0],
        ['US','LT_Rev','yearly','F-F_LT_Reversal_Factor',1],
        ['US','LT_Rev','daily','F-F_LT_Reversal_Factor_daily',0],   \
        ['Global','FF3','monthly','Global_3_Factors',0],
        ['Global','FF3','yearly','Global_3_Factors',1],
        ['Global','FF3','daily','Global_3_Factors_Daily',0],   
        ['Global_ex_US','FF3','monthly','Global_ex_US_3_Factors',0],
        ['Global_ex_US','FF3','yearly','Global_ex_US_3_Factors',1],
        ['Global_ex_US','FF3','daily','Global_ex_US_3_Factors_Daily',0],  
        ['Europe','FF3','monthly','Europe_3_Factors',0],
        ['Europe','FF3','yearly','Europe_3_Factors',1],
        ['Europe','FF3','daily','Europe_3_Factors_Daily',0],  
        ['Japan','FF3','monthly','Japan_3_Factors',0],
        ['Japan','FF3','yearly','Japan_3_Factors',1],
        ['Japan','FF3','daily','Japan_3_Factors_Daily',0],    
        ['Asia_Pacific_ex_Japan','FF3','monthly','Asia_Pacific_ex_Japan_3_Factors',0],
        ['Asia_Pacific_ex_Japan','FF3','yearly','Asia_Pacific_ex_Japan_3_Factors',1],
        ['Asia_Pacific_ex_Japan','FF3','daily','Asia_Pacific_ex_Japan_3_Factors_Daily',0],   
        ['North_America','FF3','monthly','North_America_3_Factors',0],
        ['North_America','FF3','yearly','North_America_3_Factors',1],
        ['North_America','FF3','daily','North_America_3_Factors_Daily',0], \
        ['Global','FF5','monthly','Global_5_Factors',0],
        ['Global','FF5','yearly','Global_5_Factors',1],
        ['Global','FF5','daily','Global_5_Factors_Daily',0],   
        ['Global_ex_US','FF5','monthly','Global_ex_US_5_Factors',0],
        ['Global_ex_US','FF5','yearly','Global_ex_US_5_Factors',1],
        ['Global_ex_US','FF5','daily','Global_ex_US_5_Factors_Daily',0],  
        ['Europe','FF5','monthly','Europe_5_Factors',0],
        ['Europe','FF5','yearly','Europe_5_Factors',1],
        ['Europe','FF5','daily','Europe_5_Factors_Daily',0],  
        ['Japan','FF5','monthly','Japan_5_Factors',0],
        ['Japan','FF5','yearly','Japan_5_Factors',1],
        ['Japan','FF5','daily','Japan_5_Factors_Daily',0],    
        ['Asia_Pacific_ex_Japan','FF5','monthly','Asia_Pacific_ex_Japan_5_Factors',0],
        ['Asia_Pacific_ex_Japan','FF5','yearly','Asia_Pacific_ex_Japan_5_Factors',1],
        ['Asia_Pacific_ex_Japan','FF5','daily','Asia_Pacific_ex_Japan_5_Factors_Daily',0],   
        ['North_America','FF5','monthly','North_America_5_Factors',0],
        ['North_America','FF5','yearly','North_America_5_Factors',1],
        ['North_America','FF5','daily','North_America_5_Factors_Daily',0], \
        ['Global','Mom','monthly','Global_Mom_Factor',0],
        ['Global','Mom','yearly','Global_Mom_Factor',1],
        ['Global','Mom','daily','Global_Mom_Factor_Daily',0],   
        ['Global_ex_US','Mom','monthly','Global_ex_US_Mom_Factor',0],
        ['Global_ex_US','Mom','yearly','Global_ex_US_Mom_Factor',1],
        ['Global_ex_US','Mom','daily','Global_ex_US_Mom_Factor_Daily',0],  
        ['Europe','Mom','monthly','Europe_Mom_Factor',0],
        ['Europe','Mom','yearly','Europe_Mom_Factor',1],
        ['Europe','Mom','daily','Europe_Mom_Factor_Daily',0],  
        ['Japan','Mom','monthly','Japan_Mom_Factor',0],
        ['Japan','Mom','yearly','Japan_Mom_Factor',1],
        ['Japan','Mom','daily','Japan_Mom_Factor_Daily',0],    
        ['Asia_Pacific_ex_Japan','Mom','monthly','Asia_Pacific_ex_Japan_MOM_Factor',0],
        ['Asia_Pacific_ex_Japan','Mom','yearly','Asia_Pacific_ex_Japan_MOM_Factor',1],
        ['Asia_Pacific_ex_Japan','Mom','daily','Asia_Pacific_ex_Japan_MOM_Factor_Daily',0],   
        ['North_America','Mom','monthly','North_America_Mom_Factor',0],
        ['North_America','Mom','yearly','North_America_Mom_Factor',1],
        ['North_America','Mom','daily','North_America_Mom_Factor_Daily',0]                 
        ], columns=['scope','factor','freq','symbol','seq'])

    #数据源
    source='famafrench'
    if scope == "China": scope="Asia_Pacific_ex_Japan"
    
    #匹配：scope+factor+freq
    ss=s[s['scope'].isin([scope]) & s['factor'].isin([factor]) \
                                  & s['freq'].isin([freq])]  
    #如果未找到匹配的模式，显示信息后返回
    if len(ss)==0:
        print("Error #1(get_ff_factors): No data item available for",scope,factor,freq)
        return None

    #重新索引，第1行的索引编号为0
    sss=ss.reset_index(drop=True)    
    #取出对应的symbol
    symbol=sss.iloc[0]['symbol']    
    #取出对应的月(0)/年(1)编号
    seq=sss.iloc[0]['seq']

    #抓取数据
    import pandas_datareader.data as web
    try:
        ds = web.DataReader(symbol,source,start,end)
    except:
        print("Error #2(get_ff_factors): Server did not respond")        
        return None
    
    #提取希望的资产定价因子
    factor_df=ds[seq]
    if len(factor_df)==0:
        print("Error #3(get_ff_factors): Server returned empty data for",start,end,scope,factor,freq)
        return None    
    
    return factor_df


if __name__=='__main__':
    ff3_daily=get_ff_factors('2019-05-01','2019-06-30','US','FF3','daily')


#==============================================================================
#以下为线性回归函数
#==============================================================================
def check_reg_sample(X,y):
    """
    功能：检查回归的样本数据是否存在问题
    输入参数：
    X：解释变量
    y：因变量
    输出参数：
    True：样本满足条件，False：不满足回归条件
    """
    result=True
    #检查样本个数是否为空
    if (len(X)==0):
        print("Error #1(check_reg_sample): no obs for independent variable(s)")
        print("Independent variable(s):",X)              
        result=False     
    if (len(y)==0):
        print("Error #2(check_reg_sample): no obs for dependent variable")
        print("Dependent variable:",y)              
        result=False       
        
    #检查样本中是否含有空缺值
    X1=X.dropna()
    if (len(X) != len(X1)):
        print("Error #3(check_reg_sample): missing value(s) in independent variable(s)")
        print("Missing value(s) in independent variable(s):",len(X)-len(X1))              
        result=False     
    y1=y.dropna()
    if (len(y) != len(y1)):
        print("Error #4(check_reg_sample): missing value(s) in dependent variable")
        print("Missing value(s) in dependent variable:",len(y)-len(y1))              
        result=False  
    
    #检查因变量与解释变量的样本个数是否一致
    if len(X) != len(y):
        print("Error #5(check_reg_sample): sample numbers of independent/dependent variables not match")
        print("Obs of X and y respectively:",len(X),len(y))              
        result=False  
    
    return result
    
#==============================================================================
def linreg(X,y):
    """
    函数功能：单个解释变量的简单线性回归，例如CAPM回归。y=a+b*X
    输入参数：
    X: 解释变量。必须为序列，一维数组
    y: 因变量。必须为序列，一维数组
    输出数据：
    beta：解释变量的系数。如果解释变量为单变量则为单一数值，否则为列表
    alpha：截距项
    r_sqr：拟合优度
    p_value：解释变量的系数显著性。如果解释变量为单变量则为单一数值，否则为列表
    std_err：误差项    
    注意：X和y中不能含有NaN/None等空缺值
    """
        
    check=check_reg_sample(X,y)
    if not check:
        print("Error #1(linreg): invalid sample for regression")
        return None,None,None,None,None  

    #一元简单回归
    from scipy import stats 
    (beta,alpha,r_value,p_value,std_err)=stats.linregress(X,y)
    r_sqr=r_value**2
    
    return beta,alpha,r_sqr,p_value,std_err   
    
if __name__=='__main__':
    pass    


#==============================================================================
def sigstars(p_value):
    """
    功能：将p_value转换成显著性的星星
    """
    if p_value >= 0.1: 
        stars="   "
        return stars
    if 0.1 > p_value >= 0.05:
        stars="*  "
        return stars
    if 0.05 > p_value >= 0.01:
        stars="** "
        return stars
    if 0.01 > p_value:
        stars="***"
        return stars

#==============================================================================
def regparms(results):
    """
    功能：将sm回归结果生成数据框，包括变量名称、系数数值、t值、p值和显著性星星
    """
    
    import pandas as pd
    #取系数
    params=results.params
    df_params=pd.DataFrame(params)
    df_params.columns=['coef']
    
    #取t值
    tvalues=results.tvalues
    df_tvalues=pd.DataFrame(tvalues)
    df_tvalues.columns=['t_values']

    #取p值
    pvalues=results.pvalues
    df_pvalues=pd.DataFrame(pvalues)
    df_pvalues.columns=['p_values']            

    #生成星星
    df_pvalues['sig']=df_pvalues['p_values'].apply(lambda x:sigstars(x))
    
    #合成
    parms1=pd.merge(df_params,df_tvalues, \
                    how='inner',left_index=True,right_index=True)
    parms2=pd.merge(parms1,df_pvalues, \
                    how='inner',left_index=True,right_index=True)

    return parms2
#==============================================================================
def smreg(X,y):
    """
    函数功能：多元线性回归。y=a+b1*x1+b2*x2+b3*x3
    输入参数：
    X: 解释变量。多维数组，数据框
    y: 因变量。必须为序列，一维数组
    输出数据：
    beta：解释变量的系数。如果解释变量为单变量则为单一数值，否则为列表
    alpha：截距项
    r_sqr：拟合优度
    p_value：解释变量的系数显著性。如果解释变量为单变量则为单一数值，否则为列表
    std_err：误差项    
    注意：X和y中不能含有NaN/None等空缺值
    """
        
    check=check_reg_sample(X,y)
    if not check:
        print("Error #1(smreg): invalid sample for regression")
        return None,None,None,None,None  

    import statsmodels.api as sm    
    #加入截距项
    X1 = sm.add_constant(X)    
    #多元线性回归
    reg = sm.OLS(y,X1).fit()    
    #回归结果
    parms=regparms(reg)
    
    return parms  
    
if __name__=='__main__':
    pass    
#==============================================================================
#以下为不涉及股票数据源的公共工具函数
#==============================================================================
def draw_lines(df,y_label,x_label,axhline_value,axhline_label,title_txt, \
               data_label=True):
    """
    函数功能：根据df的内容绘制折线图
    输入参数：
    df：数据框。有几个字段就绘制几条折现。必须索引，索引值将作为X轴标记点
    axhline_label: 水平辅助线标记。如果为空值则不绘制水平辅助线
    axhline_value: 水平辅助线的y轴位置
    y_label：y轴标记
    x_label：x轴标记
    title_txt：标题。如需多行，中间用\n分割
    
    输出：
    绘制折线图
    无返回数据
    """
    import matplotlib.pyplot as plt

    #取得df字段名列表
    collist=df.columns.values.tolist()  
    
    #绘制折线图    
    for c in collist:
        plt.plot(df[c],label=c,lw=3)
        #为折线加数据标签
        if data_label==True:
            for a,b in zip(df.index,df[c]):
                plt.text(a,b+0.02,str(round(b,2)), \
                         ha='center',va='bottom',fontsize=7)
    
    #绘制水平辅助线
    if axhline_label !="":
        plt.axhline(y=axhline_value,label=axhline_label,color='green',linestyle=':')  
    
    #坐标轴标记
    plt.ylabel(y_label,fontweight='bold')
    if x_label != "":
        plt.xlabel(x_label,fontweight='bold')
    #图示标题
    plt.title(title_txt,fontweight='bold')
    plt.xticks(rotation=45)
    plt.legend(loc='best')
    plt.show()
    
    return    
    
if __name__=='__main__':
    title_txt="Stock Risk \nCAPM Beta Trends"
    draw_lines(df,"market line",1.0,"Beta coefficient","",title_txt)    



#==============================================================================
def save_to_excel(df,filedir,excelfile,sheetname):
    """
    函数功能：将df保存到Excel文件。
    如果目录不存在提示出错；如果Excel文件不存在则创建之文件并保存到指定的sheet；
    如果Excel文件存在但sheet不存在则增加sheet并保存df内容，原有sheet内容不变；
    如果Excel文件和sheet都存在则追加df内容到已有sheet的末尾
    输入参数：
    df: 数据框
    filedir: 目录
    excelfile: Excel文件名，不带目录，后缀为.xls或.xlsx
    sheetname：Excel文件中的sheet名
    输出：
    保存df到Excel文件
    无返回数据
    
    注意：如果df中含有以文本表示的数字，写入到Excel会被自动转换为数字类型保存。
    从Excel中读出后为数字类型，因此将会与df的类型不一致
    """

    #检查目录是否存在
    import os
    try:
        os.chdir(filedir)
    except:
        print("Error #1(save_to_excel): folder does not exist")        
        print("Information:",filedir)  
        return
                
    #取得df字段列表
    dflist=df.columns
    #合成完整的带目录的文件名
    filename=filedir+'/'+excelfile
    
    import pandas as pd
    try:
        file1=pd.ExcelFile(excelfile)
    except:
        #不存在excelfile文件，直接写入
        df.to_excel(filename,sheet_name=sheetname, \
                       header=True,encoding='utf-8')
        print("***Results saved in",filename,"@ sheet",sheetname)
        return
    else:
        #已存在excelfile文件，先将所有sheet的内容读出到dict中        
        dict=pd.read_excel(file1, None)
    file1.close()
    
    #获得所有sheet名字
    sheetlist=list(dict.keys())
    
    #检查新的sheet名字是否已存在
    try:
        pos=sheetlist.index(sheetname)
    except:
        #不存在重复
        dup=False
    else:
        #存在重复，合并内容
        dup=True
        #合并之前可能需要对df中以字符串表示的数字字段进行强制类型转换.astype('int')
        df1=dict[sheetlist[pos]][dflist]
        dfnew=pd.concat([df1,df],axis=0,ignore_index=True)        
        dict[sheetlist[pos]]=dfnew
    
    #将原有内容写回excelfile    
    result=pd.ExcelWriter(filename)
    for s in sheetlist:
        df1=dict[s][dflist]
        df1.to_excel(result,s,header=True,index=True,encoding='utf-8')
    #写入新内容
    if not dup: #sheetname未重复
        df.to_excel(result,sheetname,header=True,index=True,encoding='utf-8')
    try:
        result.save()
        result.close()
    except:
        print("Error #2(save_to_excel): writing file permission denied")
        print("Information:",filename)  
        return
    print("***Results saved in",filename,"@ sheet",sheetname)
    return    
    
if __name__=='__main__':
    pass
#==============================================================================
def gen_yearlist(start_year,end_year):
    """
    功能：产生从start_year到end_year的一个年度列表
    输入参数：
    start_year: 开始年份，字符串
    end_year：截止年份
    输出参数：
    年份字符串列表    
    """
    #仅为测试使用，完成后应注释掉
    #start_year='2010'
    #end_year='2019'    
    
    import numpy as np
    start=int(start_year)
    end=int(end_year)
    num=end-start+1    
    ylist=np.linspace(start,end,num=num,endpoint=True)
    
    yearlist=[]
    for y in ylist:
        yy='%d' %y
        yearlist=yearlist+[yy]
    #print(yearlist)
    
    return yearlist  
#==============================================================================
  