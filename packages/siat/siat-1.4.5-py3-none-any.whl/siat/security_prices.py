# -*- coding: utf-8 -*-
"""
版权：王德宏，北京外国语大学国际商学院
功能：
1、获取证券价格，多种方法，解决网络超时问题
2、既可获取单一证券的价格，也可获取证券组合的价格
3、与爬虫过程有关的错误信息尽可能都在本过程中处理
版本：1.0，2021-1-31
"""

#==============================================================================
#关闭所有警告
import warnings; warnings.filterwarnings('ignore')
from siat.common import *
from siat.translate import *
#==============================================================================
import pandas as pd

#==============================================================================
#==============================================================================
def get_price(ticker,fromdate,todate,adj=False):
    """
    套壳函数get_prices，为保持兼容
    """
    df=get_prices(ticker,fromdate,todate,adj=adj)
    return df
#==============================================================================
if __name__=='__main__':
    ticker='AAPL'
    fromdate='2011-1-1'
    todate='2020-12-31'
    retry_count=3
    pause=1
    
    ticker='ABCD'
    
    ticker=['AAPL','MSFT']
    ticker=['AAPL','MSFT','ABCD']
    
    ticker=['600011.SS']
    fromdate='2020-1-1'
    todate='2020-6-30'    

def get_prices(ticker,fromdate,todate,adj=False,retry_count=3,pause=1):
    """
    功能：抓取证券价格，pandas_datareader + yfinance + akshare
    输出：指定收盘价格序列，日期升序排列
    ticker: 股票代码或其列表。大陆股票代码加上后缀.SZ或.SS，港股代码去掉前导0加后缀.HK
    start: 样本开始日期，yyyy-mm-dd
    end: 样本结束日期，既可以是今天日期，也可以是一个历史日期
    retry_count：网络失败时的重试次数
    pause：每次重试前的间隔秒数
    """
    print("  Searching prices for corresponding securities, please wait ...")
    
    #检查日期期间的合理性
    result,start,end=check_period(fromdate,todate)
    if not result:
        print("  #Error(get_prices): invalid date period from",fromdate,'to',todate)
        return None     

    #尝试pandas_datareader+FRED（仅对部分国外市场指数有效） 
    if ticker[0]=='^':
        print("  Trying to capture info from fred for",ticker)
        prices=get_index_fred(ticker,start,end)
        if prices is None:
            print("  #Warning(get_prices): info retrieving failed from fred for",ticker)
        else:
            if len(prices)==0:
                print("  #Warning(get_prices): zero record found in fred for",ticker)
            else:
                return prices
    
    #尝试AkShare+Sina+EM（新浪，对中国内地股票、港股和美股有效，但不包括国外市场指数）
    #printmsg=str(ticker)+" from "+fromdate+' to '+todate
    print("  Trying to capture prices from sina/EM for",ticker)
    try:
        #prices=get_prices_ak(ticker,fromdate,todate,adjust=adj)
        prices=get_prices_ak(ticker,fromdate,todate)
    except:
        print("  #Warning(get_prices): info retrieving failed from sina/EM for",ticker)
        #return None 
    else:
        if prices is None: 
            print("  #Warning(get_prices): info not found from sina/EM for",ticker)
        else:
            num=len(prices)
            if num==0:
                print("  #Warning(get_prices): zero record found in sina/EM for",ticker)
            else:
                #print("  Successfully retrieved",num,"records for",ticker)
                return prices        

    #尝试pandas_datareader+stooq（对美股、港股、欧股、国外市场指数有效，但对深交所股票无效）
    #注意stooq代码与新浪/stooq的不同
    print("  Trying to capture info from stooq for",ticker)
    try:
        prices=get_price_stooq(ticker,fromdate,todate)
    except:
        print("  #Warning(get_prices): info retrieving failed from stooq for",ticker)
        #return None 
    else:
        if prices is None: 
            print("  #Warning(get_prices): info not found from stooq for",ticker)
        else:
            num=len(prices)
            if num==0:
                print("  #Warning(get_prices): zero record found for",ticker)
            else:
                #print("  Successfully retrieved",num,"records for",ticker)
                return prices        
    
    #使用yahoo+yfinance抓取数据                
    #由于雅虎无法访问，建议暂时关闭，2021-10-24
    #抓取证券（列表）价格，需要调整收盘价：yfinance优先，线程极易出错，先尝试关闭线程
    try:
        print("  Trying to capture info from Yahoo Finance using non-threads for",ticker)
        prices=get_prices_yf(ticker,start,end,threads=False)
    except:
        print("  #Warning(get_prices): retrieving using non-threads failed from yahoo for",ticker)
    else:
        if prices is None: 
            print("  #Warning(get_prices): info not found using non-threads failed from yahoo for",ticker)
        else:
            num=len(prices)
            if num==0:
                print("  #Warning(get_prices): zero record found for",ticker)
            else:
                #print("  Successfully retrieved",num,"records for",ticker)
                return prices        

    #抓取证券（列表）价格，需要调整收盘价：yfinance优先，尝试打开线程
    try:
        print("  Trying to capture info from Yahoo Finance using threads for",ticker)
        prices=get_prices_yf(ticker,start,end,threads=True)
    except:
        print("  #Warning(get_prices): retrieving using threads failed from yahoo for",ticker)
    else:
        if prices is None: 
            print("  #Warning(get_prices): info not found using non-threads failed from yahoo for",ticker)
        else:
            num=len(prices)
            if num==0:
                print("  #Warning(get_prices): zero record found for",ticker)
            else:
                #print("  Successfully retrieved",num,"records for",ticker)
                return prices        
    
    #抓取证券（列表）价格，不考虑是否需要调整收盘价：pandas_datareader
    #由于雅虎财经当前无法访问，建议本段停用
    #由于雅虎无法访问，暂时关闭，2021-10-24
    try:    
        print("  Trying to capture info from Yahoo Finance in traditional process for",ticker)
        prices=get_prices_yahoo(ticker,start,end,retry_count=retry_count,pause=pause)
    except:    
        print("  #Warning(get_prices): info retrieving failed from Yahoo Finance in traditional process for",ticker)    
        return None    
    else:
        if prices is None: 
            print("  #Warning(get_prices): info not found  from Yahoo Finance in traditional process for",ticker)
        else:
            num=len(prices)
            if num==0:
                print("  #Warning(get_prices): zero record found for",ticker)
            else:
                #print("  Successfully retrieved",num,"records for",ticker)
                return prices        
    
    #若能够抓取到数据均已提前返回，到达此处时表面未能抓取到任何数据
    print("  #Warning(get_prices): tried everyting but nothing found for",ticker)
    return None
    
    

if __name__=='__main__':
    get_prices('INTC','2021-11-1','2021-11-5')
    get_prices('BMW.DE','2021-11-1','2021-11-5')
    get_prices(['INTC'],'2021-11-1','2021-11-5')
    get_prices(['XYZ'],'2021-11-1','2021-11-5')
    df4=get_prices(['INTC','MSFT'],'2021-11-1','2021-11-5')
    df5=get_prices(['INTC','UVW'],'2021-11-1','2021-11-5')
    df6=get_prices(['00988.HK','000858.SZ'],'2021-11-1','2021-11-5')
    df7=get_prices(['INTL','MSFT','00988.HK','000858.SZ'],'2021-11-1','2021-11-5')
    
#==============================================================================
if __name__=='__main__':
    ticker='600000.SS'
    fromdate='2021-11-1'
    todate='2021-11-5'
    adjust=''

#在common中定义
#SUFFIX_LIST_CN=['SS','SZ','BJ','NQ']

