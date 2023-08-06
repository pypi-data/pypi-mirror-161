# -*- coding: utf-8 -*-
"""
本模块功能：提供全球证券市场行情
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2020年1月5日
最新修订日期：2020年2月2日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
作者邮件：wdehong2000@163.com
版权所有：王德宏
用途限制：仅限研究与教学使用，不可商用！商用需要额外授权。
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
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

if __name__ =="__main__":
    check_period('2020-1-1','2020-2-4')
    check_period('2020-1-1','2010-2-4')
    
#==============================================================================
def get_price(ticker,fromdate,todate):
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
        print("Error #1(get_price): incorrect date or invalid period!")        
        return None         
    
    #抓取雅虎股票价格
    from pandas_datareader import data
    try:
        price=data.DataReader(ticker,'yahoo',start,end)
    except:
        print("Error #2(get_price): failed to get stock prices!")        
        print("Information:",ticker,fromdate,todate) 
        print("Possible reasons:")
        print("  1)internet connection problems.")
        print("  2)incorrect stock code.")
        print("  3)stock delisted or suspended during the period.")
        return None            
    if len(price)==0:
        print("Error #3(get_price): fetched empty stock data!")
        print("Possible reasons:")
        print("  1)internet connection problems.")
        print("  2)incorrect stock code.")
        print("  3)stock delisted or suspended during the period.")
        return None         
    """
    #去掉比起始日期更早的样本
    price2=price[price.index >= fromdate]
    #去掉比结束日期更晚的样本
    price2=price2[price2.index <= todate]
    
    #按日期升序排序，近期的价格排在后面
    sortedprice=price2.sort_index(axis=0,ascending=True)
    """
    return price

if __name__ =="__main__":
    price=get_price('^GSPC','2020-1-1','2020-2-4')
    print(price['Close'].tail(10))
    price=get_price(['000001.SS','^HSI'],'2020-1-1','2020-2-4')
    apclose=price['Close']['^HSI']
    print(price['Close']['^HSI'].tail(10))

#==============================================================================
def compare_price(price,ticker1,ticker2,fromdate,todate):
    """
    功能：比较两支股票的收盘价价格趋势，采用双坐标轴
    输入：
    price：抓取到的多只股票价格序列
    ticker1/ticker2：股票或指数或ETF代码
    fromdate/todate：开始/结束日期
    输出：折线图，双坐标轴，避免数量级差异过大的问题
    """
    #检查期间合理性
    result,start,end=check_period(fromdate,todate)
    if result is None:
        print("Error #1(compare_price): incorrect date or invalid period!")        
        return      
    
    #检查ticker1/ticker2是否已经抓取在price中
    try:
        p1=price['Close'][ticker1]
    except:
        print("Error #2(compare_price): price data not found for",ticker1)
        return
    try:
        p2=price['Close'][ticker2]
    except:
        print("Error #3(compare_price): price data not found for",ticker2)
        return

    #去掉比起始日期更早的样本
    p1b=p1[p1.index >= start]
    p2b=p2[p2.index >= start]
    #去掉比结束日期更晚的样本
    p1c=p1b[p1b.index <= end]
    p2c=p2b[p2b.index <= end]
    
    #绘制折线图，双坐标轴
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(p1c, '-', label = ticker1, lw=3)       
    
    #自动优化x轴标签
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d')) # 格式化时间轴标注
    plt.gcf().autofmt_xdate() # 优化标注（自动倾斜）
    
    #建立第二y轴
    ax2 = ax.twinx()
    ax2.plot(p2c, 'r:.', label = ticker2, lw=3)
    #fig.legend(loc='best', bbox_to_anchor=(1,1), bbox_transform=ax.transAxes)
    #fig.legend(loc='best', bbox_transform=ax.transAxes)
    #fig.legend(loc='best')
    
    plt.title("Compare Securities Price", fontsize=18)
    ax.set_xlabel("\nSource: Yahoo Finance", fontsize=13)
    ax.set_ylabel(ticker1)
    ax.legend(loc='lower left')
    ax2.legend(loc='upper right')
    ax2.set_ylabel(ticker2)
    fig.show()

if __name__ =="__main__":
    tickerlist=['000001.SS','601939.SS','^HSI','0939.HK']
    price=get_price(tickerlist,'2019-1-1','2019-12-31')
    ticker1='000001.SS'
    ticker2='^HSI'
    fromdate='2019-11-1'
    todate='2019-12-31'
    compare_price(price,'601939.SS','000001.SS','2019-1-1','2019-12-31')
    compare_price(price,'601939.SS','000001.SS','2019-8-1','2019-9-1')
    compare_price(price,'0939.HK','^HSI','2019-8-1','2019-9-1')
    compare_price(price,'000001.SS','^HSI','2019-7-1','2019-10-1')
    compare_price(price,'601939.SS','000001.SS','2019-11-15','2019-12-1')
#==============================================================================
def compare_return(price,ticker1,ticker2,fromdate,todate):
    """
    功能：比较两支股票的收盘价价格趋势，采用双坐标轴
    输入：
    price：抓取到的多只股票价格序列
    ticker1/ticker2：股票或指数或ETF代码
    fromdate/todate：开始/结束日期
    输出：折线图，双坐标轴，避免数量级差异过大的问题
    """
    #检查期间合理性
    result,start,end=check_period(fromdate,todate)
    if result is None:
        print("Error #1(compare_price): incorrect date or invalid period!")        
        return      
    
    #检查ticker1/ticker2是否已经抓取在price中
    try:
        p1=price['Close'][ticker1]
    except:
        print("Error #2(compare_price): price data not found for",ticker1)
        return
    try:
        p2=price['Close'][ticker2]
    except:
        print("Error #3(compare_price): price data not found for",ticker2)
        return

    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import pandas as pd
    
    #绘制折线图      
    r1=p1.pct_change()
    r1df=pd.DataFrame(r1)
    r1df.columns=['ret']
    r1df['ret%']=round(r1df['ret']*100.0,2)   
    
    r1dfs1=r1df[r1df.index >= start]
    r1dfs2=r1dfs1[r1dfs1.index <= end]
    
    plt.plot(r1dfs2['ret%'],label=ticker1,lw=3)
    
    r2=p2.pct_change()
    r2df=pd.DataFrame(r2)
    r2df.columns=['ret']
    r2df['ret%']=round(r2df['ret']*100.0,2)  
    
    r2dfs1=r2df[r2df.index >= start]
    r2dfs2=r2dfs1[r2dfs1.index <= end]    
    
    plt.plot(r2dfs2['ret%'],label=ticker2,lw=3,ls=':')  
    
    #纵轴零线
    plt.axhline(y=0.0,color='green',linestyle='--')

    #图示标题
    titletxt="Compare Security Returns"
    plt.title(titletxt,fontweight='bold', fontsize=18)
    plt.ylabel("Capital gain %")
    plt.xlabel("Data source: Yahoo Finance")
    #plt.xticks(rotation=45)
    #自动优化x轴标签
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    plt.gcf().autofmt_xdate() # 优化标注（自动倾斜）    
    plt.legend(loc='best')
    plt.show()    


if __name__ =="__main__":
    tickerlist=['000001.SS','601939.SS','^HSI','0939.HK']
    price=get_price(tickerlist,'2019-1-1','2019-12-31')
    compare_return(price,'601939.SS','000001.SS','2019-8-1','2019-9-1')
    compare_return(price,'0939.HK','^HSI','2019-8-1','2019-9-1')
    compare_return(price,'000001.SS','^HSI','2019-7-1','2019-10-1')


#==============================================================================
#以下使用雅虎+tushare混合数据源
#==============================================================================
def ts_token():    
    """
    功能：获得tushare的token
    输入：无
    输出：tushare的token
    """
    import tushare as ts
    token='49f134b05e668d288be43264639ac77821ab9938ff40d6013c0ed24f'
    pro=ts.pro_api(token)
    
    return pro

if __name__ =="__main__":
    pro=ts_token() 
#==============================================================================
def cvtdate_yahootots(yahoodate):
    """
    功能：日期格式转换, YYYY-MM-DD转换为YYYYMMDD
    输入：日期，YYYY-MM-DD
    输出：日期，YYYYMMDD
    """
    import pandas as pd
    try:
        dateu=pd.to_datetime(yahoodate)
    except:
        print("Error #1(datecvt_yahootots): invalid date:",yahoodate)
        return None

    yyyy=str(dateu.year)
    mm=dateu.month
    if mm <= 9: mm='0'+str(mm)
    else: mm=str(mm)
    dd=dateu.day
    if dd <= 9: dd='0'+str(dd)
    else: dd=str(dd)
    tsdate=yyyy+mm+dd   
    
    return tsdate

if __name__ =="__main__":
    yahoodate='2019-12-5'
    tsdate=cvtdate_yahootots(yahoodate)
    print(tsdate)
#==============================================================================
def cvtticker_yahootots(yahooticker):
    """
    功能：股票代码格式转换, xxxxxx.SS转换为xxxxxx.SH
    输入：股票代码，xxxxxx.SS
    输出：股票代码，xxxxxx.SH
    """
    
    tsticker=yahooticker
    suffix=yahooticker[-3:]
    if suffix == '.SS':
        tsticker=yahooticker.replace(suffix,'.SH')
    
    return tsticker

if __name__ =="__main__":
    yahooticker='601939.SS'
    tsticker=cvtticker_yahootots(yahooticker) 
#==============================================================================    
def ts_price_stock(ticker,fromdate,todate):
    """
    功能：从tushare数据源获得股票行情数据
    输入：
    ticker: 大陆股票代码，上交所后缀为.SS，深交所后缀为.SZ
    fromdate：开始日期，格式YYYY-MM-DD
    todate：结束日期
    输出：
    行情数据，df，雅虎格式
    """
    #设置tushare的token
    pro=ts_token()

    #检查期间合理性
    result,start,end=check_period(fromdate,todate)
    if result is None:
        print("Error #1(ts_price_stock): incorrect date or invalid period!")        
        return None 
    
    #转换输入日期
    tsstart=cvtdate_yahootots(fromdate)
    tsend=cvtdate_yahootots(todate)
    #转换股票代码
    tsticker=cvtticker_yahootots(ticker)
    
    #抓取股票日行情
    price=pro.daily(ts_code=tsticker,start_date=tsstart,end_date=tsend)
    
    #升序排列
    price.sort_values('trade_date',ascending=True,inplace=True)
    
    #转换日期格式，设置日期索引
    import pandas as pd
    price['date']=pd.to_datetime(price['trade_date'])
    price.set_index('date',inplace=True)
    
    #修改列名
    price.rename(columns= \
        {'ts_code':'Ticker','open':'Open','high':'High','low':'Low', \
         'close':'Close','vol':'Volume'},inplace=True)
    
    #删除不需要的列
    price.drop(['trade_date','pre_close','change','pct_chg','amount'], \
               axis=1,inplace=True)        
    
    return price

if __name__ =="__main__":
    ticker='601939.SS'
    fromdate='2019-12-11'
    todate='2020-02-05'
    price=ts_price_stock(ticker,fromdate,todate) 

#==============================================================================    
def ts_price_index(ticker,fromdate,todate):
    """
    功能：从tushare数据源获得指数行情数据
    输入：
    ticker: 大陆指数代码，上交所后缀为.SS，深交所后缀为.SZ
    fromdate：开始日期，格式YYYY-MM-DD
    todate：结束日期
    输出：
    行情数据，df，雅虎格式
    """
    #设置tushare的token
    pro=ts_token()

    #检查期间合理性
    result,start,end=check_period(fromdate,todate)
    if result is None:
        print("Error #1(ts_price_stock): incorrect date or invalid period!")        
        return None 
    
    #转换输入日期
    tsstart=cvtdate_yahootots(fromdate)
    tsend=cvtdate_yahootots(todate)
    #转换指数代码
    tsticker=cvtticker_yahootots(ticker)
    
    #抓取指数日行情
    price=pro.index_daily(ts_code=tsticker,start_date=tsstart,end_date=tsend)
    
    #升序排列
    price.sort_values('trade_date',ascending=True,inplace=True)
    
    #转换日期格式，设置日期索引
    import pandas as pd
    price['date']=pd.to_datetime(price['trade_date'])
    price.set_index('date',inplace=True)
    
    #修改列名
    price.rename(columns= \
        {'ts_code':'Ticker','open':'Open','high':'High','low':'Low', \
         'close':'Close','vol':'Volume'},inplace=True)
    price['Ticker']=ticker
        
    #删除不需要的列
    price.drop(['trade_date','pre_close','change','pct_chg','amount'], \
               axis=1,inplace=True)        
    
    return price

if __name__ =="__main__":
    ticker='000300.SS'
    fromdate='2019-12-11'
    todate='2020-02-05'
    price=ts_price_index(ticker,fromdate,todate)     

#==============================================================================    
def ts_nav_etf(etf_code,fromdate,todate):
    """
    功能：从tushare获得etf每日净值数据，便于与二级市场行情比较套利空间
    输入：
    etf_code: 大陆etf代码，雅虎格式，上交所后缀为.SS，深交所后缀为.SZ
    fromdate：开始日期，格式YYYY-MM-DD
    todate：结束日期
    输出：
    行情数据，df，升序排列
    """
    #设置tushare的token
    pro=ts_token()

    #检查期间合理性
    result,start,end=check_period(fromdate,todate)
    if result is None:
        print("Error #1(ts_price_stock): incorrect date or invalid period!")        
        return None 
    
    #转换输入日期格式
    tsstart=cvtdate_yahootots(fromdate)
    tsend=cvtdate_yahootots(todate)
    #转换etf代码
    tsticker=cvtticker_yahootots(etf_code)
    
    #抓取每日etf净值行情
    price=pro.fund_nav(ts_code=tsticker)
    
    #升序排列
    price.sort_values('end_date',ascending=True,inplace=True)
    
    #转换日期格式，设置日期索引
    import pandas as pd
    price['date']=pd.to_datetime(price['end_date'])
    price.set_index('date',inplace=True)
    
    #修改列名
    price.rename(columns={'ts_code':'Ticker','unit_nav':'Unit-nav', \
                          'adj_nav':'Adj-nav'},inplace=True)
    price['Ticker']=etf_code
        
    #提取需要的列
    nav=price[['Ticker','Unit-nav']].copy()
    
    #去掉日期范围以外的数据
    nav1=nav[nav.index >= start]
    nav2=nav1[nav1.index <= end]
    
    return nav2

if __name__ =="__main__":
    etf_code='510050.SS'
    fromdate='2019-12-11'
    todate='2020-02-01'
    etf_nav=ts_nav_etf(etf_code,fromdate,todate)     

#==============================================================================
def get_price_etf(etf_code,index_code,fromdate,todate):
    """
    功能：获得etf及其对应指数日行情，便于对比业绩
    Parameters
    ----------
    etf_code : ETF代码，雅虎格式
    index_code : 指数代码，雅虎格式
    fromdate : 开始日期，雅虎格式
    todate : 截止日期，雅虎格式
    Returns
    -------
    日行情价格，etf与指数数据，升序排列
    """

    #检查期间合理性
    result,start,end=check_period(fromdate,todate)
    if result is None:
        print("Error #1(get_price_etf): incorrect date or invalid period!")        
        return None 

    #从雅虎财经获得etf日行情
    etf=get_price(etf_code,fromdate,todate)
    try: etf['Ticker']=etf_code
    except:
        print("Error #2(get_price_etf): data not found for",etf_code)        
        return None,None        

    #去掉日期范围以外的数据
    etf1=etf[etf.index >= start]
    etf2=etf1[etf1.index <= end]
    
    #获得指数日行情
    flag1=index_code[0]
    flag2=index_code[-3:]
    if (flag1 != '^') and ((flag2 == '.SS') or (flag2 == '.SZ')):
        #从tushare获得中国大陆指数行情
        index=ts_price_index(index_code,fromdate,todate)
    else:
        #从雅虎财经获得非中国大陆指数行情
        index=get_price(index_code,fromdate,todate)

    try: index['Ticker']=index_code
    except:
        print("Error #3(get_price_etf): data not found for",index_code)        
        return None,None        
    
    #去掉日期范围以外的数据
    index1=index[index.index >= start]
    index2=index1[index1.index <= end]

    return etf2,index2

if __name__ =="__main__":
    etf_code='510050.SS'
    index_code='000016.SS'
    fromdate='2019-12-11'
    todate='2020-02-05'
    etf_price,index_price=get_price_etf(etf_code,index_code,fromdate,todate)  

#==============================================================================
def compare_price_etf(etf_price,index_price,fromdate,todate):
    """
    功能：比较etf与对应指数的收盘价趋势，采用双坐标轴
    输入：
    etf_price：抓取到的etf价格序列
    index_price：抓取到的指数价格序列
    fromdate/todate：开始/结束日期
    输出：折线图，双坐标轴，避免数量级差异过大的问题
    """
    #检查期间合理性
    result,start,end=check_period(fromdate,todate)
    if result is None:
        print("Error #1(compare_price_etf): incorrect date or invalid period!")        
        return      

    #检查价格序列
    if (etf_price is None) or (index_price is None):
        print("Error #2(compare_price_etf): incorrect input for either etf or index")        
        return 
    
    #提取收盘价
    p1=etf_price['Close']
    try: ticker1=etf_price['Ticker'][0]
    except:
        print("Error #2(compare_price_etf): no data available for the etf!")        
        return         
    p2=index_price['Close']
    try: ticker2=index_price['Ticker'][0]
    except:
        print("Error #3(compare_price_etf): no data available for the index!")        
        return  

    #去掉比起始日期更早的样本
    p1b=p1[p1.index >= start]
    p2b=p2[p2.index >= start]
    #去掉比结束日期更晚的样本
    p1c=p1b[p1b.index <= end]
    p2c=p2b[p2b.index <= end]
    
    #绘制折线图，双坐标轴
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(p1c, '-', label = ticker1, lw=3)       
    
    #自动优化x轴标签，格式化时间轴标注
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d')) 
    plt.gcf().autofmt_xdate() # 优化标注（自动倾斜）
    
    #建立第二y轴
    ax2 = ax.twinx()
    ax2.plot(p2c, 'r:.', label = ticker2, lw=3)
    #fig.legend(loc='best', bbox_to_anchor=(1,1), bbox_transform=ax.transAxes)
    #fig.legend(loc='best', bbox_transform=ax.transAxes)
    #fig.legend(loc='best')
    
    plt.title("Sync of ETF Price and Index Based", fontsize=15)
    ax.set_xlabel("\nSource: Yahoo Finance", fontsize=13)
    ax.set_ylabel(ticker1)
    ax.legend(loc='upper center')
    ax2.legend(loc='lower center')
    ax2.set_ylabel(ticker2)
    fig.show()
    
    return

if __name__ =="__main__":
    etf_code='510050.SS'
    index_code='000016.SS'
    fromdate='2019-7-1'
    todate='2020-02-05'
    etf_price,index_price=get_price_etf(etf_code,index_code,fromdate,todate)
    compare_price_etf(etf_price,index_price,'2019-7-1','2019-12-1')
    compare_price_etf(etf_price,index_price,'2019-7-1','2019-8-1')

#==============================================================================
def get_price_nav_etf(etf_code,fromdate,todate):
    """
    功能：获得etf每日二级市场行情以及净值，便于寻找套利机会，限大陆etf
    Parameters
    ----------
    etf_code : ETF代码，雅虎格式
    fromdate : 开始日期，雅虎格式
    todate : 截止日期，雅虎格式
    Returns
    -------
    etf日二级市场行情价格，etf每日净值，升序排列
    """

    #检查期间合理性
    result,start,end=check_period(fromdate,todate)
    if result is None:
        print("Error #1(get_price_nav_etf): incorrect date or invalid period!")        
        return None 

    #从雅虎财经获得etf日行情
    etf=get_price(etf_code,fromdate,todate)
    etf['Ticker']=etf_code

    #去掉日期范围以外的数据
    etf1=etf[etf.index >= start]
    etf2=etf1[etf1.index <= end]
    
    #获得大陆etf每日净值    
    nav2=ts_nav_etf(etf_code,fromdate,todate)

    return etf2,nav2

if __name__ =="__main__":
    etf_code='510050.SS'
    fromdate='2019-1-1'
    todate='2020-02-05'
    etf_price,etf_nav=get_price_nav_etf(etf_code,fromdate,todate)  

#==============================================================================
def compare_price_nav_etf(etf_price,etf_nav,fromdate,todate):
    """
    功能：比较etf二级市场行情与其净值趋势
    输入：
    etf_price：抓取到的etf二级市场价格序列
    etf_nav：抓取到的etf净值序列
    fromdate/todate：开始/结束日期
    输出：折线图
    """
    #检查期间合理性
    result,start,end=check_period(fromdate,todate)
    if result is None:
        print("Error #1(compare_price_nav_etf): incorrect date or invalid period!")        
        return      
    
    #提取收盘价
    p1=etf_price['Close']
    try: ticker1=etf_price['Ticker'][0]+" price"
    except:
         print("Error #2(compare_price_nav_etf): no data available for the etf price!")        
         return          
    p2=etf_nav['Unit-nav']
    try: ticker2=etf_nav['Ticker'][0]+" nav"
    except:
         print("Error #3(compare_price_nav_etf): no data available for the etf nav!")        
         return     

    #去掉比起始日期更早的样本
    p1b=p1[p1.index >= start]
    p2b=p2[p2.index >= start]
    #去掉比结束日期更晚的样本
    p1c=p1b[p1b.index <= end]
    p2c=p2b[p2b.index <= end]
    
    #绘制折线图
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    
    plt.plot(p1c, '-', label = ticker1, lw=3)
    plt.plot(p2c, 'r:.', label = ticker2, lw=3)
    
    #自动优化x轴标签，格式化时间轴标注
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d')) 
    plt.gcf().autofmt_xdate() # 优化标注（自动倾斜）

    plt.title("ETF Arbitrage: Market Price vs. Net Asset Value", fontsize=13)
    plt.xlabel("\nSource: Yahoo Finance, Sina Finance", fontsize=11)
    plt.ylabel('Unit price/net asset value')
    plt.legend(loc='best')
    plt.show()    
    
    return

if __name__ =="__main__":
    etf_code='510050.SS'
    fromdate='2019-8-1'
    todate='2019-9-1'
    etf_price,etf_nav=get_price_nav_etf(etf_code,fromdate,todate)
    compare_price_nav_etf(etf_price,etf_nav,fromdate,todate)

#==============================================================================
def compare_return_nav_etf(etf_price,etf_nav,fromdate,todate):
    """
    功能：比较etf二级市场行情与其净值的收益率
    输入：
    etf_price：抓取到的etf二级市场价格序列
    etf_nav：抓取到的etf净值序列
    fromdate/todate：开始/结束日期
    输出：收益率折线图
    """
    #检查期间合理性
    result,start,end=check_period(fromdate,todate)
    if result is None:
        print("Error #1(compare_return_nav_etf): incorrect date or invalid period!")        
        return      
    
    #提取收盘价的收益率
    import pandas as pd
    cp=etf_price['Close']
    r1=cp.pct_change()
    r1df=pd.DataFrame(r1)
    r1df.columns=['ret']
    r1df['ret%']=round(r1df['ret']*100.0,2)    
    p1=r1df['ret%']
    try: ticker1=etf_price['Ticker'][0]+" market return"
    except:
         print("Error #2(compare_return_nav_etf): no data available for the etf price!")        
         return          
    
    nv=etf_nav['Unit-nav']
    r2=nv.pct_change()
    r2df=pd.DataFrame(r2)
    r2df.columns=['ret']
    r2df['ret%']=round(r2df['ret']*100.0,2)  
    p2=r2df['ret%']    
    try: ticker2=etf_nav['Ticker'][0]+" nav gain"
    except:
         print("Error #3(compare_return_nav_etf): no data available for the etf nav!")        
         return     

    #去掉比起始日期更早的样本
    p1b=p1[p1.index >= start]
    p2b=p2[p2.index >= start]
    #去掉比结束日期更晚的样本
    p1c=p1b[p1b.index <= end]
    p2c=p2b[p2b.index <= end]
    
    #绘制折线图
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    
    plt.plot(p1c, '-', label = ticker1, lw=3)
    plt.plot(p2c, 'r:.', label = ticker2, lw=3)
    
    #纵轴零线
    plt.axhline(y=0.0,color='green',linestyle='--')
    
    #自动优化x轴标签，格式化时间轴标注
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d')) 
    plt.gcf().autofmt_xdate() # 优化标注（自动倾斜）

    plt.title("ETF Arbitrage: Market Return vs. Nav Gain", fontsize=13)
    plt.xlabel("\nSource: Yahoo Finance, Sina Finance", fontsize=11)
    plt.ylabel('Market return/nav gain(%)')
    plt.legend(loc='best')
    plt.show()    
    
    return

if __name__ =="__main__":
    etf_code='510050.SS'
    fromdate='2019-8-1'
    todate='2019-9-1'
    etf_price,etf_nav=get_price_nav_etf(etf_code,fromdate,todate)
    compare_return_nav_etf(etf_price,etf_nav,fromdate,todate)
#==============================================================================

#==============================================================================

#==============================================================================    
def get_price_ts(ticker,fromdate,todate,asset='E',freq='D'):
    """
    功能：从tushare数据源获得交易数据
    
    Parameters
    ----------
    ticker : 资产代码
        包括股票、指数、数字货币、期货、基金、期货、可转债.
    fromdate : 开始日期
        格式：YYYY-MM-DD. 注意tushare的格式为YYYYMMDD
    todate : 截止日期
        格式：YYYY-MM-DD.
    asset : 资产类别, optional
        包括股票(E)、沪深指数(I)、数字货币(C)、期货(FT)、基金(FD)、期权(O)、
        可转债(CB). The default is 'E'.
    freq : 频率, optional
        数据频度：支持分钟(min)/日(D)/周(W)/月(M)K线，
        其中1min表示1分钟（类推1/5/15/30/60分钟），默认D.
    Returns
    -------
    价格行情，数据框，升序排列.
    """