def get_price_ak_em(ticker,fromdate,todate,adjust=''):
    """
    功能：基于东方财富从akshare获得中国国内的股票和指数历史行情，只能处理单个股票，处理指数有时出错
    ticker：雅虎格式，沪市股票为.SS，深市为.SZ，北交所为.BJ，其他的不处理，直接返回None
    fromdate：格式为YYYY-m-d，需要改造为YYYYMMDD
    todate：格式为YYYY-m-d，需要改造为YYYYMMDD
    adjust：不考虑复权为''，后复权为'hfq'，前复权为'qfq'
    返回结果：雅虎格式，日期升序，列明首字母大写等
    """
    #变换代码格式
    ticker1=ticker.upper()
    result,prefix,suffix=split_prefix_suffix(ticker1)
    
    #若不是A股则返回
    if not (suffix in SUFFIX_LIST_CN):
        print("  #Warning(get_price_ak_em): function not suitable for",ticker)
        return None
    else:
        ticker2=prefix
    
    #变换日期格式
    result,start,end=check_period(fromdate,todate)
    if not result:
        print("  #Warning(get_price_ak_em): invalid date period from",fromdate,'to',todate)
        return None   
    start1=start.strftime('%Y%m%d')
    end1=end.strftime('%Y%m%d')
    
    #检查复权选项
    adjustlist=['','none','hfq','qfq']
    if adjust not in adjustlist:
        print("  #Warning(get_price_ak_em): invalid close adjustment",adjust)
        return None          
    if adjust=='none': adjust=''
    
    #抓取股价，含复权选项
    import akshare as ak
    try:
        #bug: 股票代码为399xxx时出错
        df=ak.stock_zh_a_hist(symbol=ticker2,period="daily",start_date=start1,end_date=end1,adjust=adjust)
    except:
        print("  #Warning(get_price_ak_em): failed to find prices from EM for",ticker)
        return None
    
    #检查抓取到的结果
    if df is None:
        print("  #Warning(get_price_ak_em): no record found from EM for",ticker)
        return None
    if len(df)==0:
        print("  #Warning(get_price_ak_em): zero record found from EM for",ticker)
        return None

    #升序排序
    df.sort_values(by=['日期'],ascending=[True],inplace=True)
    
    #调整数据格式
    df['Date']=pd.to_datetime(df['日期'])
    df.set_index(['Date'],inplace=True)

    df.rename(columns={'开盘':'Open','收盘':'Close','最高':'High','最低':'Low', \
                       '成交量':'Volume','成交额':'Amount','换手率':'Turnover'},inplace=True)
    df1=df[['Open','Close','High','Low','Volume','Amount','Turnover']]
    
    df1['source']='东方财富'
    df1['ticker']=str(ticker)
    df1['Adj Close']=df1['Close']
    df1['footnote']=adjust    
    print("  Successfully retrieved",len(df1),"records for",ticker)

    return df1
    

if __name__=='__main__':
    df1=get_price_ak_em('600519.SS','2020-12-1','2020-12-5',adjust='none')
    df2=get_price_ak_em('600519.SS','2020-12-1','2021-2-5',adjust='hfq')
    df3=get_price_ak_em('399001.SZ','2020-12-1','2021-2-5') #出错
    df4=get_price_ak_em('000688.SS','2020-12-1','2021-2-5')
    df5=get_price_ak_em('AAPL','2020-12-1','2021-2-5')
    df6=get_price_ak_em('000001.SS','2020-12-1','2021-2-5')
    df7=get_price_ak_em('000002.SS','2020-12-1','2021-2-5')
    df7=get_price_ak_em('000300.SS','2020-12-1','2021-2-5')

#==============================================================================
def cvt_stooq_suffix(symbol):
    """
    映射雅虎后缀符号至stooq后缀符号
    输入：雅虎后缀符号。输出：stooq后缀符号
    """
    import pandas as pd
    suffix=pd.DataFrame([
        ['SS','CN'], ['SZ','CN'], ['T','JP'], 
        
        ], columns=['yahoo','stooq'])

    try:
        stooq=suffix[suffix['yahoo']==symbol]['stooq'].values[0]
    except:
        #未查到翻译词汇，返回原词
        stooq=symbol
   
    return stooq

if __name__=='__main__':
    cvt_stooq_suffix('SS')
    cvt_stooq_suffix('SZ')
    cvt_stooq_suffix('T')
#==================================================================================
def cvt_stooq_symbol(symbol):
    """
    映射雅虎指数符号至stooq指数符号
    输入：雅虎指数符号。输出：stooq指数符号
    """
    import pandas as pd
    suffix=pd.DataFrame([
        ['^GSPC','^SPX'], ['^IXIC','^NDQ'], ['^IXIC','^NDX'], 
        ['^RUT','QR.F'],
        ['000001.SS','^SHC'],  
        ['^N225','^NKX'], ['^TWII','^TWSE'], ['^KS11','^KOSPI'],
        ['^BSESN','^SNX'],['^FTSE','^FTM'], ['^GDAXI','^DAX'],
        ['^FCHI','^CAC'], ['IMOEX.ME','^MOEX'], 
        
        ], columns=['yahoo','stooq'])

    result=False
    try:
        stooq=suffix[suffix['yahoo']==symbol]['stooq'].values[0]
        result=True
    except:
        #未查到翻译词汇，返回原词
        stooq=symbol
   
    return result,stooq

if __name__=='__main__':
    cvt_stooq_symbol('^GSPC')
    cvt_stooq_symbol('^IXIC')
    cvt_stooq_symbol('000001.SS')
#==================================================================================
if __name__=='__main__':
    ticker='600519.SS'

def cvt_stooq_ticker(ticker):
    """
    映射雅虎证券符号至stooq证券符号
    输入：雅虎证券符号。输出：stooq证券符号
    局限：无法处理深交所股票代码！！！！！
    """
    #直接转换
    result,ticker_stooq=cvt_stooq_symbol(ticker)
    if result:
        return ticker_stooq
    
    #拆分前缀后缀
    result,prefix,suffix=split_prefix_suffix(ticker)
    
    #去掉前导0
    prefix2=prefix.lstrip('0')
    
    #无后缀
    if not result:
        _,ticker_stooq=cvt_stooq_symbol(prefix2)
        
    #有后缀
    if result:
        _,prefix3=cvt_stooq_symbol(prefix2)
        ticker_stooq=prefix3+'.'+cvt_stooq_suffix(suffix)
        
    return ticker_stooq    

if __name__=='__main__':
    cvt_stooq_ticker('^GSPC')   
    cvt_stooq_ticker('000001.SS') 
    cvt_stooq_ticker('0700.HK') 
    
    #有问题
    cvt_stooq_ticker('002504.SZ')
#==================================================================================

if __name__=='__main__':
    ticker='^HSI'
    ticker='^GSPC'
    ticker='^DJI'
    ticker='000001.SS'
    ticker='00700.HK'
    ticker='IBM'
    start='2020-1-1'
    end='2021-12-21'    

def get_price_stooq(ticker,start,end):
    """
    抓取股价
    """
    #转换证券代码
    ticker2=cvt_stooq_ticker(ticker)
    
    #从stooq抓取每日价格
    import pandas_datareader.data as web
    try:
        prices=web.DataReader(ticker2,'stooq',start=start,end=end)
    except:
        print("  #Warning(get_price_stooq): inaccessible from stooq for",ticker)
        return None
    
    #添加附注
    if not (prices is None):
        prices.sort_index(axis=0, ascending=True, inplace=True)
        prices.dropna(inplace=True)
        
        prices['Adj Close']=prices['Close']
        prices['source']='stooq'
        prices['ticker']=str(ticker)
        prices['footnote']=''
        
        _,start1,end1=check_period(start,end)
        prices2=prices[(prices.index >= start1) & (prices.index <= end1)]
        num=len(prices2)
        if num > 0:
            print("  Successfully retrieved",num,"records for",ticker)
            return prices2
        else:
            print("  #Warning(get_price_stooq): no records found for",ticker,"from",start,'to',end)
            return None      
    
if __name__=='__main__':
    get_price_stooq('AAPL','2021-11-1','2021-11-5')    
    get_price_stooq('BMW.DE','2021-11-1','2021-11-5')
    hsi=get_price_stooq('^HSI','2021-11-1','2021-11-5')
    get_price_stooq('0700.HK','2021-11-1','2021-11-5')
    get_price_stooq('^N225','2021-11-1','2021-11-5')
    get_price_stooq('^DJI','2021-11-1','2021-11-5')    

#==============================================================================
if __name__=='__main__':
    ticker='600340.SS'
    fromdate='2020-12-1'
    todate='2021-1-31'
    adjust='none'
    
    ticker='000338.SZ'

#在common中定义
#SUFFIX_LIST_CN=['SS','SZ','BJ','NQ']


def get_price_ak(ticker,fromdate,todate,adjust='none'):
    """
    功能：基于akshare抓取A股、港股和美股单只股价
    若抓取A股，调用get_price_ak_cn
    若抓取港股，调用get_price_ak_hk
    若抓取美股，调用get_price_ak_us
    """
    #提取交易所后缀
    ticker1=ticker.upper()
    result,prefix,suffix=split_prefix_suffix(ticker1)
    
    # A股
    if suffix in SUFFIX_LIST_CN:
        #抓取东方财富，处理股指有时出错
        #df=get_price_ak_em(ticker,fromdate,todate,adjust=adjust)
        df=get_price_ak_cn(ticker,fromdate,todate,adjust=adjust)
        if not (df is None): return df
        
        #抓取新浪A股，能处理股指
        df=get_price_ak_cn(ticker,fromdate,todate,adjust=adjust)
        return df

    if adjust=='none':
        adjust=''
    #抓取新浪港股，不能处理股指
    if suffix in ['HK']:
        df=get_price_ak_hk(ticker,fromdate,todate,adjust=adjust)
        return df    
    # 美股，不能处理股指
    df=get_price_ak_us(ticker,fromdate,todate,adjust=adjust)
    
    return df 

def get_price_ak_cn(ticker,fromdate,todate,adjust='none'):
    """
    功能：从akshare获得中国国内的股票和指数历史行情，只能处理单个股票或指数
    ticker：雅虎格式，沪市股票为.SS，深市为.SZ，其他的不处理，直接返回None
    fromdate：格式为YYYY-m-d，需要改造为YYYYMMDD
    todate：格式为YYYY-m-d，需要改造为YYYYMMDD
    adjust：不考虑复权为'none'，后复权为'hfq'，前复权为'qfq'
    返回结果：雅虎格式，日期升序，列明首字母大写等
    """
    #变换代码格式
    ticker1=ticker.upper()
    last3=ticker1[-3:]
    headcode=ticker1[:-3]
    if last3 == '.SS':
        ticker2='sh'+headcode
    if last3 == '.SZ':
        ticker2='sz'+headcode
    if last3 not in ['.SS','.SZ']:
        print("  #Warning(get_price_ak_cn): not eligible for security",ticker)
        return None

    #变换日期格式
    result,start,end=check_period(fromdate,todate)
    if not result:
        print("  #Warning(get_price_ak_cn): invalid date period from",fromdate,'to',todate)
        return None   
    start1=start.strftime('%Y%m%d')
    end1=end.strftime('%Y%m%d')
    
    adjustlist=['none','hfq','qfq']
    if adjust not in adjustlist:
        print("  #Warning(get_price_ak_cn): adjust only supports",adjustlist)
        return None          

    import akshare as ak
    import pandas as pd
    import datetime as dt
    df=None
    #printmsg=str(ticker)+" from "+fromdate+" to "+todate
    #不考虑复权情形
    if adjust == 'none':
        try:
            #抓取指数行情，实际上亦可抓取股票行情
            df = ak.stock_zh_index_daily(symbol=ticker2)  
            df['Date']=df.index
            df['Date']=df['Date'].dt.tz_localize(None)
        except:
            try:
                #股票的历史行情数据（不考虑复权，特殊函数）
                df=ak.stock_zh_a_cdr_daily(ticker2,start1,end1)
                df['Date']=pd.to_datetime(df['date'])
            except:
                print("  #Error(get_price_ak_cn): failed to find prices for",ticker)
                return None
        
    #考虑复权情形
    if adjust != 'none':
        try:
            #股票的历史行情数据（考虑复权）
            df=ak.stock_zh_a_daily(ticker2,start1,end1,adjust=adjust)
            df['Date']=df['date']
        except:
            print("  #Error(get_price_ak_cn): failed to find prices for",ticker)
            return None
    
    if df is None:
        return None
    else:
        #设置新的索引
        df.set_index(['Date'],inplace=True)
        df.rename(columns={'open':'Open','high':'High','low':'Low','close':'Close','volume':'Volume'},inplace=True)
        df['Adj Close']=df['Close']

    df1=df[df.index >= start]
    df2=df1[df1.index <= end]
    
    if df2 is None:
        print("  #Error(get_price_ak_cn): failed to find prices for",ticker)
        return None
    num=len(df2)
    if num==0:
        print("  #Error(get_price_ak_cn): found zero record for",ticker)
        return None
    
    df2['source']='新浪'
    df2['ticker']=str(ticker)
    df2['Adj Close']=df2['Close']
    df2['footnote']=adjust    
    print("  Successfully retrieved",num,"records for",ticker)
    
    return df2

if __name__=='__main__':
    dfx=get_price_ak_cn('600519.SS','2020-12-1','2020-12-5',adjust='none')
    dfy=get_price_ak_cn('600519.SS','2020-12-1','2021-2-5',adjust='hfq')
    df399001=get_price_ak_cn('399001.SZ','2020-12-1','2021-2-5')
    df000688=get_price_ak('000688.SS','2020-12-1','2021-2-5')
    dfz=get_price_ak_cn('AAPL','2020-12-1','2021-2-5')

#==============================================================================
if __name__=='__main__':
    symbol='AAPL'
    fromdate='2020-12-1'
    todate='2021-1-31'
    adjust=""

def get_price_ak_us(symbol, fromdate, todate, adjust=""):
    """
    抓取单个美股股价，不能处理股指
    """
    
    #检查日期期间
    result,start,end=check_period(fromdate,todate)
    if not result:
        print("  #Warning(get_price_ak_us): invalid date period from",fromdate,'to',todate)
        return None  
    
    symbol=symbol.upper()
    #printmsg=str(symbol)+" from "+fromdate+" to "+todate    

    import akshare as ak
    print("  Searching info in Sina for",symbol,"... ...")
    try:
        df=ak.stock_us_daily(symbol=symbol, adjust=adjust)
    except:
        print("  #Error(get_price_ak_us): no info found for",symbol)
        return None
    
    df['Date']=df.index
    #去掉可能出现的时区信息，必须使用datetime中的tz_localize
    import datetime as dt
    df['Date']=df['Date'].dt.tz_localize(None)
    #设置新的索引
    df.set_index(['Date'],inplace=True)    
    
    #选取时间范围
    df1=df[df.index >=start]    
    df2=df1[df1.index <=end] 
    if df2 is None:
        print("  #Error(get_price_ak_us): failed to find prices for",symbol)
        return None    
    num=len(df2)
    if num==0:
        print("  #Error(get_price_ak_us): found zero record for",symbol)
        return None 
    
    df2.rename(columns={'open':'Open','high':'High','low':'Low','close':'Close','volume':'Volume'},inplace=True)
    df2['ticker']=symbol
    df2['Adj Close']=df2['Close']
    df2['source']='新浪'
    df2['footnote']=adjust    
    print("  Successfully retrieved",num,"records for",symbol)    
    
    return df2

if __name__=='__main__':
    get_price_ak_us('AAPL', '2021-11-1', '2021-11-5')
    get_price_ak_us('^DJI', '2021-11-1', '2021-11-5')
#==============================================================================
if __name__=='__main__':
    symbol='0700.HK'
    symbol='0700.hk'
    symbol='00700.HK'
    fromdate='2020-12-1'
    todate='2021-1-31'

def get_price_ak_hk(symbol, fromdate, todate, adjust=""):
    """
    抓取单个港股股价，不能处理股指
    """
    
    #检查日期期间
    result,start,end=check_period(fromdate,todate)
    if not result:
        print("  #Warning(get_price_ak_hk): invalid date period from",fromdate,'to',todate)
        return None  
    
    #printmsg=str(symbol)+" from "+fromdate+" to "+todate  

    import akshare as ak
    print("  Searching info in Sina for",symbol,"... ...")
    symbol1=symbol.upper()
    symbol2 = symbol1.strip('.HK')
    if len(symbol2)==4:
        symbol3='0'+symbol2
    else:
        symbol3=symbol2
    
    try:
        df=ak.stock_hk_daily(symbol=symbol3, adjust="")
    except:
        print("  #Error(get_price_ak_hk): no info found for",symbol)
        return None
    
    df['Date']=df.index
    #去掉可能出现的时区信息，必须使用datetime中的tz_localize
    import datetime as dt
    try:
        df['Date']=df['Date'].dt.tz_localize(None)
    except:
        import pandas as pd
        df['Date']=pd.to_datetime(df['date'])
    #设置新的索引
    df.set_index(['Date'],inplace=True)  
    
    #选取时间范围
    df1=df[df.index >=start]    
    df2=df1[df1.index <=end] 
    if df2 is None:
        print("  #Error(get_price_ak_hk): failed to find prices for",symbol)
        return None
    num=len(df2)
    if num==0:
        print("  #Error(get_price_ak_hk): found zero record for",ticker)
        return None
    
    df2.rename(columns={'open':'Open','high':'High','low':'Low','close':'Close','volume':'Volume'},inplace=True)
    df2['ticker']=symbol
    df2['Adj Close']=df2['Close']
    df2['source']='新浪'
    print("  Successfully retrieved",num,"records for",symbol)
    
    return df2

if __name__=='__main__':
    df=get_price_ak_hk('0700.hk', '2021-11-1', '2021-11-5')
    df=get_price_ak_hk('0700.HK', '2021-11-1', '2021-11-5')
    df=get_price_ak_hk('00700.hk', '2021-11-1', '2021-11-5')
#==============================================================================
if __name__=='__main__':
    ticker=['600519.SS','000858.SZ']
    fromdate='2020-12-1'
    todate='2021-1-31'
    adjust='none'    

def get_prices_ak(ticker,fromdate,todate,adjust='none'):
    """
    功能：获取中国国内股票或指数的历史行情，多个股票
    """
    #检查是否为多个股票:单个股票代码
    if isinstance(ticker,str):
        df=get_price_ak(ticker,fromdate,todate,adjust=adjust)
        return df
    
    #检查是否为多个股票:空的列表
    if isinstance(ticker,list) and len(ticker) == 0:
        pass
        return None        
    
    #检查是否为多个股票:列表中只有一个代码
    if isinstance(ticker,list) and len(ticker) == 1:
        ticker1=ticker[0]
        df=get_price_ak(ticker1,fromdate,todate,adjust=adjust)
        return df       
    
    """
    #检查是否均为中国国内的股票或指数
    cncode=True
    for t in ticker:
        last3=t[-3:]
        if last3 not in ['.SS','.SZ']:
            cncode=False
            return None
    """
    import pandas as pd
    #处理列表中的第一个股票
    i=0
    df=None
    while df is None:
        t=ticker[i]
        df=get_price_ak(t,fromdate,todate,adjust=adjust)
        if not (df is None):
            columns=create_tuple_for_columns(df,t)
            df.columns=pd.MultiIndex.from_tuples(columns)
        else:
            i=i+1
    if (i+1) == len(ticker):
        #已经到达股票代码列表末尾
        return df
        
    #处理列表中的其余股票
    for t in ticker[(i+1):]:
        dft=get_price_ak(t,fromdate,todate,adjust=adjust)
        if not (dft is None):
            columns=create_tuple_for_columns(dft,t)
            dft.columns=pd.MultiIndex.from_tuples(columns)
        
        df=pd.merge(df,dft,how='inner',left_index=True,right_index=True)
     
    return df

if __name__=='__main__':
    dfm=get_prices_ak(['600519.SS','000858.SZ'],'2020-12-1','2021-1-31')
    dfm2=get_prices_ak(['600519.SS','AAPL'],'2020-12-1','2021-1-31')

#==============================================================================
if __name__=='__main__':
    ticker='AAPL'
    start='2020-12-1'
    end='2021-1-31'
    retry_count=3
    pause=1
    
    ticker='^RUT'
    
    ticker=['AAPL','MSFT']
    ticker=['AAPL','MSFT','ABCD']

def get_prices_yahoo(ticker,start,end,retry_count=3,pause=1):
    """
    功能：抓取股价，使用pandas_datareader
    输出：指定收盘价格序列，最新日期的股价排列在前
    ticker: 股票代码。大陆股票代码加上后缀.SZ或.SS，港股代码去掉前导0加后缀.HK
    start: 样本开始日期，尽量远的日期，以便取得足够多的原始样本，yyyy-mm-dd
    end: 样本结束日期，既可以是今天日期，也可以是一个历史日期
    retry_count：网络失败时的重试次数
    pause：每次重试前的间隔秒数
    """
    
    #抓取新浪/stooq股票价格
    from pandas_datareader import data as pdr
    
    """
    #临时修正新浪/stooq网站问题: 2021-7-14
    #yfinance极易出现线程失败，不再覆盖pdr，2021-10-24
    import yfinance as yfin
    yfin.pdr_override()
    """
    try:
        #p=data.DataReader(ticker,'yahoo',start,end,retry_count=retry_count,pause=pause)
        p=pdr.get_data_yahoo(ticker,start=start,end=end)
    except:
        print("  #Error(get_prices_yahoo): data source unreachable, try later")
        return None    
    
    cols=list(p)
    if 'Adj Close' not in cols:
        p['Adj Close']=p['Close']

    p['ticker']=ticker
    #p['Adj Close']=p['Close']
    p['source']='雅虎'
    print("  Successfully retrieved",len(p),"records for",ticker)
        
    return p

if __name__=='__main__':
    df1=get_prices_yahoo('AAPL','2020-12-1','2021-1-31')
    df2=get_prices_yahoo('ABCD','2020-12-1','2021-1-31')
    df3=get_prices_yahoo(['AAPL','MSFT'],'2020-12-1','2021-1-31')
    df4=get_prices_yahoo(['AAPL','EFGH','MSFT','ABCD'],'2020-12-1','2021-1-31')
    df5=get_prices_yahoo(['0700.HK','600519.SS'],'2020-12-1','2021-1-31')
    df6=get_prices_yahoo(['AAPL','MSFT','0700.HK','600519.SS'],'2020-12-1','2021-1-31')

#==============================================================================
def get_price_yf(ticker,start,end,threads=False):
    """
    套壳函数get_prices_yf，保持兼容
    """
    df=get_prices_yf(ticker,start,end,threads=threads)
    
    df['ticker']=ticker
    df['Adj Close']=df['Close']
    df['source']='雅虎'
    print("  Successfully retrieved",len(df),"records for",ticker)    
    
    return df


if __name__=='__main__':
    start='2020-12-1'
    end='2021-1-31'
    
    ticker='AAPL'
    ticker=['AAPL','MSFT']
    ticker=['0700.HK','600519.SS']
    ticker=['AAPL','MSFT','0700.HK','600519.SS']
    
    threads=False


def get_prices_yf(ticker,start,end,threads=False):
    """
    功能：从新浪/stooq抓取股价，使用yfinance(对非美股抓取速度快，但有时不太稳定)
    输入：股票代码或股票代码列表，开始日期，结束日期
    ticker: 股票代码或股票代码列表。大陆股票代码加上后缀.SZ或.SS，港股代码去掉前导0加后缀.HK
    start: 样本开始日期，尽量远的日期，以便取得足够多的原始样本，yyyy-mm-dd
    end: 样本结束日期，既可以是今天日期，也可以是一个历史日期
    
    输出：指定收盘价格序列，最新日期的股价排列在前
    特别注意：yfinance中的收盘价Close其实是Yahoo Finance中的调整收盘价Adj Close。
    """
   
    #抓取新浪/stooq股票价格
    import yfinance as yf
    ticker1,islist=cvt_yftickerlist(ticker)
    if not islist:
        #下载单一股票的股价
        stock=yf.Ticker(ticker1)
        try:
            p=stock.history(start=start,end=end,threads=threads)
            #p=stock.history(start=start,end=end)
        except Exception as e:
            emsg=str(e)
            #print(emsg)
        
            #检查是否网络超时出错
            key1='WSAETIMEDOUT'
            if emsg.find(key1) != -1:
                print("  #Error(get_prices_yf): data source unreachable, try later")
                return None
        
            #单个代码：是否未找到
            key2='Date'
            if emsg.find(key2):
                #单个ticker，未找到代码
                print("  #Error(get_prices_yf): ticker info inaccessible now for",ticker)  
                return None            
    else: 
        #下载股票列表的股价
        try:
            p=yf.download(ticker1,start=start,end=end,progress=False,threads=threads)
        except Exception as e:
            #检查是否网络超时出错
            key1='WSAETIMEDOUT'
            if emsg.find(key1) != -1:
                print("  #Error(get_prices_yf): data source unreachable, try later")
                return None

    cols=list(p)
    if 'Adj Close' not in cols:
        p['Adj Close']=p['Close']  

    p['ticker']=ticker
    p['Adj Close']=p['Close']
    p['source']='雅虎'
    print("  Successfully retrieved",len(p),"records for",ticker)    

    return p

if __name__=='__main__':
    df1=get_prices_yf('AAPL','2020-12-1','2021-1-31')
    df1b=get_prices_yf('EFGH','2020-12-1','2021-1-31')
    df2=get_prices_yf(['AAPL'],'2020-12-1','2021-1-31')
    df3=get_prices_yf(['AAPL','MSFT'],'2020-12-1','2021-1-31')
    df3b=get_prices_yf(['AAPL','MSFS'],'2020-12-1','2021-1-31')
    df4=get_prices_yf(['0700.HK','600519.SS'],'2020-12-1','2021-1-31')
    df5=get_prices_yf(['AAPL','MSFT','0700.HK','600519.SS'],'2020-12-1','2021-1-31')
    df6=get_prices_yf(['ABCD','EFGH','0700.HK','600519.SS'],'2020-12-1','2021-1-31')
    
#==============================================================================
if __name__=='__main__':
    ticker='^GSPC'
    start='1991-1-1'
    end='2000-12-31'

def get_index_fred(ticker,start,end):
    """
    功能：临时解决方案，获取标普500、道琼斯等国外市场指数
    """
    yahoolist=['^GSPC','^DJI','^VIX','^IXIC','^N225','^NDX']
    fredlist=['sp500','djia','vixcls','nasdaqcom','nikkei225','nasdaq100']
    
    if not (ticker in yahoolist):
        return None
    
    import pandas as pd
    import pandas_datareader.data as web
    if ticker in yahoolist:
        pos=yahoolist.index(ticker)
        id=fredlist[pos]
        
        try:
            df = web.DataReader([id], 'fred', start, end)
        except:
            print("  #Warning(get_index_fred): connection failed, trying to recover ...")
            import time
            time.sleep(5) # 暂停 5秒
            try:
                df = web.DataReader([id], 'fred', start, end)
            except:
                pass
                return None
        if len(df)==0:
            return None
        df.rename(columns={id:'Close'},inplace=True)
    
    #删除空值记录
    df.dropna(inplace=True)
    
    df['ticker']=ticker
    df['Adj Close']=df['Close']
    df['source']='FRED'
    print("  Successfully retrieved",len(df),"records for",ticker)    
    
    return df

if __name__=='__main__':
    df1=get_index_fred('^VIX','1991-1-1','1991-12-31')    
    df2=get_index_fred('^DJI','1991-1-1','2020-12-31')  #始于2011-11-25
    df3=get_index_fred('^GSPC','1991-1-1','2020-12-31')  #始于2011-11-25
    df4=get_index_fred('^IXIC','1991-1-1','2020-12-31')
    df5=get_index_fred('^N225','1991-1-1','2020-12-31')
    df6=get_index_fred('^NDX','1991-1-1','2020-12-31')
#==============================================================================  
def create_tuple_for_columns(df_a, multi_level_col):
    """
    Create a columns tuple that can be pandas MultiIndex to create multi level column

    :param df_a: pandas dataframe containing the columns that must form the first level of the multi index
    :param multi_level_col: name of second level column
    :return: tuple containing (first_level_cols,second_level_col)
    """
    temp_columns = []
    for item in df_a.columns:
        temp_columns.append((item, multi_level_col))
    
    return temp_columns    
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
def get_price_portfolio(tickerlist,sharelist,fromdate,todate,adj=False):
    """
    套壳函数get_prices_portfolio
    """
    df=get_prices_portfolio(tickerlist,sharelist,fromdate,todate,adj=adj)
    return df

if __name__=='__main__':
    tickerlist=['INTC','MSFT']
    sharelist=[0.6,0.4]
    fromdate='2020-11-1'
    todate='2021-1-31'

def get_prices_portfolio(tickerlist,sharelist,fromdate,todate,adj=False):
    """
    功能：抓取投资组合的每日价值
    输入：股票代码列表，份额列表，开始日期，结束日期
    tickerlist: 股票代码列表
    sharelist：持有份额列表，与股票代码列表一一对应
    fromdate: 样本开始日期。格式：'YYYY-MM-DD'
    todate: 样本结束日期。既可以是今天日期，也可以是一个历史日期    
    
    输出：投资组合的价格序列，按照日期升序排列
    """
    
    #检查股票列表个数与份额列表个数是否一致
    if len(tickerlist) != len(sharelist):
        print("  Error(get_prices_portfolio): numbers of stocks and shares mismatch.")
        return None        
    
    #抓取股票价格
    p=get_prices(tickerlist,fromdate,todate,adj=adj)
    if p is None: return None
    
    #结果非空时，检查整列为空的证券代码
    nancollist=[] 
    collist=list(p)
    for c in collist:
        if p[c].isnull().all():
            nancollist=nancollist+[c]
    #查找错误的ticker
    wrongtickers=[]
    for w in tickerlist:
        nancolstr=str(nancollist)
        if nancolstr.find(w.upper()) != -1:    #找到
            wrongtickers=wrongtickers+[w]
        
    if len(wrongtickers) > 0:
        print("  #Warning(get_prices_portfolio): price info not found for",wrongtickers)
        print("  #Warning(get_prices_portfolio): dropping all the rows related to",wrongtickers)
        p.dropna(axis=1,how="all",inplace=True)   # 丢弃全为缺失值的那些列
        
        #删除投资组合中相关的权重
        for w in wrongtickers:
            pos=tickerlist.index(w)
            del sharelist[pos]

    if len(sharelist) > 1:    
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
    else:
        prices=p
    
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

if __name__=='__main__':
    tickerlist=['INTC','MSFT']
    sharelist=[0.6,0.4]
    fromdate='2020-11-1'
    todate='2021-1-31'
    dfp=get_prices_portfolio(tickerlist,sharelist,fromdate,todate)

#==============================================================================
#==============================================================================
if __name__=='__main__':
    ticker='AAPL'

    ticker=['AAPL','MSFT','0700.HK','600519.SS']

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
        yftickerlist=yftickerlist+' '+t.upper()
    
    return yftickerlist,True


if __name__=='__main__':
    cvt_yftickerlist('AAPL')
    cvt_yftickerlist(['AAPL'])
    cvt_yftickerlist(['AAPL','MSFT'])
    cvt_yftickerlist(['AAPL','MSFT','0700.hk'])
    
#==============================================================================
if __name__=='__main__':
    url='https://finance.yahoo.com'

def test_website(url='https://finance.yahoo.com'):
    """
    功能：测试网站的联通性和反应时间
    优点：真实
    缺点：运行过程非常慢
    """
    print("  Testing internet connection to",url,"...")
    import pycurl
    from io import BytesIO

    #进行网络测试
    c = pycurl.Curl()
    buffer = BytesIO()  # 创建缓存对象
    c.setopt(c.WRITEDATA, buffer)  # 设置资源数据写入到缓存对象
    c.setopt(c.URL, url)  # 指定请求的URL
    c.setopt(c.MAXREDIRS, 3)  # 指定HTTP重定向的最大数
    
    test_result=True
    test_msg=""
    try:
        c.perform()  # 测试目标网站
    except Exception as e:
        c.close()
        
        #print(e)
        print("  #Error(test_website2):",e)
              
        test_result=False
        test_msg="UNREACHABLE"        
        
        return test_result,test_msg
        
    #获得网络测试结果阐述
    http_code = c.getinfo(pycurl.HTTP_CODE)  # 返回的HTTP状态码
    dns_resolve = c.getinfo(pycurl.NAMELOOKUP_TIME)  # DNS解析所消耗的时间
    http_conn_time = c.getinfo(pycurl.CONNECT_TIME)  # 建立连接所消耗的时间
    http_pre_trans = c.getinfo(pycurl.PRETRANSFER_TIME)  # 从建立连接到准备传输所消耗的时间
    http_start_trans = c.getinfo(pycurl.STARTTRANSFER_TIME)  # 从建立连接到传输开始消耗的时间
    http_total_time = c.getinfo(pycurl.TOTAL_TIME)  # 传输结束所消耗的总时间
    http_size_download = c.getinfo(pycurl.SIZE_DOWNLOAD)  # 下载数据包大小
    http_size_upload = c.getinfo(pycurl.SIZE_UPLOAD)  # 上传数据包大小
    http_header_size = c.getinfo(pycurl.HEADER_SIZE)  # HTTP头部大小
    http_speed_downlaod = c.getinfo(pycurl.SPEED_DOWNLOAD)  # 平均下载速度
    http_speed_upload = c.getinfo(pycurl.SPEED_UPLOAD)  # 平均上传速度
    http_redirect_time = c.getinfo(pycurl.REDIRECT_TIME)  # 重定向所消耗的时间
    
    """
    print('HTTP响应状态： %d' % http_code)
    print('DNS解析时间：%.2f ms' % (dns_resolve * 1000))
    print('建立连接时间： %.2f ms' % (http_conn_time * 1000))
    print('准备传输时间： %.2f ms' % (http_pre_trans * 1000))
    print("传输开始时间： %.2f ms" % (http_start_trans * 1000))
    print("传输结束时间： %.2f ms" % (http_total_time * 1000))
    print("重定向时间： %.2f ms" % (http_redirect_time * 1000))
    print("上传数据包大小： %d bytes/s" % http_size_upload)
    print("下载数据包大小： %d bytes/s" % http_size_download)
    print("HTTP头大小： %d bytes/s" % http_header_size)
    print("平均上传速度： %d k/s" % (http_speed_upload / 1024))
    print("平均下载速度： %d k/s" % (http_speed_downlaod / 1024))
    """
    c.close()
    
    if http_speed_downlaod >= 100*1024: test_msg="FAST"
    if http_speed_downlaod < 100*1024: test_msg="GOOD"
    if http_speed_downlaod < 50*1024: test_msg="GOOD"
    if http_speed_downlaod < 10*1024: test_msg="VERY SLOW"
    if http_speed_downlaod < 1*1024: test_msg="UNSTABLE"
    
    return test_result,test_msg

if __name__=='__main__':
    test_website()
    
#==============================================================================
def calc_daily_return(pricedf):
    """
    功能：基于从新浪/stooq抓取的单个证券价格数据集计算其日收益率
    输入：从新浪/stooq抓取的单个证券价格数据集pricedf，基于收盘价或调整收盘价进行计算
    输出：证券日收益率序列，按照日期升序排列。
    """
    import numpy as np    
    #计算算术日收益率：基于收盘价
    pricedf["Daily Ret"]=pricedf['Close'].pct_change()
    pricedf["Daily Ret%"]=pricedf["Daily Ret"]*100.0
    
    #计算算术日收益率：基于调整收盘价
    pricedf["Daily Adj Ret"]=pricedf['Adj Close'].pct_change()
    pricedf["Daily Adj Ret%"]=pricedf["Daily Adj Ret"]*100.0
    
    #计算对数日收益率
    pricedf["log(Daily Ret)"]=np.log(pricedf["Daily Ret"]+1)
    pricedf["log(Daily Adj Ret)"]=np.log(pricedf["Daily Adj Ret"]+1)
    
    return pricedf 
    

if __name__ =="__main__":
    ticker='AAPL'
    fromdate='2018-1-1'
    todate='2020-3-16'
    pricedf=get_price(ticker, fromdate, todate)
    drdf=calc_daily_return(pricedf)    
    

#==============================================================================
def calc_rolling_return(drdf, period="Weekly"):
    """
    功能：基于单个证券的日收益率数据集, 计算其滚动期间收益率
    输入：
    单个证券的日收益率数据集drdf。
    期间类型period，默认为每周。
    输出：期间滚动收益率序列，按照日期升序排列。
    """
    #检查period类型
    periodlist = ["Weekly","Monthly","Quarterly","Annual"]
    if not (period in periodlist):
        print("*** 错误#1(calc_rolling_return)，仅支持期间类型：",periodlist)
        return None

    #换算期间对应的实际交易天数
    perioddays=[5,21,63,252]
    rollingnum=perioddays[periodlist.index(period)]    
    
    #计算滚动收益率：基于收盘价
    retname1=period+" Ret"
    retname2=period+" Ret%"
    import numpy as np
    drdf[retname1]=np.exp(drdf["log(Daily Ret)"].rolling(rollingnum).sum())-1.0
    drdf[retname2]=drdf[retname1]*100.0
    
    #计算滚动收益率：基于调整收盘价
    retname3=period+" Adj Ret"
    retname4=period+" Adj Ret%"
    drdf[retname3]=np.exp(drdf["log(Daily Adj Ret)"].rolling(rollingnum).sum())-1.0
    drdf[retname4]=drdf[retname3]*100.0
    
    return drdf

if __name__ =="__main__":
    ticker='000002.SZ'
    period="Weekly"
    prdf=calc_rolling_return(drdf, period) 
    prdf=calc_rolling_return(drdf, "Monthly")
    prdf=calc_rolling_return(drdf, "Quarterly")
    prdf=calc_rolling_return(drdf, "Annual")

#==============================================================================
def calc_expanding_return(drdf,basedate):
    """
    功能：基于日收益率数据集，从起始日期开始到结束日期的扩展窗口收益率序列。
    输入：
    日收益率数据集drdf。
    输出：期间累计收益率序列，按照日期升序排列。
    """
    
    #计算累计收益率：基于收盘价
    retname1="Exp Ret"
    retname2="Exp Ret%"
    import numpy as np
    drdf[retname1]=np.exp(drdf[drdf.index >= basedate]["log(Daily Ret)"].expanding(min_periods=1).sum())-1.0
    drdf[retname2]=drdf[retname1]*100.0  
    
    #计算累计收益率：基于调整收盘价
    retname3="Exp Adj Ret"
    retname4="Exp Adj Ret%"
    drdf[retname3]=np.exp(drdf[drdf.index >= basedate]["log(Daily Adj Ret)"].expanding(min_periods=1).sum())-1.0
    drdf[retname4]=drdf[retname3]*100.0  
    
    return drdf

if __name__ =="__main__":
    ticker='000002.SZ'
    basedate="2019-1-1"
    erdf=calc_expanding_return(prdf,basedate)  

#==============================================================================
def rolling_price_volatility(df, period="Weekly"):
    """
    功能：基于单个证券价格的期间调整标准差, 计算其滚动期间价格风险
    输入：
    单个证券的日价格数据集df。
    期间类型period，默认为每周。
    输出：期间滚动价格风险序列，按照日期升序排列。
    """
    #检查period类型
    periodlist = ["Weekly","Monthly","Quarterly","Annual"]
    if not (period in periodlist):
        print("*** 错误#1(calc_rolling_volatility)，仅支持期间类型：",periodlist)
        return None

    #换算期间对应的实际交易天数
    perioddays=[5,21,63,252]
    rollingnum=perioddays[periodlist.index(period)]    
    
    #计算滚动期间的调整标准差价格风险：基于收盘价
    retname1=period+" Price Volatility"
    import numpy as np
    df[retname1]=df["Close"].rolling(rollingnum).apply(lambda x: np.std(x,ddof=1)/np.mean(x)*np.sqrt(len(x)))
    
    #计算滚动期间的调整标准差价格风险：基于调整收盘价
    retname3=period+" Adj Price Volatility"
    df[retname3]=df["Adj Close"].rolling(rollingnum).apply(lambda x: np.std(x,ddof=1)/np.mean(x)*np.sqrt(len(x)))
    
    return df

if __name__ =="__main__":
    period="Weekly"
    df=get_price('000002.SZ','2018-1-1','2020-3-16')
    vdf=rolling_price_volatility(df, period) 

#==============================================================================
def expanding_price_volatility(df,basedate):
    """
    功能：基于日价格数据集，从起始日期开始到结束日期调整价格风险的扩展窗口序列。
    输入：
    日价格数据集df。
    输出：期间扩展调整价格风险序列，按照日期升序排列。
    """
    
    #计算扩展窗口调整价格风险：基于收盘价
    retname1="Exp Price Volatility"
    import numpy as np
    df[retname1]=df[df.index >= basedate]["Close"].expanding(min_periods=1).apply(lambda x: np.std(x,ddof=1)/np.mean(x)*np.sqrt(len(x)))
    
    #计算扩展窗口调整价格风险：基于调整收盘价
    retname3="Exp Adj Price Volatility"
    df[retname3]=df[df.index >= basedate]["Adj Close"].expanding(min_periods=1).apply(lambda x: np.std(x,ddof=1)/np.mean(x)*np.sqrt(len(x)))
    
    return df

if __name__ =="__main__":
    df=get_price('000002.SZ','2018-1-1','2020-3-16')    
    evdf=expanding_price_volatility(df)  


#==============================================================================
def rolling_ret_volatility(df, period="Weekly"):
    """
    功能：基于单个证券的期间收益率, 计算其滚动收益率波动风险
    输入：
    单个证券的期间收益率数据集df。
    期间类型period，默认为每周。
    输出：滚动收益率波动风险序列，按照日期升序排列。
    """
    #检查period类型
    periodlist = ["Weekly","Monthly","Quarterly","Annual"]
    if not (period in periodlist):
        print("*** 错误#1(rolling_ret_volatility)，仅支持期间类型：",periodlist)
        return None

    #换算期间对应的实际交易天数
    perioddays=[5,21,63,252]
    rollingnum=perioddays[periodlist.index(period)]    
    
    #计算滚动标准差：基于普通收益率
    periodret=period+" Ret"
    retname1=period+" Ret Volatility"
    retname2=retname1+'%'
    import numpy as np
    df[retname1]=df[periodret].rolling(rollingnum).apply(lambda x: np.std(x,ddof=1))
    df[retname2]=df[retname1]*100.0
    
    #计算滚动标准差：基于调整收益率
    periodadjret=period+" Adj Ret"
    retname3=period+" Adj Ret Volatility"
    retname4=retname3+'%'
    df[retname3]=df[periodadjret].rolling(rollingnum).apply(lambda x: np.std(x,ddof=1))
    df[retname4]=df[retname3]*100.0
    
    return df

if __name__ =="__main__":
    period="Weekly"
    pricedf=get_price('000002.SZ','2018-1-1','2020-3-16')
    retdf=calc_daily_return(pricedf)
    vdf=rolling_ret_volatility(retdf, period) 

#==============================================================================
def expanding_ret_volatility(df,basedate):
    """
    功能：基于日收益率数据集，从起始日期basedate开始的收益率波动风险扩展窗口序列。
    输入：
    日收益率数据集df。
    输出：扩展调整收益率波动风险序列，按照日期升序排列。
    """
    
    #计算扩展窗口调整收益率波动风险：基于普通收益率
    retname1="Exp Ret Volatility"
    retname2="Exp Ret Volatility%"
    import numpy as np
    df[retname1]=df[df.index >= basedate]["Daily Ret"].expanding(min_periods=1).apply(lambda x: np.std(x,ddof=1)*np.sqrt(len(x)))
    df[retname2]=df[retname1]*100.0
    
    #计算扩展窗口调整收益率风险：基于调整收益率
    retname3="Exp Adj Ret Volatility"
    retname4="Exp Adj Ret Volatility%"
    df[retname3]=df[df.index >= basedate]["Daily Adj Ret"].expanding(min_periods=1).apply(lambda x: np.std(x,ddof=1)*np.sqrt(len(x)))
    df[retname4]=df[retname3]*100.0
    
    return df

if __name__ =="__main__":
    basedate='2019-1-1'
    pricedf=get_price('000002.SZ','2018-1-1','2020-3-16')    
    retdf=calc_daily_return(pricedf)
    evdf=expanding_ret_volatility(retdf,'2019-1-1')  

#==============================================================================
def lpsd(ds):
    """
    功能：基于给定数据序列计算其下偏标准差。
    输入：
    数据序列ds。
    输出：序列的下偏标准差。
    """
    import numpy as np
    #若序列长度为0则直接返回数值型空值
    if len(ds) == 0: return np.NaN
    
    #求均值
    import numpy as np
    miu=np.mean(ds)
    
    #计算根号内的下偏平方和
    sum=0; ctr=0
    for s in list(ds):
        if s < miu:
            sum=sum+pow((s-miu),2)
            ctr=ctr+1
    
    #下偏标准差
    if ctr > 1:
        result=np.sqrt(sum/(ctr-1))
    elif ctr == 1: result=np.NaN
    else: result=np.NaN
        
    return result
    
if __name__ =="__main__":
    df=get_price("000002.SZ","2020-1-1","2020-3-16")
    print(lpsd(df['Close']))

#==============================================================================
def rolling_ret_lpsd(df, period="Weekly"):
    """
    功能：基于单个证券期间收益率, 计算其滚动收益率损失风险。
    输入：
    单个证券的期间收益率数据集df。
    期间类型period，默认为每周。
    输出：滚动收益率的下偏标准差序列，按照日期升序排列。
    """
    #检查period类型
    periodlist = ["Weekly","Monthly","Quarterly","Annual"]
    if not (period in periodlist):
        print("*** 错误#1(rolling_ret_lpsd)，仅支持期间类型：",periodlist)
        return None

    #换算期间对应的实际交易天数
    perioddays=[5,21,63,252]
    rollingnum=perioddays[periodlist.index(period)]    
    
    #计算滚动下偏标准差：基于普通收益率
    periodret=period+" Ret"
    retname1=period+" Ret LPSD"
    retname2=retname1+'%'
    #import numpy as np
    df[retname1]=df[periodret].rolling(rollingnum).apply(lambda x: lpsd(x))
    df[retname2]=df[retname1]*100.0
    
    #计算滚动下偏标准差：基于调整收益率
    periodadjret=period+" Adj Ret"
    retname3=period+" Adj Ret LPSD"
    retname4=retname3+'%'
    df[retname3]=df[periodadjret].rolling(rollingnum).apply(lambda x: lpsd(x))
    df[retname4]=df[retname3]*100.0
    
    return df

if __name__ =="__main__":
    period="Weekly"
    pricedf=get_price('000002.SZ','2018-1-1','2020-3-16')
    retdf=calc_daily_return(pricedf)
    vdf=rolling_ret_lpsd(retdf, period) 

#==============================================================================
def expanding_ret_lpsd(df,basedate):
    """
    功能：基于日收益率数据集，从起始日期basedate开始的收益率损失风险扩展窗口序列。
    输入：
    日收益率数据集df。
    输出：扩展调整收益率波动风险序列，按照日期升序排列。
    """
    
    #计算扩展窗口调整收益率下偏标准差：基于普通收益率
    retname1="Exp Ret LPSD"
    retname2=retname1+'%'
    import numpy as np
    df[retname1]=df[df.index >= basedate]["Daily Ret"].expanding(min_periods=1).apply(lambda x: lpsd(x)*np.sqrt(len(x)))
    df[retname2]=df[retname1]*100.0
    
    #计算扩展窗口调整下偏标准差：基于调整收益率
    retname3="Exp Adj Ret LPSD"
    retname4=retname3+'%'
    df[retname3]=df[df.index >= basedate]["Daily Adj Ret"].expanding(min_periods=1).apply(lambda x: lpsd(x)*np.sqrt(len(x)))
    df[retname4]=df[retname3]*100.0
    
    return df

if __name__ =="__main__":
    basedate='2019-1-1'
    pricedf=get_price('000002.SZ','2018-1-1','2020-3-16')    
    retdf=calc_daily_return(pricedf)
    evdf=expanding_ret_lpsd(retdf,'2019-1-1')  
#==============================================================================
if __name__ =="__main__":
    portfolio={'Market':('US','^GSPC'),'AAPL':1}
    portfolio={'Market':('China','^HSI'),'0823.HK':1.0}
    portfolio={'Market':('China','000001.SS'),'000661.SZ':2,'603392.SS':3,'300601.SZ':4}
    fromdate='2019-7-19'
    todate='2020-7-20'
    adj=False

def get_portfolio_prices(portfolio,fromdate,todate,adj=False):
    """
    功能：抓取投资组合portfolio的每日价值和FF3各个因子
    输入：投资组合portfolio，开始日期，结束日期
    fromdate: 样本开始日期。格式：'YYYY-MM-DD'
    todate: 样本结束日期。既可以是今天日期，也可以是一个历史日期    
    
    输出：投资组合的价格序列，按照日期升序排列
    """
    
    #解构投资组合
    _,mktidx,tickerlist,sharelist=decompose_portfolio(portfolio)
    
    #检查股票列表个数与份额列表个数是否一致
    if len(tickerlist) != len(sharelist):
        print("  #Error(get_portfolio_prices): numbers of stocks and shares mismatch.")
        return None        
    
    #抓取股票价格
    #print("  Searching portfolio prices for",tickerlist,'from',fromdate,'to',todate)
    p=get_prices(tickerlist,fromdate,todate,adj=adj)
    if p is None:
        print("  #Error(get_portfolio_prices): information inaccessible for",tickerlist)
        return None  

    #print("  Retrieved",len(p),'records of portfolio records')
    import pandas as pd
    if len(sharelist) > 0:    
        #计算投资组合的开盘价
        op=pd.DataFrame(p['Open'])
        #计算投资组合的价值
        try:
            oprice=pd.DataFrame(op.dot(sharelist))
        except:
            print("  #Error(get_portfolio_prices): Dot product shape mismatch for open price",tickerlist)
            return None
        oprice.rename(columns={0: 'Open'}, inplace=True)    

        #计算投资组合的收盘价
        cp=pd.DataFrame(p['Close'])
        #计算投资组合的价值
        cprice=pd.DataFrame(cp.dot(sharelist))
        cprice.rename(columns={0: 'Close'}, inplace=True) 
        
        #计算投资组合的调整收盘价
        acp=pd.DataFrame(p['Adj Close'])
        #计算投资组合的价值
        acprice=pd.DataFrame(acp.dot(sharelist))
        acprice.rename(columns={0: 'Adj Close'}, inplace=True) 
    
        #计算投资组合的交易量
        vol=pd.DataFrame(p['Volume'])
        #计算投资组合的价值
        pfvol=pd.DataFrame(vol.dot(sharelist))
        pfvol.rename(columns={0: 'Volume'}, inplace=True) 
    
        #计算投资组合的交易金额
        if len(sharelist) > 1:
            for t in tickerlist:
                p['Amount',t]=p['Close',t]*p['Volume',t]
        elif len(sharelist) == 1:
            p['Amount']=p['Close']*p['Volume']
        amt=pd.DataFrame(p['Amount'])
        
        #计算投资组合的价值
        pfamt=pd.DataFrame(amt.dot(sharelist))
        pfamt.rename(columns={0: 'Amount'}, inplace=True) 

        #合成开盘价、收盘价、调整收盘价、交易量和交易金额
        pf1=pd.merge(oprice,cprice,how='inner',left_index=True,right_index=True)    
        pf2=pd.merge(pf1,acprice,how='inner',left_index=True,right_index=True)
        pf3=pd.merge(pf2,pfvol,how='inner',left_index=True,right_index=True)
        pf4=pd.merge(pf3,pfamt,how='inner',left_index=True,right_index=True)
    """
    else:
        p['Amount']=p['Close']*p['Volume']
        pf4=p
    """
    pf4['Ret%']=pf4['Close'].pct_change()*100.0

    #获得期间的市场收益率：假设无风险收益率非常小，可以忽略
    try:
        m=get_prices(mktidx,fromdate,todate)
    except:
        print("  #Error(get_portfolio_prices): info inaccesible for market index",mktidx)
        return None
    
    m['Mkt-RF']=m['Close'].pct_change()*100.0
    m['RF']=0.0
    rf_df=m[['Mkt-RF','RF']]
    
    #合并pf4与rf_df
    prices=pd.merge(pf4,rf_df,how='left',left_index=True,right_index=True)

    #提取日期和星期几
    prices['Date']=prices.index.strftime("%Y-%m-%d")
    prices['Weekday']=prices.index.weekday+1

    prices['Portfolio']=str(tickerlist)
    prices['Shares']=str(sharelist)
    
    prices['Adjustment']=adj
    try:
        prices['Adjustment']=prices.apply(lambda x: \
          False if x['Close']==x['Adj Close'] else True, axis=1)
    except: pass
    
    pfdf=prices[['Portfolio','Shares','Date','Weekday', \
                 'Open','Close','Adj Close','Adjustment', \
                'Volume','Amount','Ret%','Mkt-RF','RF']]  

    return pfdf      


#==============================================================================
if __name__ =="__main__":
    ticker='AAPL'  

def recent_stock_split(ticker):
    """
    功能：显示股票最近一年的分拆历史
    输入：单一股票代码
    输出：最近一年的分拆历史
    """   
    #获取今日日期
    import datetime
    today = datetime.date.today()
    fromdate = date_adjust(today,-365)
    
    import yfinance as yf
    stock = yf.Ticker(ticker)
    try:
        div=stock.splits
    except:
        print("#Error(recent_stock_split): no split info found for",ticker)
        return None    
    if len(div)==0:
        print("#Warning(recent_stock_split): no split info found for",ticker)
        return None      
    
    #过滤期间
    div2=div[div.index >= fromdate]
    if len(div2)==0:
        print("#Warning(stock_split): no split info from",fromdate,'to',today)
        return None          
    
    #对齐打印
    import pandas as pd    
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    
    divdf=pd.DataFrame(div2)
    divdf['Index Date']=divdf.index
    datefmt=lambda x : x.strftime('%Y-%m-%d')
    divdf['Split Date']= divdf['Index Date'].apply(datefmt)
    
    #增加星期
    from datetime import datetime
    weekdayfmt=lambda x : x.isoweekday()
    divdf['Weekdayiso']= divdf['Index Date'].apply(weekdayfmt)
    wdlist=['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    wdfmt=lambda x : wdlist[x-1]
    divdf['Weekday']= divdf['Weekdayiso'].apply(wdfmt)
    
    #增加序号
    divdf['Seq']=divdf['Split Date'].rank(ascending=1)
    divdf['Seq']=divdf['Seq'].astype('int')
    
    divdf['Splitint']=divdf['Stock Splits'].astype('int')
    splitfmt=lambda x: "1:"+str(x)
    divdf['Splits']=divdf['Splitint'].apply(splitfmt)
    
    divprt=divdf[['Seq','Split Date','Weekday','Splits']]
    
    print("\n=== 近期股票分拆历史 ===")
    print("股票:",ticker,'\b,',ticker)
    print("期间:",fromdate,"to",today)
    divprt.columns=['序号','日期','星期','分拆比例']
    print(divprt.to_string(index=False))   
    
    import datetime
    today = datetime.date.today()
    print("数据来源: 新浪/stooq,",today)
    
    return divdf
    
    
if __name__ =="__main__":
    df=recent_stock_split('AAPL')

#==============================================================================
if __name__ =="__main__":
    ticker='AAPL'

def get_last_close(ticker):
    """
    功能：从新浪/stooq抓取股票股价或指数价格或投资组合价值，使用pandas_datareader
    输入：股票代码或股票代码列表，开始日期，结束日期
    ticker: 股票代码或者股票代码列表。
    大陆股票代码加上后缀.SZ或.SS，港股代码去掉前导0加后缀.HK
    输出：最新的收盘价和日期
    """
    #获取今日日期
    import datetime
    today = datetime.date.today()
    fromdate = date_adjust(today,-30)
    
    #抓取新浪/stooq股票价格
    from pandas_datareader import data
    try:
        price=data.DataReader(ticker,'yahoo',fromdate,today)
    except:
        print("\n  #Error(get_last_close): failed in retrieving prices!")        
        return None,None            
    if price is None:
        print("\n  #Error(get_last_close): retrieved none info!")
        return None,None  
    if len(price)==0:
        print("\n  #Error(get_last_close): retrieved empty info!")
        return None,None         
    price['date']=price.index
    datecvt=lambda x:x.strftime("%Y-%m-%d")
    price['date']=price['date'].apply(datecvt)
    price.sort_values("date",inplace=True)

    #提取最新的日期和收盘价
    lasttradedate=list(price['date'])[-1]
    lasttradeclose=round(list(price['Close'])[-1],2)

    return lasttradedate,lasttradeclose

if __name__ =="__main__":
    get_last_close('AAPL')

#==============================================================================

#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
