# -*- coding: utf-8 -*-
"""
本模块功能：提供全球证券信息，应用层
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2018年6月16日
最新修订日期：2020年8月28日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
作者邮件：wdehong2000@163.com
版权所有：王德宏
用途限制：仅限研究与教学使用，不可商用！商用需要额外授权。
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""
#==============================================================================
#关闭所有警告
import warnings; warnings.filterwarnings('ignore')

from siat.common import *
from siat.translate import *
from siat.grafix import *
from siat.security_prices import *
#==============================================================================
import matplotlib.pyplot as plt
plt.rcParams['figure.figsize']=(12.8,7.2)
plt.rcParams['figure.dpi']=300
plt.rcParams['font.size'] = 13
plt.rcParams['xtick.labelsize']=11 #横轴字体大小
plt.rcParams['ytick.labelsize']=11 #纵轴字体大小

title_txt_size=16
ylabel_txt_size=14
xlabel_txt_size=14
legend_txt_size=14

import mplfinance as mpf

#处理绘图汉字乱码问题
import sys; czxt=sys.platform
if czxt in ['win32','win64']:
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置默认字体
    mpfrc={'font.family': 'SimHei'}

if czxt in ['darwin']: #MacOSX
    plt.rcParams['font.family']= ['Heiti TC']
    mpfrc={'font.family': 'Heiti TC'}

if czxt in ['linux']: #website Jupyter
    plt.rcParams['font.family']= ['Heiti TC']
    mpfrc={'font.family':'Heiti TC'}

# 解决保存图像时'-'显示为方块的问题
plt.rcParams['axes.unicode_minus'] = False 
#==============================================================================
def reset_plt():
    """
    功能：用于使用完mplfinance可能造成的绘图乱码问题，但不能恢复默认绘图尺寸
    """
    import matplotlib.pyplot as plt
    if czxt in ['win32','win64']:
        plt.rcParams['font.sans-serif'] = ['SimHei']
    if czxt in ['darwin']:
        plt.rcParams['font.sans-serif']=['Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False
#==============================================================================
#以下使用新浪/stooq数据源
#==============================================================================

if __name__ =="__main__":
    ticker='AAPL'
    
def get_profile(ticker):
    """
    功能：按照证券代码抓取证券基本信息。
    输入：证券代码ticker。
    返回：证券基本信息，数据框
    注意：经常出现无规律失败，放弃
    """
    #引入插件
    try:
        import yfinance as yf
    except:
        print("#Error(get_profile): lack of python plugin yfinance")
        return None    

    #抓取证券信息，结果为字典
    tp=yf.Ticker(ticker)
    dic=tp.info
    
    #将字典转换为数据框
    import pandas as pd
    df=pd.DataFrame([dic])
        
    #转换特殊列的内容：10位时间戳-->日期
    cols=list(df)
    import time
    if ('exDividendDate' in cols):
        df['exDividendDate']=int10_to_date(df['exDividendDate'][0])
    if ('lastSplitDate' in cols):
        df['lastSplitDate']=int10_to_date(df['lastSplitDate'][0])
    if ('sharesShortPreviousMonthDate' in cols):
        df['sharesShortPreviousMonthDate']=int10_to_date(df['sharesShortPreviousMonthDate'][0])
    if ('dateShortInterest' in cols):
        df['dateShortInterest']=int10_to_date(df['dateShortInterest'][0])
    if ('mostRecentQuarter' in cols):
        df['mostRecentQuarter']=int10_to_date(df['mostRecentQuarter'][0])
    if ('lastFiscalYearEnd' in cols):
        df['lastFiscalYearEnd']=int10_to_date(df['lastFiscalYearEnd'][0])
    if ('nextFiscalYearEnd' in cols):
        df['nextFiscalYearEnd']=int10_to_date(df['nextFiscalYearEnd'][0])
    
    #转换特殊列的内容：可交易标志
    if df['tradeable'][0]: df['tradeable']="Yes"
    else: df['tradeable']="No"
    
    return df

if __name__ =="__main__":
    ticker='AAPL'
    df=get_profile('AAPL')
#==============================================================================
def print_profile_detail(df,option='basic'):
    """
    功能：按照选项显示证券信息，更多细节。
    输入：证券基本信息df；分段选项option。
    输出：按照选项打印证券信息
    返回：证券信息，数据框
    注意：放弃
    """
    #检查数据框的有效性
    if (df is None) or (len(df)==0):
        print("...Error #1(print_profile), data input invalid!")
        return None         

    options=["basic","financial","market"]
    if not(option in options):
        print("...Error #2(print_profile), 仅支持选项: basic, financial, market")
        return None
    
    #遍历数据框，清洗数据
    cols=list(df)   #取得数据框的列名
    import numpy as np
    for c in cols:
        dfc0=df[c][0]
        #删除空值列
        if dfc0 is None:
            del df[c]; continue
        if dfc0 is np.nan:
            del df[c]; continue        
        #删除空表列
        if isinstance(dfc0,list):
            if len(dfc0)==0: del df[c]; continue
        
        #分类型清洗内容
        if isinstance(dfc0,float): df[c]=round(dfc0,4)
        if isinstance(dfc0,str): df[c]=dfc0.strip()
    newcols=list(df)    #取得清洗后数据框的列名
    
    #需要打印的字段，只要抓取到就打印
    basiccols=['symbol','quoteType','shortName','longName','sector','industry', \
            'fullTimeEmployees','address1','city','state','country','zip', \
            'phone','fax','website','currency','exchange','market']    
    financialcols=['symbol','shortName','currency','dividendRate',
            'trailingAnnualDividendRate','exDividendDate', \
            'dividendYield','trailingAnnualDividendYield', \
            'fiveYearAvgDividendYield','payoutRatio', \
            'lastSplitDate','lastSplitFactor','trailingPE','forwardPE', \
            'trailingEps','forwardEps','profitMargins','earningsQuarterlyGrowth', \
            'pegRatio','priceToSalesTrailing12Months','priceToBook', \
            'enterpriseToRevenue','enterpriseToEbitda','netIncomeToCommon','bookValue', \
            'lastFiscalYearEnd', \
            'mostRecentQuarter','nextFiscalYearEnd']     
    marketcols=['symbol','shortName','currency','beta','tradeable','open', \
                'regularMarketOpen','dayHigh','regularMarketDayHigh', \
                'dayLow','regularMarketLow','previousClose', \
                'regularMarketPreviousClose','regularMarketPrice','ask','bid', \
                'fiftyDayAvergae','twoHundredDayAverage','fiftyTwoWeekHigh', \
                'fiftyTwoWeekLow','52WeekChange','SandP52Change','volume', \
                'regularMarketVolume','averageVolume','averageDailyVolume10Day', \
                'averageVolume10days', \
                'sharesShortPriorMonth','sharesShortPreviousMonthDate', \
                'dateShortInterest','sharesPercentSharesOut', \
                'sharesOutstanding','floatShares','heldPercentInstitutions', \
                'heldPercentInsiders','enterpriseValue','marketCap', \
                'sharesShort','shortRatio','shortPercentOfFloat'] 

    typecn=["公司信息","财务信息","市场信息"]
    typeinfo=typecn[options.index(option)]
    print("\n===",texttranslate("证券快照：")+typeinfo,"===")
    typecols=[basiccols,financialcols,marketcols]
    cols=typecols[options.index(option)]
    
    from pandas.api.types import is_numeric_dtype
    for i in cols:
        if i in newcols:
            cn=ectranslate(i)
            if is_numeric_dtype(df[i][0]):      
                if abs(df[i][0]) >= 0.0001:
                    print(cn+':',format(df[i][0],','))  
            else:
                print(cn+':',df[i][0])

    import datetime as dt; today=dt.date.today()    
    print(texttranslate("数据来源：雅虎，")+str(today))
    return df

if __name__ =="__main__":
    option='basic'
    df=print_profile_detail(df, option='basic')
    df=print_profile_detail(df, option='financial')
    df=print_profile_detail(df, option='market')

#==============================================================================
def print_profile(df,option='basic'):
    """
    功能：按照选项显示证券信息，简化版。
    输入：证券基本信息df；分段选项option。
    输出：按照选项打印证券信息
    返回：证券信息，数据框
    注意：放弃
    """
    #检查数据框的有效性
    if (df is None) or (len(df)==0):
        print("  #Error(print_profile), data set input invalid!")
        return None         

    options=["basic","financial","market"]
    if not(option in options):
        print("  #Error(print_profile), only support types of basic, financial, market")
        return None
    
    #遍历数据框，清洗数据
    cols=list(df)   #取得数据框的列名
    import numpy as np
    for c in cols:
        dfc0=df[c][0]
        #删除空值列
        if dfc0 is None:
            del df[c]; continue
        if dfc0 is np.nan:
            del df[c]; continue        
        #删除空表列
        if isinstance(dfc0,list):
            if len(dfc0)==0: del df[c]; continue
        
        #分类型清洗内容
        if isinstance(dfc0,float): df[c]=round(dfc0,4)
        if isinstance(dfc0,str): df[c]=dfc0.strip()
    newcols=list(df)    #取得清洗后数据框的列名
    
    basiccols=['symbol','quoteType','shortName','sector','industry', \
            'fullTimeEmployees','city','state','country', \
            'website','currency','exchange']    
    financialcols=['symbol','dividendRate',
            'dividendYield', \
            'payoutRatio', \
            'trailingPE','forwardPE', \
            'trailingEps','forwardEps','profitMargins','earningsQuarterlyGrowth', \
            'pegRatio','priceToSalesTrailing12Months','priceToBook', \
            'bookValue', \
            'lastFiscalYearEnd']     
    marketcols=['symbol','beta','open', \
                'dayHigh', \
                'dayLow','previousClose', \
                'fiftyTwoWeekHigh', \
                'fiftyTwoWeekLow','52WeekChange','SandP52Change','volume', \
                'averageDailyVolume10Day', \
                'sharesOutstanding','floatShares','heldPercentInstitutions', \
                'heldPercentInsiders','marketCap'] 

    typecn=["公司信息","财务信息","市场信息"]
    typeinfo=typecn[options.index(option)]
    print("\n===",texttranslate("证券快照TTM：")+typeinfo,"===")
    typecols=[basiccols,financialcols,marketcols]
    cols=typecols[options.index(option)]
    
    from pandas.api.types import is_numeric_dtype
    for i in cols:
        if i in newcols:
            cn=ectranslate(i)
            if is_numeric_dtype(df[i][0]):                    
                print(cn+':',format(df[i][0],','))  
            else:
                print(cn+':',df[i][0])

    import datetime as dt; today=dt.date.today()    
    print(texttranslate("数据来源：新浪/stooq，")+str(today))
    return df

if __name__ =="__main__":
    option='basic'
    df=print_profile(df, option='basic')
    df=print_profile(df, option='financial')
    df=print_profile(df, option='market')
#==============================================================================
def stock_profile(ticker,verbose=False):
    """
    功能：抓取证券快照信息，包括静态公司信息、财务信息和市场信息。
    输入：证券代码ticker；选项verbose表示是否显示详细信息，默认否。
    输出：一次性打印公司信息、财务信息和市场信息。
    返回：证券快照信息数据表。
    注意：放弃
    """
    print("... Searching for security snapshot information, please wait ...")
    #抓取证券静态信息
    try:
        df=get_profile(ticker)
    except:
        print("  #Error(stock_profile), failed to retrieve or decode profile info of",ticker)
        return None        
    
    #检查抓取到的数据表
    if (df is None) or (len(df)==0):
        print("  #Error(stock_profile), retrieved empty profile info of",ticker)
        return None
    
    df=print_profile(df, option='basic')
    #详细版输出信息
    if verbose:
        df=print_profile_detail(df, option='financial')
        df=print_profile_detail(df, option='market')

    return df


#==============================================================================

if __name__ =="__main__":
    #美股
    info=stock_profile("MSFT")
    info=stock_profile("MSFT",option="market")
    info=stock_profile("MSFT",option="financial")
    #大陆股票
    info=stock_profile("000002.SZ")
    info=stock_profile("000002.SZ",option="financial")
    info=stock_profile("000002.SZ",option="market")
    #港股
    info=stock_profile("00700.HK",option="financial")
    info=stock_profile("00700.HK",option="market")
    info=stock_profile("00700.HK",option="basic")
    #印度股票
    info=stock_profile("TCS.NS",option="financial")
    info=stock_profile("TCS.NS",option="market")
    info=stock_profile("TCS.NS",option="basic")
    #德国股票
    info=stock_profile("BMW.DE",option="financial")
    info=stock_profile("BMW.DE",option="market")
    info=stock_profile("BMW.DE",option="basic")
    #日本股票
    info=stock_profile("6758.t",option="financial")
    info=stock_profile("6758.t",option="market")
    info=stock_profile("6758.t",option="basic")
    info=stock_profile("9501.t",option="financial")
    #ETF指数基金
    info=stock_profile("SPY")
    info=stock_profile("SPY",option="market")
    info=stock_profile("SPY",option="financial")
    #债券期货
    info=stock_profile("US=F")
    info=stock_profile("US=F",option="market")
    info=stock_profile("US=F",option="financial") 
    #债券基金
    info=stock_profile("LBNDX",option="basic")
    info=stock_profile("LBNDX",option="market")
    info=stock_profile("LBNDX",option="financial")
    #期货
    info=stock_profile("VXX",option="basic")
    info=stock_profile("VXX",option="market")
    info=stock_profile("VXX",option="financial")    

#==============================================================================
def security_price(ticker, fromdate, todate, adj=False, datatag=False, power=4):
    """
    功能：绘制证券价格折线图。为维持兼容性，套壳函数stock_price
    """
    df=stock_price(ticker=ticker,fromdate=fromdate,todate=todate,adj=adj,datatag=datatag,power=power)
    
    return df

#==============================================================================
def stock_price(ticker, fromdate, todate, adj=False, datatag=False, power=4):
    """
    功能：绘制证券价格折线图。
    输入：证券代码ticker；开始日期fromdate，结束日期todate；
    是否标注数据标签datatag，默认否；多项式趋势线的阶数，若为0则不绘制趋势线。
    输出：绘制证券价格折线图
    返回：证券价格数据表
    """
    #抓取证券价格
    df=get_price(ticker,fromdate,todate,adj=adj)
    
    if not (df is None):
        tickername=codetranslate(ticker)

        import datetime; today = datetime.date.today()
        lang=check_language()
        if lang == 'English':
            titletxt=texttranslate("Security Price Trend：")+tickername
            footnote=texttranslate("Source: sina/stooq，")+str(today)
        else:
            titletxt=texttranslate("证券价格走势图：")+tickername
            footnote=texttranslate("数据来源：新浪/stooq，")+str(today)
        pricetype='Close'
        collabel=ectranslate(pricetype)
        ylabeltxt=collabel
        plot_line(df,pricetype,collabel,ylabeltxt,titletxt,footnote,datatag=datatag,power=power)
    
    return df

if __name__ =="__main__":
    priceinfo=stock_price("000002.SZ","2020-2-1","2020-3-10",power=3)

#==============================================================================
def stock_ret(ticker,fromdate,todate,type="Daily Ret%",datatag=False,power=4,graph=True):
    """
    功能：绘制证券收益率折线图。
    输入：证券代码ticker；开始日期fromdate，结束日期todate；收益率类型type；
    是否标注数据标签datatag，默认否；多项式趋势线的阶数，若为0则不绘制趋势线。
    输出：绘制证券价格折线图
    返回：证券价格数据表
    """
    #调整抓取样本的开始日期366*2=732，以便保证有足够的样本供后续计算
    fromdate1=date_adjust(fromdate, -732)

    #抓取证券价格
    adj=False
    if 'Adj' in type: adj=True
    pricedf=get_price(ticker,fromdate1,todate,adj=adj)
    if pricedf is None:
        print("  #Error(stock_ret): failed to find price info for",ticker,fromdate,todate)
        return None
    pricedfcols=list(pricedf)    
    
    #加入日收益率
    drdf=calc_daily_return(pricedf)
    #加入滚动收益率
    prdf1=calc_rolling_return(drdf, "Weekly") 
    prdf2=calc_rolling_return(prdf1, "Monthly")
    prdf3=calc_rolling_return(prdf2, "Quarterly")
    prdf4=calc_rolling_return(prdf3, "Annual") 
    
    #加入扩展收益率
    erdf=calc_expanding_return(prdf4,fromdate)
    
    #如果不绘图则直接返回数据表
    if not graph: return erdf    
    
    #获得支持的收益率类型列名
    colnames=list(erdf)
    for c in pricedfcols:
        colnames.remove(c)
    
    #检查type是否在支持的收益率列名中
    if not (type in colnames):
        print("  #Error(stock_ret)：only support return types of",colnames)
        return        

    titletxt=texttranslate("证券收益率走势图：")+codetranslate(ticker)
    import datetime; today = datetime.date.today()
    footnote=texttranslate("数据来源：新浪/stooq，")+str(today)
    collabel=ectranslate(type)
    ylabeltxt=ectranslate(type)
    pltdf=erdf[erdf.index >= fromdate]
    plot_line(pltdf,type,collabel,ylabeltxt,titletxt,footnote,datatag=datatag, \
              power=power,zeroline=True)
    
    return erdf

if __name__ =="__main__":
    ticker="000002.SZ"
    fromdate="2020-1-1"
    todate="2020-3-16"
    type="Daily Ret%"
    datatag=False
    power=3
    retinfo=stock_ret("000002.SZ","2020-1-1","2020-3-16",power=3)
    retinfo=stock_ret("000002.SZ","2020-1-1","2020-3-16","Daily Adj Ret%",power=3)
    retinfo=stock_ret("000002.SZ","2020-1-1","2020-3-16","Weekly Ret%",power=3)
    retinfo=stock_ret("000002.SZ","2020-1-1","2020-3-16","Monthly Ret%",power=4)
    retinfo=stock_ret("000002.SZ","2020-1-1","2020-3-16","Quarterly Ret%",power=4)
    retinfo=stock_ret("000002.SZ","2019-1-1","2020-3-16","Annual Ret%",power=4)
    retinfo=stock_ret("000002.SZ","2019-1-1","2020-3-16","Cum Ret%",power=4)


#==============================================================================
def stock_price_volatility(ticker,fromdate,todate,type="Weekly Price Volatility",datatag=False,power=4,graph=True):
    """
    功能：绘制证券价格波动风险折线图。
    输入：证券代码ticker；开始日期fromdate，结束日期todate；期间类型type；
    是否标注数据标签datatag，默认否；多项式趋势线的阶数，若为0则不绘制趋势线。
    输出：绘制证券价格波动折线图
    返回：证券价格数据表
    """
    #调整抓取样本的开始日期，以便保证有足够的样本供后续计算
    fromdate1=date_adjust(fromdate, -400)

    #抓取证券价格
    adj=False
    if 'Adj' in type: adj=True
    pricedf=get_price(ticker,fromdate1,todate,adj=adj)
    if pricedf is None:
        print("  #Error(stock_price_volatility)：failed to find price info for",ticker,fromdate,todate)
        return
    pricedfcols=list(pricedf)    
    
    #加入滚动价格波动风险
    prdf1=rolling_price_volatility(pricedf, "Weekly") 
    prdf2=rolling_price_volatility(prdf1, "Monthly")
    prdf3=rolling_price_volatility(prdf2, "Quarterly")
    prdf4=rolling_price_volatility(prdf3, "Annual") 
    
    #加入累计价格波动风险
    erdf=expanding_price_volatility(prdf4,fromdate)
    
    #如果不绘图则直接返回数据表
    if not graph: return erdf    
    
    #获得支持的价格波动风险类型列名，去掉不需要的列名
    colnames=list(erdf)
    for c in pricedfcols:
        colnames.remove(c)
    
    #检查type是否在支持的收益率列名中
    if not (type in colnames):
        print("  #Error(stock_price_volatility)：only support price risk types of",colnames)
        return        

    titletxt=texttranslate("证券价格波动风险走势图：")+codetranslate(ticker)
    import datetime; today = datetime.date.today()
    footnote=texttranslate("数据来源：新浪/stooq，")+str(today)
    collabel=ectranslate(type)
    ylabeltxt=ectranslate(type)
    pltdf=erdf[erdf.index >= fromdate]
    plot_line(pltdf,type,collabel,ylabeltxt,titletxt,footnote,datatag=datatag, \
              power=power,zeroline=True)
    
    return erdf

if __name__ =="__main__":
    ticker="000002.SZ"
    fromdate="2020-1-1"
    todate="2020-3-16"
    type="Daily Ret%"
    datatag=False
    power=3

    pv=stock_price_volatility("000002.SZ","2019-1-1","2020-3-16","Annual Price Volatility")
    pv=stock_price_volatility("000002.SZ","2019-1-1","2020-3-16","Annual Exp Price Volatility")

#==============================================================================
def price_volatility2(pricedf,ticker,fromdate,todate,type="Weekly Price Volatility",datatag=False,power=4,graph=True):
    """
    功能：绘制证券价格波动风险折线图。与函数price_volatility的唯一区别是不抓取股价。
    输入：股价数据集pricedf；证券代码ticker；开始日期fromdate，结束日期todate；期间类型type；
    是否标注数据标签datatag，默认否；多项式趋势线的阶数，若为0则不绘制趋势线。
    输出：绘制证券价格波动折线图
    返回：证券价格数据表
    """
    pricedfcols=list(pricedf)
    #加入滚动价格波动风险
    prdf1=rolling_price_volatility(pricedf, "Weekly") 
    prdf2=rolling_price_volatility(prdf1, "Monthly")
    prdf3=rolling_price_volatility(prdf2, "Quarterly")
    prdf4=rolling_price_volatility(prdf3, "Annual") 
    
    #加入累计价格波动风险
    erdf=expanding_price_volatility(prdf4,fromdate)
    
    #如果不绘图则直接返回数据表
    if not graph: return erdf    
    
    #获得支持的价格波动风险类型列名，去掉不需要的列名
    colnames=list(erdf)
    for c in pricedfcols:
        colnames.remove(c)
    
    #检查type是否在支持的收益率列名中
    if not (type in colnames):
        print("  #Error(price_volatility2)：only support price risk types of",colnames)
        return        

    titletxt=texttranslate("证券价格波动风险走势图：")+codetranslate(ticker)
    import datetime; today = datetime.date.today()
    footnote=texttranslate("数据来源：新浪/stooq，")+str(today)
    collabel=ectranslate(type)
    ylabeltxt=ectranslate(type)
    pltdf=erdf[erdf.index >= fromdate]
    plot_line(pltdf,type,collabel,ylabeltxt,titletxt,footnote,datatag=datatag, \
              power=power,zeroline=True)
    
    return erdf

if __name__ =="__main__":
    ticker="000002.SZ"
    fromdate="2020-1-1"
    todate="2020-3-16"
    type="Daily Ret%"
    datatag=False
    power=3
    
    df=get_price("000002.SZ","2019-1-1","2020-3-16")
    pv=price_volatility2(df,"000002.SZ","2019-1-1","2020-3-16","Annual Price Volatility")
    pv=price_volatility2(df,"000002.SZ","2019-1-1","2020-3-16","Annual Exp Price Volatility")

#==============================================================================
def stock_ret_volatility(ticker,fromdate,todate,type="Weekly Ret Volatility%",datatag=False,power=4,graph=True):
    """
    功能：绘制证券收益率波动风险折线图。
    输入：证券代码ticker；开始日期fromdate，结束日期todate；期间类型type；
    是否标注数据标签datatag，默认否；多项式趋势线的阶数，若为0则不绘制趋势线。
    输出：绘制证券收益率波动折线图
    返回：证券收益率波动数据表
    """
    #调整抓取样本的开始日期，以便保证有足够的样本供后续计算
    fromdate1=date_adjust(fromdate, -400)
    retdf=stock_ret(ticker,fromdate1,todate,graph=False)
    pricedfcols=list(retdf)
    
    #加入滚动收益率波动风险
    prdf1=rolling_ret_volatility(retdf, "Weekly") 
    prdf2=rolling_ret_volatility(prdf1, "Monthly")
    prdf3=rolling_ret_volatility(prdf2, "Quarterly")
    prdf4=rolling_ret_volatility(prdf3, "Annual") 
    
    #加入累计收益率波动风险
    erdf=expanding_ret_volatility(prdf4,fromdate)
    
    #如果不绘图则直接返回数据表
    if not graph: return erdf    
    
    #获得支持的收益率波动风险类型列名，去掉不需要的列名
    colnames=list(erdf)
    for c in pricedfcols:
        colnames.remove(c)
    
    #检查type是否在支持的收益率波动指标列名中
    if not (type in colnames):
        print("  #Error(stock_ret_volatility)，only support return risk types of",colnames)
        return        

    titletxt=texttranslate("证券收益率波动风险走势图：")+codetranslate(ticker)
    import datetime; today = datetime.date.today()
    footnote=texttranslate("数据来源：新浪/stooq，")+str(today)
    collabel=ectranslate(type)
    ylabeltxt=ectranslate(type)
    pltdf=erdf[erdf.index >= fromdate]
    plot_line(pltdf,type,collabel,ylabeltxt,titletxt,footnote,datatag=datatag, \
              power=power,zeroline=True)
    
    return erdf

if __name__ =="__main__":
    ticker="000002.SZ"
    fromdate="2020-1-1"
    todate="2020-3-16"
    type="Daily Ret%"
    datatag=False
    power=3

    pv=stock_ret_volatility("000002.SZ","2019-1-1","2020-3-16","Annual Ret Volatility%")
    pv=stock_ret_volatility("000002.SZ","2019-1-1","2020-3-16","Annual Exp Ret Volatility%")


#==============================================================================
def ret_volatility2(retdf,ticker,fromdate,todate,type="Weekly Ret Volatility%",datatag=False,power=4,graph=True):
    """
    功能：绘制证券收益率波动风险折线图。与函数ret_volatility的唯一区别是不抓取股价。
    输入：股价数据集pricedf；证券代码ticker；开始日期fromdate，结束日期todate；期间类型type；
    是否标注数据标签datatag，默认否；多项式趋势线的阶数，若为0则不绘制趋势线。
    输出：绘制证券收益率波动折线图
    返回：证券收益率波动数据表
    """
    retdfcols=list(retdf)
    #retdf=calc_daily_return(pricedf)    
    #加入滚动价格波动风险
    prdf1=rolling_ret_volatility(retdf, "Weekly") 
    prdf2=rolling_ret_volatility(prdf1, "Monthly")
    prdf3=rolling_ret_volatility(prdf2, "Quarterly")
    prdf4=rolling_ret_volatility(prdf3, "Annual") 
    
    #加入累计价格波动风险
    erdf=expanding_ret_volatility(prdf4,fromdate)
    
    #如果不绘图则直接返回数据表
    if not graph: return erdf    
    
    #获得支持的价格波动风险类型列名，去掉不需要的列名
    colnames=list(erdf)
    for c in retdfcols:
        colnames.remove(c)
    
    #检查type是否在支持的收益率列名中
    if not (type in colnames):
        print("  #Error(ret_volatility2): only support return risk types of",colnames)
        return        

    titletxt=texttranslate("证券收益率波动风险走势图：")+codetranslate(ticker)
    import datetime; today = datetime.date.today()
    footnote=texttranslate("数据来源：新浪/stooq，")+str(today)
    collabel=ectranslate(type)
    ylabeltxt=ectranslate(type)
    pltdf=erdf[erdf.index >= fromdate]
    plot_line(pltdf,type,collabel,ylabeltxt,titletxt,footnote,datatag=datatag, \
              power=power,zeroline=True)
    
    return erdf

if __name__ =="__main__":
    ticker="000002.SZ"
    fromdate="2020-1-1"
    todate="2020-3-16"
    type="Daily Ret%"
    datatag=False
    power=3
    
    df=get_price("000002.SZ","2019-1-1","2020-3-16")
    pv=price_volatility2(df,"000002.SZ","2019-1-1","2020-3-16","Annual Price Volatility")
    pv=price_volatility2(df,"000002.SZ","2019-1-1","2020-3-16","Annual Exp Price Volatility")

#==============================================================================
def ret_lpsd(ticker,fromdate,todate,type="Weekly Ret Volatility%",datatag=False,power=4,graph=True):
    """
    功能：绘制证券收益率波动损失风险折线图。
    输入：证券代码ticker；开始日期fromdate，结束日期todate；期间类型type；
    是否标注数据标签datatag，默认否；多项式趋势线的阶数，若为0则不绘制趋势线。
    输出：绘制证券收益率下偏标准差折线图
    返回：证券收益率下偏标准差数据表
    """
    #调整抓取样本的开始日期，以便保证有足够的样本供后续计算
    fromdate1=date_adjust(fromdate, -400)
    retdf=stock_ret(ticker,fromdate1,todate,graph=False)
    pricedfcols=list(retdf)
    
    #加入滚动收益率下偏标准差
    prdf1=rolling_ret_lpsd(retdf, "Weekly") 
    prdf2=rolling_ret_lpsd(prdf1, "Monthly")
    prdf3=rolling_ret_lpsd(prdf2, "Quarterly")
    prdf4=rolling_ret_lpsd(prdf3, "Annual") 
    
    #加入扩展收益率下偏标准差
    erdf=expanding_ret_lpsd(prdf4,fromdate)
    
    #如果不绘图则直接返回数据表
    if not graph: return erdf    
    
    #获得支持的收益率波动风险类型列名，去掉不需要的列名
    colnames=list(erdf)
    for c in pricedfcols:
        colnames.remove(c)
    
    #检查type是否在支持的收益率波动指标列名中
    if not (type in colnames):
        print("  #Error(ret_lpsd): only support return risk types of",colnames)
        return        

    titletxt=texttranslate("证券收益率波动损失风险走势图：")+codetranslate(ticker)
    import datetime; today = datetime.date.today()
    footnote=texttranslate("数据来源：新浪/stooq，")+str(today)
    collabel=ectranslate(type)
    ylabeltxt=ectranslate(type)
    pltdf=erdf[erdf.index >= fromdate]
    plot_line(pltdf,type,collabel,ylabeltxt,titletxt,footnote,datatag=datatag, \
              power=power,zeroline=True)
    
    return erdf

if __name__ =="__main__":
    ticker="000002.SZ"
    fromdate="2020-1-1"
    todate="2020-3-16"
    type="Daily Ret%"
    datatag=False
    power=3

    pv=ret_lpsd("000002.SZ","2019-1-1","2020-3-16","Annual Ret Volatility%")
    pv=ret_lpsd("000002.SZ","2019-1-1","2020-3-16","Annual Exp Ret Volatility%")

#==============================================================================
def ret_lpsd2(retdf,ticker,fromdate,todate,type="Weekly Ret Volatility%",datatag=False,power=4,graph=True):
    """
    功能：绘制证券收益率波动损失风险折线图。与函数ret_lpsd的唯一区别是不抓取股价。
    输入：股价数据集pricedf；证券代码ticker；开始日期fromdate，结束日期todate；期间类型type；
    是否标注数据标签datatag，默认否；多项式趋势线的阶数，若为0则不绘制趋势线。
    输出：绘制证券收益率下偏标准差折线图。
    返回：证券收益率下偏标准差数据表。
    """
    retdfcols=list(retdf)
    #retdf=calc_daily_return(pricedf)    
    #加入滚动价格波动风险
    prdf1=rolling_ret_lpsd(retdf, "Weekly") 
    prdf2=rolling_ret_lpsd(prdf1, "Monthly")
    prdf3=rolling_ret_lpsd(prdf2, "Quarterly")
    prdf4=rolling_ret_lpsd(prdf3, "Annual") 
    
    #加入扩展收益率下偏标准差
    erdf=expanding_ret_lpsd(prdf4,fromdate)
    
    #如果不绘图则直接返回数据表
    if not graph: return erdf    
    
    #获得支持的价格波动风险类型列名，去掉不需要的列名
    colnames=list(erdf)
    for c in retdfcols:
        colnames.remove(c)
    
    #检查type是否在支持的收益率列名中
    if not (type in colnames):
        print("  #Error(ret_lpsd2): only support return risk types of",colnames)
        return        

    titletxt=texttranslate("证券收益率波动损失风险走势图：")+codetranslate(ticker)
    import datetime; today = datetime.date.today()
    footnote=texttranslate("数据来源：新浪/stooq，")+str(today)
    collabel=ectranslate(type)
    ylabeltxt=ectranslate(type)
    pltdf=erdf[erdf.index >= fromdate]
    plot_line(pltdf,type,collabel,ylabeltxt,titletxt,footnote,datatag=datatag, \
              power=power,zeroline=True)
    
    return erdf

if __name__ =="__main__":
    ticker="000002.SZ"
    fromdate="2020-1-1"
    todate="2020-3-16"
    type="Daily Ret%"
    datatag=False
    power=3
    
    df=get_price("000002.SZ","2019-1-1","2020-3-16")
    pv=price_lpsd2(df,"000002.SZ","2019-1-1","2020-3-16","Annual Price Volatility")
    pv=price_lpsd2(df,"000002.SZ","2019-1-1","2020-3-16","Annual Exp Price Volatility")
#==============================================================================
def comp_1security_2measures(df,measure1,measure2,twinx=False,loc1='upper left',loc2='lower left'):
    """
    功能：对比绘制一只证券两个指标的折线图。
    输入：证券指标数据集df；行情类别measure1/2。
    输出：绘制证券行情双折线图，基于twinx判断使用单轴或双轴坐标
    返回：无
    """
    #筛选证券指标，检验是否支持指标
    dfcols=list(df)
    #nouselist=['date','Weekday','ticker']
    #for c in nouselist: dfcols.remove(c)
    
    if not (measure1 in dfcols) or not (measure2 in dfcols):
        print("... #Error(comp_1security_2measures)，supporting measures: ",dfcols)
        return        

    #判断是否绘制水平0线
    pricelist=['High','Low','Open','Close','Volume','Adj Close']
    if (measure1 in pricelist) or (measure2 in pricelist): 
        zeroline=False
    else: zeroline=True

    #提取信息
    ticker=df['ticker'][0]
    fromdate=str(df.index[0].date())
    todate=str(df.index[-1].date())
    label1=ectranslate(measure1)
    label2=ectranslate(measure2)
    ylabeltxt=""
    
    lang=check_language()
    if lang == 'English':
        titletxt="Security Trend: "+codetranslate(ticker)
    else:
        titletxt=texttranslate("证券指标走势对比：")+codetranslate(ticker)
    import datetime; today = datetime.date.today()
    if lang == 'English':
        footnote="Source: sina/eastmoney/stooq, "+str(today)
    else:
        footnote=texttranslate("数据来源：sina/eastmoney/stooq，")+str(today)
    
    #绘图
    plot_line2(df,ticker,measure1,label1,df,ticker,measure2,label2, \
                   ylabeltxt,titletxt,footnote,zeroline=zeroline,twinx=twinx, \
                       loc1=loc1,loc2=loc2)

    return 

if __name__ =="__main__":
    ticker='000002.SZ'
    measure1='Daily Ret%'
    measure2='Daily Adj Ret%'
    fromdate='2020-1-1'
    todate='2020-3-16'
    df=stock_ret(ticker,fromdate,todate,graph=False)
    comp_1security_2measures(df,measure1,measure2)
#==============================================================================
def comp_2securities_1measure(df1,df2,measure,twinx=False,loc1='upper left',loc2='lower left',graph=True):
    """
    功能：对比绘制两只证券的相同指标折线图。
    输入：指标数据集df1/2；证券代码ticker1/2；指标类别measure。
    输出：绘制证券指标双折线图，基于twinx判断使用单轴或双轴坐标。
    返回：无
    """
    
    #筛选证券指标，检验是否支持指标
    dfcols=list(df1)
    #nouselist=['date','Weekday','ticker']
    #for c in nouselist: dfcols.remove(c)
    
    if not (measure in dfcols):
        print("  #Error(comp_2securities_1measure)： only support measurement types of",dfcols)
        return        

    #判断是否绘制水平0线
    pricelist=['High','Low','Open','Close','Volume','Adj Close']
    if measure in pricelist: zeroline=False
    else: zeroline=True

    #提取信息
    try:
        ticker1=df1['ticker'][0]
    except:
        print("  #Error(comp_2securities_1measure)： none info found for the 1st symbol")
        return
    try:
        ticker2=df2['ticker'][0]
    except:
        print("  #Error(comp_2securities_1measure)： none info found for the 2nd symbol")
        return
    
    fromdate=str(df1.index[0].date())
    todate=str(df1.index[-1].date())
    label=ectranslate(measure)
    ylabeltxt=ectranslate(measure)

    lang=check_language()
    if lang == 'English':
        titletxt="Security Trend: "+codetranslate(ticker1)+" vs "+codetranslate(ticker2)
    else:
        titletxt=texttranslate("证券指标走势对比：")+codetranslate(ticker1)+" vs "+codetranslate(ticker2)
        
    import datetime; today = datetime.date.today()
    if lang == 'English':
        footnote=texttranslate("Source: sina/eastmoney/stooq，")+str(today)
    else:
        footnote=texttranslate("数据来源：sina/eastmoney/stooq，")+str(today)

    plot_line2(df1,ticker1,measure,label,df2,ticker2,measure,label, \
                   ylabeltxt,titletxt,footnote,zeroline=zeroline,twinx=twinx, \
                       loc1=loc1,loc2=loc2)

    return 

if __name__ =="__main__":
    ticker1='000002.SZ'
    ticker2='600266.SS'
    measure='Daily Ret%'
    fromdate='2020-1-1'
    todate='2020-3-16'
    df1=stock_ret(ticker1,fromdate,todate,graph=False)
    df2=stock_ret(ticker2,fromdate,todate,graph=False)
    comp_2securities_1measure(df1,df2,measure)
#==============================================================================
def compare_security(tickers,measures,fromdate,todate,twinx=False, \
                     loc1='best',loc2='lower left',graph=True):
    """
    功能：函数克隆compare_stock
    """
    result=compare_stock(tickers=tickers,measures=measures, \
                  fromdate=fromdate,todate=todate,twinx=twinx, \
                      loc1=loc1,loc2=loc2,graph=graph)
    return result

#==============================================================================
def compare_stock(tickers,measures,fromdate,todate,twinx=False, \
                  loc1='best',loc2='lower left',graph=True):    
    """
    功能：对比绘制折线图：一只证券的两种测度，或两只证券的同一个测度。
    输入：
    证券代码tickers，如果是一个列表且内含两个证券代码，则认为希望比较两个证券的
    同一个测度指标。如果是一个列表但只内含一个证券代码或只是一个证券代码的字符串，
    则认为希望比较一个证券的两个测度指标。
    测度指标measures：如果是一个列表且内含两个测度指标，则认为希望比较一个证券的
    两个测度指标。如果是一个列表但只内含一个测度指标或只是一个测度指标的字符串，
    则认为希望比较两个证券的同一个测度指标。
    如果两个判断互相矛盾，以第一个为准。
    开始日期fromdate，结束日期todate。
    输出：绘制证券价格折线图，手动指定是否使用单轴或双轴坐标。
    返回：无
    """
    #调试开关
    DEBUG=False
    
    #判断证券代码个数
    #如果tickers只是一个字符串
    security_num = 0
    if isinstance(tickers,str): 
        security_num = 1
        ticker1 = tickers
    #如果tickers是一个列表
    if isinstance(tickers,list): 
        security_num = len(tickers)
        if security_num == 0:
            print("  #Error(compare_stock)：security code/codes needed.")
            return None,None
        if security_num >= 1: ticker1 = tickers[0]
        if security_num >= 2: ticker2 = tickers[1]
            
    #判断测度个数
    #如果measures只是一个字符串
    measure_num = 0
    if isinstance(measures,str): 
        measure_num = 1
        measure1 = measures
    #如果measures是一个列表
    if isinstance(measures,list): 
        measure_num = len(measures)
        if measure_num == 0:
            print("  #Error(compare_stock)： a measurement indicator needed.")
            return None,None
        if measure_num >= 1: measure1 = measures[0]
        if measure_num >= 2: measure2 = measures[1]

    #是否单一证券代码+两个测度指标
    if (security_num == 1) and (measure_num >= 2):
        #证券ticker1：抓取行情，并计算其各种期间的收益率
        df1a=stock_ret(ticker1,fromdate,todate,graph=False)
        if df1a is None: return None,None
        if DEBUG: print("compare|df1a first date:",df1a.index[0])
        #加入价格波动指标
        df1b=price_volatility2(df1a,ticker1,fromdate,todate,graph=False)
        if DEBUG: print("compare|df1b first date:",df1b.index[0])
        #加入收益率波动指标
        df1c=ret_volatility2(df1b,ticker1,fromdate,todate,graph=False)
        if DEBUG: print("compare|df1c first date:",df1c.index[0])
        #加入收益率下偏标准差指标
        df1d=ret_lpsd2(df1c,ticker1,fromdate,todate,graph=False)
        if DEBUG: print("compare|df1d first date:",df1d.index[0])
        
        #去掉开始日期以前的数据
        pltdf1=df1d[df1d.index >= fromdate]
        #绘制单个证券的双指标对比图
        if graph:
            comp_1security_2measures(pltdf1,measure1,measure2,twinx=twinx,loc1=loc1,loc2=loc2,graph=graph)
        
        result1=pltdf1[[measure1]]
        result2=pltdf1[[measure2]]
        
    elif (security_num >= 2) and (measure_num >= 1):
        #双证券+单个测度指标        
        #证券ticker1：抓取行情，并计算其各种期间的收益率
        df1a=stock_ret(ticker1,fromdate,todate,graph=False)
        if df1a is None: return None,None
        #加入价格波动指标
        df1b=price_volatility2(df1a,ticker1,fromdate,todate,graph=False)
        #加入收益率波动指标
        df1c=ret_volatility2(df1b,ticker1,fromdate,todate,graph=False)
        #加入收益率下偏标准差指标
        df1d=ret_lpsd2(df1c,ticker1,fromdate,todate,graph=False)        
        #去掉开始日期以前的数据
        pltdf1=df1d[df1d.index >= fromdate]
        
        #证券ticker2：
        df2a=stock_ret(ticker2,fromdate,todate,graph=False)
        if df2a is None: return None,None
        df2b=price_volatility2(df2a,ticker2,fromdate,todate,graph=False)
        df2c=ret_volatility2(df2b,ticker2,fromdate,todate,graph=False)
        df2d=ret_lpsd2(df2c,ticker2,fromdate,todate,graph=False)
        pltdf2=df2d[df2d.index >= fromdate]
        
        #绘制双证券单指标对比图
        if graph:
            comp_2securities_1measure(pltdf1,pltdf2,measure1,twinx=twinx,loc1=loc1,loc2=loc2,graph=graph)
        
        result1=pltdf1[[measure1]]
        result2=pltdf2[[measure1]]
    else:
        print("  #Error(compare_stock)：do not understand what to compare.")
        return None,None

    return result1,result2

if __name__ =="__main__":
    tickers='000002.SZ'
    measures=['Close','Adj Close']
    fromdate='2020-1-1'
    todate='2020-3-16'
    compare_stock(tickers,measures,fromdate,todate)            

    tickers2=['000002.SZ','600266.SS']
    measures2=['Close','Adj Close']
    compare_stock(tickers2,measures2,fromdate,todate)

    tickers3=['000002.SZ','600266.SS']
    measures3='Close'
    compare_stock(tickers3,measures3,fromdate,todate)    

    tickers4=['000002.SZ','600606.SS','600266.SS']
    measures4=['Close','Adj Close','Daily Return']
    compare_stock(tickers4,measures4,fromdate,todate)      
    
#==============================================================================
if __name__ =="__main__":
    tickers1=["AMZN","EBAY","SHOP","BABA","JD"]
    tickers2=["AMZN","EBAY","SHOP","BABA","JD","PDD"]
    measure1="Annual Ret%"
    measure2="Exp Ret%"
    start="2022-1-1"
    end="2022-7-31"
    
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
if __name__ =="__main__":
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
def candlestick(stkcd,fromdate,todate,volume=False,style='default',mav=0):
    """
    功能：绘制证券价格K线图。
    输入：证券代码ticker；开始日期fromdate，结束日期todate；
    绘图类型type：默认为蜡烛图；
    是否绘制交易量volume：默认否；
    绘图风格style：默认为黑白图；
    输出：绘制证券价格蜡烛图线图
    返回：证券价格数据表
    """
    #检查命令参数
    stylelist=['blueskies','brasil','charles','checkers','classic','default', \
               'mike','nightclouds','sas','starsandstripes','yahoo']
    if not (style in stylelist):
        print("  #Error(candlestick)，onply support graphics styles of",stylelist)
        return
    s  = mpf.make_mpf_style(base_mpf_style=style,rc=mpfrc)
    
    #抓取证券价格
    daily=get_price(stkcd,fromdate,todate)
    
    if daily is None:
        print("  #Error(candlestick): failed to get price info of",stkcd,fromdate,todate)
        return
   
    #绘制蜡烛图
    lang=check_language()
    if lang == 'English':
        ylabel_txt='Price'
        ylabel_lower_txt='Volume'
    else:
        ylabel_txt='价格'
        ylabel_lower_txt='成交量'
        
    titletxt=codetranslate(stkcd)
    if mav > 1: 
        mpf.plot(daily,type='candle',
             volume=volume,
             style=s,
             title=titletxt,
             datetime_format='%Y-%m-%d',
             tight_layout=True,
             xrotation=15,
             ylabel=texttranslate(ylabel_txt),
             ylabel_lower=texttranslate(ylabel_lower_txt),
             mav=mav)       
    else: 
        mpf.plot(daily,type='candle',
             volume=volume,
             style=s,
             datetime_format='%Y-%m-%d',
             tight_layout=True,
             xrotation=15,
             title=titletxt,
             ylabel=texttranslate(ylabel_txt),
             ylabel_lower=texttranslate(ylabel_lower_txt)
             )
    reset_plt()
    return daily

if __name__ =="__main__":
    stkcd='000002.SZ'
    fromdate='2020-2-1'
    todate='2020-3-10'
    type='candle'
    volume=True
    style='default'
    mav=0
    line=False
    price=candlestick("000002.SZ","2020-2-1","2020-2-29")    

#==============================================================================
def candlestick_pro(stkcd,fromdate,todate,colorup='#00ff00',colordown='#ff00ff',style='nightclouds'):
    """
    功能：绘制证券价格K线图。
    输入：证券代码ticker；开始日期fromdate，结束日期todate；
    绘图类型type：默认为蜡烛图；
    是否绘制交易量volume：默认否；
    绘图风格style：nightclouds修改版；
    输出：绘制证券价格蜡烛图线图
    返回：证券价格数据表
    注意：可能导致其后的matplotlib绘图汉字乱码
    """

    #抓取证券价格
    daily=get_price(stkcd,fromdate,todate)
    
    if daily is None:
        print("  #Error(candlestick_pro): failed to get price info of",stkcd,fromdate,todate)
        return
   
    #绘制蜡烛图
    #在原有的风格nightclouds基础上定制阳线和阴线柱子的色彩，形成自定义风格s
    mc = mpf.make_marketcolors(up=colorup,down=colordown,inherit=True)
    s  = mpf.make_mpf_style(base_mpf_style=style,marketcolors=mc,rc=mpfrc)
    #kwargs = dict(type='candle',mav=(2,4,6),volume=True,figratio=(10,8),figscale=0.75)
    #kwargs = dict(type='candle',mav=(2,4,6),volume=True,figscale=0.75)
    kwargs = dict(type='candle',mav=5,volume=True)
    #titletxt=str(stkcd)
    titletxt=codetranslate(stkcd)
    mpf.plot(daily,**kwargs,
             style=s,
             datetime_format='%Y-%m-%d',
             tight_layout=True,
             xrotation=15,
             title=titletxt,
             ylabel=texttranslate("价格"),
             ylabel_lower=texttranslate("成交量")
             )       
    reset_plt()
    return daily

if __name__ =="__main__":
    stkcd='000002.SZ'
    fromdate='2020-2-1'
    todate='2020-3-10'
    type='candle'
    volume=True
    style='default'
    mav=0
    line=False
    price=candlestick_pro("000002.SZ","2020-2-1","2020-2-29")    
#==============================================================================
def candlestick_demo(stkcd,fromdate,todate,colorup='red',colordown='black',width=0.7):
    """
    功能：绘制证券价格K线图，叠加收盘价。
    输入：证券代码ticker；开始日期fromdate，结束日期todate；
    阳线颜色colorup='red'，阴线颜色colordown='black'，柱子宽度width=0.7
    输出：绘制证券价格蜡烛图线图
    返回：证券价格数据表
    """
    #抓取证券价格
    p=get_price(stkcd,fromdate,todate)    
    if p is None:
        print("  #Error(candlestick_demo): failed to get price info of",stkcd,fromdate,todate)
        return    

    import numpy as np
    b= np.array(p.reset_index()[['Date','Open','High','Low','Close']])
    
    #change 1st column of b to number type
    import matplotlib.dates as dt2
    b[:,0] = dt2.date2num(b[:,0])	
     
    #specify the size of the graph
    #fig,ax=plt.subplots(figsize=(10,6))	
    fig,ax=plt.subplots()
    
    #绘制各个价格的折线图
    lang=check_language()
    if lang == 'English':   
        open_txt='Open'
        high_txt='High'
        low_txt='Low'
        close_txt='Close'
    else:
        open_txt='开盘价'
        high_txt='最高价'
        low_txt='最低价'
        close_txt='收盘价'
        
    plt.plot(p.index,p['Open'],color='green',ls="--",label=open_txt,marker='>',markersize=10,linewidth=2)
    plt.plot(p.index,p['High'],color='cyan',ls="-.",label=high_txt,marker='^',markersize=10,linewidth=2)
    plt.plot(p.index,p['Low'],color='k',ls=":",label=low_txt,marker='v',markersize=10,linewidth=2)
    plt.plot(p.index,p['Close'],color='blue',ls="-",label=close_txt,marker='<',markersize=10,linewidth=2)
    
    #绘制蜡烛图
    try:
        from mplfinance.original_flavor import candlestick_ohlc
    except:
        print("  #Error(candlestick_demo)： please install plugin mplfinance.")
        print("  Method:")
        print("  In Anaconda Prompt, key in a command: pip install mplfinance")
        return None    
        
    candlestick_ohlc(ax,b,colorup=colorup,colordown=colordown,width=width,alpha=0.5)

    ax.xaxis_date()	#draw dates in x axis
    ax.autoscale_view()
    fig.autofmt_xdate()

    if lang == 'English':   
        titletxt=texttranslate("Security Price Candlestick Demo: ")+codetranslate(str(stkcd))
        price_txt='Price'
        source_txt="Source: "
    else:
        titletxt=texttranslate("证券价格走势蜡烛图演示：")+codetranslate(str(stkcd))
        price_txt='价格'
        source_txt="数据来源: "

    plt.title(titletxt,fontsize=title_txt_size,fontweight='bold')
    plt.ylabel(price_txt,fontsize=ylabel_txt_size)
    plt.xticks(rotation=30)        
    plt.legend(loc="best",fontsize=legend_txt_size)    
    plt.xlabel(source_txt+"sina/stooq",fontsize=xlabel_txt_size)   
    plt.show()
    
    return p

if __name__ =="__main__":
    price=candlestick_demo("000002.SZ","2020-3-1","2020-3-6") 

#==============================================================================   
#==============================================================================   
#==============================================================================   
def stock_dividend(ticker,fromdate,todate):
    """
    功能：显示股票的分红历史
    输入：单一股票代码
    输出：分红历史
    """   
    print("...Searching for the dividend info of stock",ticker)
    result,startdt,enddt=check_period(fromdate,todate)
    if not result: 
        print("  #Error(stock_dividend): invalid period",fromdate,todate)
        return None
    
    import yfinance as yf
    stock = yf.Ticker(ticker)
    try:
        div=stock.dividends
    except:
        print("  #Error(stock_dividend): no div info found for",ticker)
        return None    
    if len(div)==0:
        print("  #Warning(stock_dividend): no div info found for",ticker)
        return None      
    
    #过滤期间
    div1=div[div.index >= startdt]
    div2=div1[div1.index <= enddt]
    if len(div2)==0:
        print("  #Warning(stock_dividend): no div info in period",fromdate,todate)
        return None          
    
    #对齐打印
    import pandas as pd    
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.width', 180) # 设置打印宽度(**重要**)
    """
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    """
    divdf=pd.DataFrame(div2)
    divdf['Index Date']=divdf.index
    datefmt=lambda x : x.strftime('%Y-%m-%d')
    divdf['Dividend Date']= divdf['Index Date'].apply(datefmt)
    
    #增加星期
    from datetime import datetime
    weekdayfmt=lambda x : x.isoweekday()
    divdf['Weekdayiso']= divdf['Index Date'].apply(weekdayfmt)
    wdlist=['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    wdfmt=lambda x : wdlist[x-1]
    divdf['Weekday']= divdf['Weekdayiso'].apply(wdfmt)
    
    #增加序号
    divdf['Seq']=divdf['Dividend Date'].rank(ascending=1)
    divdf['Seq']=divdf['Seq'].astype('int')
    divprt=divdf[['Seq','Dividend Date','Weekday','Dividends']]
    
    print('\n===== '+texttranslate("股票分红历史")+' =====')
    print(texttranslate("股票:"),ticker,'\b,',codetranslate(ticker))
    print(texttranslate("历史期间:"),fromdate,"-",todate)
    
    #修改列命为中文
    divprt.columns = [texttranslate('序号'),texttranslate('日期'),texttranslate('星期'),texttranslate('股息')]
    print(divprt.to_string(index=False))   
    
    import datetime; today = datetime.date.today()
    print(texttranslate("数据来源: 新浪/stooq,"),today)
    
    return divdf
    
    
if __name__ =="__main__":
    ticker='AAPL'  
    fromdate='2019-1-1'
    todate='2020-6-30'

#==============================================================================   
def stock_split(ticker,fromdate,todate):
    """
    功能：显示股票的分拆历史
    输入：单一股票代码
    输出：分拆历史
    """   
    print("...Searching for the split info of stock",ticker)
    result,startdt,enddt=check_period(fromdate,todate)
    if not result: 
        print("  #Error(stock_split): invalid period",fromdate,todate)
        return None
    
    import yfinance as yf
    stock = yf.Ticker(ticker)
    try:
        div=stock.splits
    except:
        print("  #Error(stock_split): no split info found for",ticker)
        return None    
    if len(div)==0:
        print("  #Warning(stock_split): no split info found for",ticker)
        return None      
    
    #过滤期间
    div1=div[div.index >= startdt]
    div2=div1[div1.index <= enddt]
    if len(div2)==0:
        print("  #Warning(stock_split): no split info in period",fromdate,todate)
        return None          
    
    #对齐打印
    import pandas as pd
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.width', 180) # 设置打印宽度(**重要**)
    """    
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    """
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
    
    print('\n===== '+texttranslate("股票分拆历史")+' =====')
    print(texttranslate("股票:"),ticker,'\b,',codetranslate(ticker))
    print(texttranslate("历史期间:"),fromdate,"-",todate)
    divprt.columns=[texttranslate('序号'),texttranslate('日期'),texttranslate('星期'),texttranslate('分拆比例')]
    print(divprt.to_string(index=False))   
    
    import datetime
    today = datetime.date.today()
    print(texttranslate("数据来源: 新浪/stooq,"),today)
    
    return divdf
    
    
if __name__ =="__main__":
    ticker='AAPL'  
    fromdate='1990-1-1'
    todate='2020-6-30'

#==============================================================================   
#==============================================================================   
#==============================================================================
if __name__=='__main__':
    symbol='AAPL'
    symbol='BABA'

def stock_info(symbol):
    """
    功能：返回静态信息
    """
    DEBUG=False
    print("...Searching for information of",symbol,"\b, please wait...")
    
    from yahooquery import Ticker
    stock = Ticker(symbol)

    """
    Asset Profile:
    Head office address/zip/country, Officers, Employees, industry/sector, phone/fax,
    web site,
    Risk ranks: auditRisk, boardRisk, compensationRisk, overallRisk, shareHolderRightRisk,
    compensationRisk: 薪酬风险。Jensen 及 Meckling (1976)的研究指出薪酬與管理者的風險承擔
    具有關連性，站在管理者的立場來看，創新支出的投入使管理者承受更大的薪酬風險(compensation risk)，
    管理者自然地要求更高的薪酬來補貼所面臨的風險，因此企業創新投資對管理者薪酬成正相關。
    boardRisk: 董事会风险
    shareHolderRightRisk：股权风险
    """
    try:
        adict=stock.asset_profile
    except:
        print("  #Error(stock_info): failed to get the profile of",symbol)
        print("  Possible reasons: Wrong stock code, or unstable internet connection")
        return None
    
    keylist=list(adict[symbol].keys())
    import pandas as pd    
    aframe=pd.DataFrame.from_dict(adict, orient='index', columns=keylist)
    ainfo=aframe.T
    info=ainfo.copy()


    """
    ESG Scores: Risk measurements
    peerGroup, ratingYear, 
    environmentScore, governanceScore, socialScore, totalEsg
    dict: peerEnvironmentPerformance, peerGovernancePerformance, peerSocialPerformance, 
    peerEsgScorePerformance
    """
    try:
        adict=stock.esg_scores
    except:
        print("#Error(stock_info): failed to get esg profile of",symbol)
        return None    
    try:    #一些企业无此信息
        keylist=list(adict[symbol].keys())
        aframe=pd.DataFrame.from_dict(adict, orient='index', columns=keylist)
        ainfo=aframe.T
        info=pd.concat([info,ainfo])
    except:
        pass

    """
    Financial Data: TTM???
    currentPrice, targetHighPrice, targetLowPrice, targetMeanPrice, targetMedianPrice, 
    currentRatio, debtToEquity, earningsGrowth, ebitda, ebitdaMargins, financialCurrency,
    freeCashflow, grossMargins, grossProfits, 
    operatingCashflow, operatingMargins, profitMargins,
    quickRatio, returnOnAssets, returnOnEquity, revenueGrowth, revenuePerShare, 
    totalCash, totalCashPerShare, totalDebt, totalRevenue, 
    """
    try:
        adict=stock.financial_data
    except:
        print("  #Error(stock_info): failed to get financial profile of",symbol)
        return None    
    keylist=list(adict[symbol].keys())
    aframe=pd.DataFrame.from_dict(adict, orient='index', columns=keylist)
    ainfo=aframe.T
    info=pd.concat([info,ainfo])    
    

    """
    Key Statistics: TTM???
    52WeekChang, SandP52WeekChang, beta, floatShares, sharesOutstanding, 
    bookValue, earningsQuarterlyGrowth, enterpriseToEbitda, enterpriseToRevenue,
    enterpriseValue, netIncomeToCommon, priceToBook, profitMargins, 
    forwardEps, trailingEps,
    heldPercentInsiders, heldPercentInstitutions, 
    lastFiscalYearEnd, lastSplitDate, lastSplitFactor, mostRecentQuarter, nextFiscalYearEnd,
    """
    try:
        adict=stock.key_stats
    except:
        print("  #Error(stock_info): failed to get key stats of",symbol)
        return None
    keylist=list(adict[symbol].keys())
    aframe=pd.DataFrame.from_dict(adict, orient='index', columns=keylist)
    ainfo=aframe.T
    info=pd.concat([info,ainfo]) 
    
    
    """
    Price Information:
    currency, currencySymbol, exchange, exchangeName, shortName, 
    longName, 
    marketCap, marketState, quoteType, 
    regularMarketChange, regularMarketChangPercent, regularMarketHigh, regularMarketLow, 
    regularMarketOpen, regularMarketPreviousClose, regularMarketPrice, regularMarketTime,
    regularMarketVolume, 
    """
    try:
        adict=stock.price
    except:
        print("  #Error(stock_info): failed to get stock prices of",symbol)
        return None    
    keylist=list(adict[symbol].keys())
    aframe=pd.DataFrame.from_dict(adict, orient='index', columns=keylist)
    ainfo=aframe.T
    info=pd.concat([info,ainfo]) 
    

    """
    Quote Type:
    exchange, firstTradeDateEpocUtc(上市日期), longName, quoteType(证券类型：股票), 
    shortName, symbol(当前代码), timeZoneFullName, timeZoneShortName, underlyingSymbol(原始代码), 
    """
    try:
        adict=stock.quote_type
    except:
        print("  #Error(stock_info): failed to get quote type of",symbol)
        return None    
    keylist=list(adict[symbol].keys())
    aframe=pd.DataFrame.from_dict(adict, orient='index', columns=keylist)
    ainfo=aframe.T
    info=pd.concat([info,ainfo]) 
    

    """
    Share Purchase Activity
    period(6m), totalInsiderShares
    """
    try:
        adict=stock.share_purchase_activity
    except:
        print("  #Error(stock_info): failed to get share purchase of",symbol)
        return None    
    keylist=list(adict[symbol].keys())
    aframe=pd.DataFrame.from_dict(adict, orient='index', columns=keylist)
    ainfo=aframe.T
    info=pd.concat([info,ainfo]) 


    """
    # Summary detail
    averageDailyVolume10Day, averageVolume, averageVolume10days, beta, currency, 
    dayHigh, dayLow, fiftyDayAverage, fiftyTwoWeekHigh, fiftyTwoWeekLow, open, previousClose, 
    regularMarketDayHigh, regularMarketDayLow, regularMarketOpen, regularMarketPreviousClose, 
    regularMarketVolume, twoHundredDayAverage, volume, 
    forwardPE, marketCap, priceToSalesTrailing12Months, 
    dividendRate, dividendYield, exDividendDate, payoutRatio, trailingAnnualDividendRate,
    trailingAnnualDividendYield, trailingPE, 
    """
    try:
        adict=stock.summary_detail
    except:
        print("  #Error(stock_info): failed to get summary detail of",symbol)
        return None    
    keylist=list(adict[symbol].keys())
    aframe=pd.DataFrame.from_dict(adict, orient='index', columns=keylist)
    ainfo=aframe.T
    info=pd.concat([info,ainfo]) 

    
    """
    summary_profile
    address/city/country/zip, phone/fax, sector/industry, website/longBusinessSummary, 
    fullTimeEmployees, 
    """
    try:
        adict=stock.summary_profile
    except:
        print("  #Error(stock_info): failed to get summary profile of",symbol)
        print("  Possible reasons:","\n  1.Wrong stock code","\n  2.Instable data source, try later")
        return None    
    keylist=list(adict[symbol].keys())
    aframe=pd.DataFrame.from_dict(adict, orient='index', columns=keylist)
    ainfo=aframe.T
    info=pd.concat([info,ainfo]) 
    

    # 清洗数据项目
    info.sort_index(inplace=True)   #排序
    info.dropna(inplace=True)   #去掉空值
    #去重
    info['Item']=info.index
    info.drop_duplicates(subset=['Item'],keep='last',inplace=True)
    
    #删除不需要的项目
    delrows=['adult','alcoholic','animalTesting','ask','askSize','bid','bidSize', \
             'catholic','coal','controversialWeapons','furLeather','gambling', \
                 'gmo','gmtOffSetMilliseconds','militaryContract','messageBoardId', \
                     'nuclear','palmOil','pesticides','tobacco','uuid','maxAge']
    for r in delrows:
       info.drop(info[info['Item']==r].index,inplace=True) 
    
    #修改列名
    info.rename(columns={symbol:'Value'}, inplace=True) 
    del info['Item']
    
    return info


if __name__=='__main__':
    info=stock_info('AAPL')
    info=stock_info('BABA')

#==============================================================================
if __name__=='__main__':
    info=stock_info('AAPL')

def stock_basic(info):
    
    wishlist=['sector','industry', \
              #公司地址，网站
              'address1','address2','city','state','country','zip','phone','fax', \
              'website', \
              
              #员工人数
              'fullTimeEmployees', \
              
              #上市与交易所
              'exchangeName', \
              
              #其他
              'currency']
        
    #按照wishlist的顺序从info中取值
    rowlist=list(info.index)
    import pandas as pd
    info_sub=pd.DataFrame(columns=['Item','Value'])
    infot=info.T
    for w in wishlist:
        if w in rowlist:
            v=infot[w][0]
            s=pd.Series({'Item':w,'Value':v})
            info_sub=info_sub.append(s,ignore_index=True) 
    
    return info_sub

if __name__=='__main__':
    basic=stock_basic(info)    

#==============================================================================
if __name__=='__main__':
    info=stock_info('AAPL')

def stock_officers(info):
    
    wishlist=['sector','industry','currency', \
              #公司高管
              'companyOfficers', \
              ]
        
    #按照wishlist的顺序从info中取值
    rowlist=list(info.index)
    import pandas as pd
    info_sub=pd.DataFrame(columns=['Item','Value'])
    infot=info.T
    for w in wishlist:
        if w in rowlist:
            v=infot[w][0]
            s=pd.Series({'Item':w,'Value':v})
            info_sub=info_sub.append(s,ignore_index=True) 
    
    return info_sub

if __name__=='__main__':
    sub_info=stock_officers(info)    

#==============================================================================
def stock_risk_general(info):
    
    wishlist=['sector','industry', \
              
              'overallRisk','boardRisk','compensationRisk', \
              'shareHolderRightsRisk','auditRisk'
              ]
        
    #按照wishlist的顺序从info中取值
    rowlist=list(info.index)
    import pandas as pd
    info_sub=pd.DataFrame(columns=['Item','Value'])
    infot=info.T
    for w in wishlist:
        if w in rowlist:
            v=infot[w][0]
            s=pd.Series({'Item':w,'Value':v})
            info_sub=info_sub.append(s,ignore_index=True) 
    
    return info_sub

if __name__=='__main__':
    risk_general=stock_risk_general(info)    

#==============================================================================
def stock_risk_esg(info):
    
    wishlist=[
              'peerGroup','peerCount','percentile','esgPerformance', \
              'totalEsg','peerEsgScorePerformance', \
              'environmentScore','peerEnvironmentPerformance', \
              'socialScore','peerSocialPerformance','relatedControversy', \
              'governanceScore','peerGovernancePerformance'
              ]
        
    #按照wishlist的顺序从info中取值
    rowlist=list(info.index)
    import pandas as pd
    info_sub=pd.DataFrame(columns=['Item','Value'])
    infot=info.T
    for w in wishlist:
        if w in rowlist:
            v=infot[w][0]
            s=pd.Series({'Item':w,'Value':v})
            info_sub=info_sub.append(s,ignore_index=True) 
    
    return info_sub

if __name__=='__main__':
    risk_esg=stock_risk_esg(info)  
    
#==============================================================================
def stock_fin_rates(info):
    
    wishlist=['financialCurrency', \
              
              #偿债能力
              'currentRatio','quickRatio','debtToEquity', \
                  
              #盈利能力
              'ebitdaMargins','operatingMargins','grossMargins','profitMargins', \
                  
              #股东回报率
              'returnOnAssets','returnOnEquity', \
              'dividendRate','trailingAnnualDividendRate','trailingEps', \
              'payoutRatio','revenuePerShare','totalCashPerShare', \
              
              #业务发展能力
              'revenueGrowth','earningsGrowth','earningsQuarterlyGrowth'
              ]
        
    #按照wishlist的顺序从info中取值
    rowlist=list(info.index)
    import pandas as pd
    info_sub=pd.DataFrame(columns=['Item','Value'])
    infot=info.T
    for w in wishlist:
        if w in rowlist:
            v=infot[w][0]
            s=pd.Series({'Item':w,'Value':v})
            info_sub=info_sub.append(s,ignore_index=True) 
    
    return info_sub

if __name__=='__main__':
    fin_rates=stock_fin_rates(info) 

#==============================================================================
def stock_fin_statements(info):
    
    wishlist=['financialCurrency','lastFiscalYearEnd','mostRecentQuarter','nextFiscalYearEnd', \
              
              #资产负债
              'marketCap','enterpriseValue','totalDebt', \
                  
              #利润表
              'totalRevenue','grossProfits','ebitda','netIncomeToCommon', \
                  
              #现金流量
              'operatingCashflow','freeCashflow','totalCash', \
              
              #股票数量
              'sharesOutstanding','totalInsiderShares'
              ]

    datelist=['lastFiscalYearEnd','mostRecentQuarter','nextFiscalYearEnd']
        
    #按照wishlist的顺序从info中取值
    rowlist=list(info.index)
    import pandas as pd
    info_sub=pd.DataFrame(columns=['Item','Value'])
    infot=info.T
    for w in wishlist:
        if w in rowlist:
            if not (w in datelist):
                v=infot[w][0]
            else:
                v=infot[w][0][0:10]
                
            s=pd.Series({'Item':w,'Value':v})
            info_sub=info_sub.append(s,ignore_index=True) 
    
    return info_sub

if __name__=='__main__':
    fin_statements=stock_fin_statements(info) 

#==============================================================================
def stock_market_rates(info):
    
    wishlist=['beta','currency', \
              
              #市场观察
              'priceToBook','priceToSalesTrailing12Months', \
              
              #市场风险与收益
              '52WeekChange','SandP52WeekChange', \
              'trailingEps','forwardEps','trailingPE','forwardPE','pegRatio', \
              
              #分红
              'dividendYield', \
                  
              #持股
              'heldPercentInsiders','heldPercentInstitutions', \
              
              #股票流通
              'sharesOutstanding','currentPrice','recommendationKey']
        
    #按照wishlist的顺序从info中取值
    rowlist=list(info.index)
    import pandas as pd
    info_sub=pd.DataFrame(columns=['Item','Value'])
    infot=info.T
    for w in wishlist:
        if w in rowlist:
            v=infot[w][0]
            s=pd.Series({'Item':w,'Value':v})
            info_sub=info_sub.append(s,ignore_index=True) 
    
    return info_sub

if __name__=='__main__':
    market_rates=stock_market_rates(info) 

#==============================================================================
if __name__=='__main__':
    ticker='AAPL'
    info_type='fin_rates' 

    ticker='FIBI.TA'
    info_type='officers' 

def get_stock_profile(ticker,info_type='basic',graph=True):
    """
    功能：抓取和获得股票的信息
    basic: 基本信息
    fin_rates: 财务比率快照
    fin_statements: 财务报表快照
    market_rates: 市场比率快照
    risk_general: 一般风险快照
    risk_esg: 可持续发展风险快照（有些股票无此信息）
    """
    #print("\nSearching for snapshot info of",ticker,"\b, please wait...")

    typelist=['basic','officers','fin_rates','fin_statements','market_rates','risk_general','risk_esg','all']    
    if info_type not in typelist:
        print("  #Sorry, info_type not supported for",info_type)
        print("  Supported info_type:\n",typelist)
        return None
    
    #应对各种出错情形：执行出错，返回NoneType，返回空值
    try:
        info=stock_info(ticker)
    except:
        print("  #Warning(get_stock_profile): failed to retrieve info of",ticker,"\b, recovering...")
        import time; time.sleep(5)
        try:
            info=stock_info(ticker)
        except:
            print("  #Error(get_stock_profile): failed to retrieve info of",ticker)
            return None
    if info is None:
        print("  #Error(get_stock_profile): retrieved none info of",ticker)
        return None
    if len(info) == 0:
        print("  #Error(get_stock_profile): retrieved empty info of",ticker)
        return None    
    """
    #处理公司短名字    
    name0=info.T['shortName'][0]
    name1=name0.split('.',1)[0] #仅取第一个符号.以前的字符串
    name2=name1.split(',',1)[0] #仅取第一个符号,以前的字符串
    name3=name2.split('(',1)[0] #仅取第一个符号(以前的字符串
    #name4=name3.split(' ',1)[0] #仅取第一个空格以前的字符串
    #name=codetranslate(name4)  #去掉空格有名字错乱风险
    name9=name3.strip()
    name=codetranslate(name9)   #从短名字翻译
    """
    if not graph: return info
    
    name=codetranslate(ticker)  #从股票代码直接翻译
    if info_type in ['basic','all']:
        sub_info=stock_basic(info)
        titletxt="===== "+name+": "+texttranslate("公司基本信息")+" =====\n"        
        printdf(sub_info,titletxt)
    
    if info_type in ['officers','all']:
        sub_info=stock_officers(info)
        titletxt="===== "+name+": "+texttranslate("公司高管信息")+" =====\n"        
        printdf(sub_info,titletxt)    
    
    if info_type in ['fin_rates','all']:
        sub_info=stock_fin_rates(info)
        titletxt="=== "+name+": "+texttranslate("基本财务比率TTM")+" ===\n"        
        printdf(sub_info,titletxt)
    
    if info_type in ['fin_statements','all']:
        sub_info=stock_fin_statements(info)
        titletxt="===== "+name+": "+texttranslate("财报主要项目")+" =====\n"        
        printdf(sub_info,titletxt)
    
    if info_type in ['market_rates','all']:
        sub_info=stock_market_rates(info)
        titletxt="===== "+name+": "+texttranslate("基本市场比率")+" =====\n"        
        printdf(sub_info,titletxt)
    
    if info_type in ['risk_general','all']:
        sub_info=stock_risk_general(info)
        titletxt="===== "+name+": "+texttranslate("一般风险指数")+" ====="+ \
            "\n"+texttranslate("(指数越小风险越低)")+"\n"
        printdf(sub_info,titletxt)
    
    if info_type in ['risk_esg','all']:
        sub_info=stock_risk_esg(info)
        if len(sub_info)==0:
            print("  #Error(get_stock_profile): esg info not available for",ticker)
        else:
            titletxt="===== "+name+": "+texttranslate("可持续发展风险")+" ====="+ \
                     "\n"+texttranslate("(分数越小风险越低)")+"\n"
            printdf(sub_info,titletxt)
    
    return info

if __name__=='__main__':
    info=get_stock_profile(ticker,info_type='basic')
    info=get_stock_profile(ticker,info_type='officers')
    info=get_stock_profile(ticker,info_type='fin_rates')
    info=get_stock_profile(ticker,info_type='fin_statements')
    info=get_stock_profile(ticker,info_type='market_rates')
    info=get_stock_profile(ticker,info_type='risk_general')
    info=get_stock_profile(ticker,info_type='risk_esg')

#==============================================================================
if __name__=='__main__':
    ticker='AAPL'
    info=stock_info(ticker)
    sub_info=stock_basic(info)
    titletxt="===== "+ticker+": Snr Management ====="

def printdf(sub_info,titletxt):
    """
    功能：整齐显示股票信息快照，翻译中文，按照中文项目长度计算空格数
    """
    print("\n"+titletxt)

    for index,row in sub_info.iterrows():
        
        #----------------------------------------------------------------------
        #特殊打印：高管信息
        if row['Item']=="companyOfficers":
            print_companyOfficers(sub_info)
            continue
        
        #特殊打印：ESG同行状况
        peerlist=["peerEsgScorePerformance","peerEnvironmentPerformance", \
                 "peerSocialPerformance","peerGovernancePerformance"]
        if row['Item'] in peerlist:
            print_peerPerformance(sub_info,row['Item'])
            continue

        #特殊打印：ESG Social风险内容
        if row['Item']=="relatedControversy":
            print_controversy(sub_info,row['Item'])
            continue
        #----------------------------------------------------------------------

        print_item(row['Item'],row['Value'],10)
    
    import datetime; today=datetime.date.today()
    lang=check_language()
    if lang == 'Chinese':
        print(texttranslate("\n***数据来源: 雅虎财经,"),today)
    else:
        print(texttranslate("\n***Source: Yahoo Finance,"),today)
    
    return

if __name__=='__main__':
    printdf(sub_info,titletxt)

#==============================================================================
if __name__=='__main__':
    item='currentPrice'
    value='110.08'
    maxlen=10
    
def print_item(item,value,maxlen):
    """
    功能：打印一个项目和相应的值，中间隔开一定空间对齐
    限制：只区分字符串、整数和浮点数
    """
    DEBUG=False
    
    print(ectranslate(item)+': ',end='')
    
    directprint=['zip','ratingYear','ratingMonth']
    if item in directprint:
        if DEBUG: print("...Direct print")
        print(value)
        return
    
    #是否整数
    if isinstance(value,int):
        if DEBUG: print("...Integer: ",end='')
        if value != 0:
            print(format(value,','))
        else:
            print('-')
        return
    
    #是否浮点数
    ZERO=0.00001
    if isinstance(value,float):
        if DEBUG: print("...Float: ",end='')
        if value < 1.0: 
            value1=round(value,4)
        else:
            value1=round(value,2)
        if value <= -ZERO or value >= ZERO:
            print(format(value1,','))
        else:
            print('-')
        return  
    
    #是否字符串
    if not isinstance(value,str):
        print(str(value))
    
    #是否字符串表示的整数
    if value.isdigit():
        value1=int(value)
        if DEBUG: print("...Integer in string: ",end='')
        if value1 != 0:
            print(format(value1,','))
        else:
            print('-')
        return          
    
    #是否字符串表示的浮点数
    try:
        value1=float(value)
        if value1 < 1.0:
            value2=round(value1,4)
        else:
            value2=round(value1,2)
        if DEBUG: print("...Float in string")
        if value1 <= -ZERO or value1 >= ZERO:
            print(format(value2,','))
        else:
            print('-')
    except:
        #只是字符串
        if DEBUG: print("...String")
        print(value)       
    
    return

if __name__=='__main__':
    print_item('currentPrice','110.08',10)
    
#==============================================================================
if __name__=='__main__':
    str1='哈哈哈ROA1'

def str_len(str1):
    """
    功能：计算中英文混合字符串的实际占位长度，不太准
    """
    len_d=len(str1)
    len_u=len(str1.encode('utf_8'))
    
    num_ch=(len_u - len_d)/2
    num_en=len_d - num_ch    
    totallen=int(num_ch*2 + num_en)
    
    return totallen

if __name__=='__main__':
    str_len('哈哈哈ROA1')

#==============================================================================
if __name__=='__main__':
    info=stock_info('AAPL')
    sub_info=stock_officers(info)

def print_companyOfficers(sub_info):
    """
    功能：打印公司高管信息
    """
    item='companyOfficers'
    itemtxt=texttranslate('公司高管:')
    key1='name'
    key2='title'
    key3='yearBorn'
    key4='age'
    
    key6='totalPay'
    key7='fiscalYear'
    currency=list(sub_info[sub_info['Item'] == 'currency']['Value'])[0]
    alist=list(sub_info[sub_info['Item'] == item]['Value'])[0]
    
    print(itemtxt)
    if len(alist)==0:
        print("  #Warning(print_companyOfficers): company officer info not available")
    
    import datetime as dt; today=dt.date.today()
    thisyear=int(str(today)[:4])
    for i in alist:
        
        #测试是否存在：姓名，职位，出生年份
        try:
            ikey1=i[key1]
            ikey2=i[key2]
            ikey3=i[key3]
        except:
            continue
        ikey4=thisyear-ikey3
        print(' '*4,ikey1)    
        print(' '*8,ikey2,'\b,',ikey4,texttranslate('\b岁 (生于')+str(ikey3)+')')    
        
        #测试是否存在：薪酬信息
        try:
            ikey6=i[key6]
            ikey7=i[key7]
            if ikey6 > 0:
                print(' '*8,texttranslate('总薪酬'),currency+str(format(ikey6,',')),'@'+str(ikey7))
        except:
            continue
    return

if __name__=='__main__':
    print_companyOfficers(sub_info)

#==============================================================================
if __name__=='__main__':
    info=stock_info('AAPL')
    sub_info=stock_risk_esg(info)
    item="peerEsgScorePerformance"

def print_peerPerformance(sub_info,item):
    """
    功能：打印ESG信息
    """
    
    key1='min'
    key2='avg'
    key3='max'
    i=list(sub_info[sub_info['Item'] == item]['Value'])[0]
    
    """
    print(ectranslate(item)+':')
    print(' '*4,key1+':',i[key1],'\b,',key2+':',round(i[key2],2),'\b,',key3+':',i[key3])
    """
    print(ectranslate(item)+': ',end='')
    print(texttranslate("均值")+str(round(i[key2],2)),end='')
    print(" ("+str(i[key1])+'-'+str(i[key3])+")")
    
    return

if __name__=='__main__':
    print_peerPerformance(sub_info,item)

#==============================================================================
if __name__=='__main__':
    info=stock_info('AAPL')
    sub_info=stock_risk_esg(info)
    item='relatedControversy'

def print_controversy(sub_info,item):
    """
    功能：打印ESG Social风险内容
    """
    alist=list(sub_info[sub_info['Item'] == item]['Value'])[0]
    if len(alist)==0:
        print("  #Error(print_controversy): no relevant info found.")    
    
    print(ectranslate(item)+':')
    for i in alist:
        print(' '*4,ectranslate(i))
        
    return

if __name__=='__main__':
    print_controversy(sub_info,item)

#==============================================================================
if __name__ =="__main__":
    stocklist=["BAC", "TD","PNC"]
    
def get_esg2(stocklist):
    """
    功能：根据股票代码列表，抓取企业最新的可持续性发展ESG数据
    输入参数：
    stocklist：股票代码列表，例如单个股票["AAPL"], 多只股票["AAPL","MSFT","GOOG"]
    输出参数：    
    企业最新的可持续性发展ESG数据，数据框
    """
    
    import pandas as pd
    collist=['symbol','totalEsg','environmentScore','socialScore','governanceScore']
    sust=pd.DataFrame(columns=collist)
    for t in stocklist:
        try:
            info=stock_info(t).T
        except:
            print("  #Error(get_esg2): esg info not available for",t)
            continue
        if (info is None) or (len(info)==0):
            print("  #Error(get_esg2): failed to get esg info for",t)
            continue
        sub=info[collist]
        sust=pd.concat([sust,sub])
    
    newcols=['Stock','ESGscore','EPscore','CSRscore','CGscore']
    sust.columns=newcols
    """
    sust=sust.rename(columns={'symbol':'Stock','totalEsg':'ESGscore', \
                         'environmentScore':'EPscore', \
                             'socialScore':'CSRscore', \
                                 'governanceScore':'CGscore'})
    """
    sust.set_index('Stock',inplace=True)
    
    return sust

if __name__ =="__main__":
    sust=get_esg2(stocklist)

#==============================================================================
#==============================================================================
def portfolio_esg2(portfolio):
    """
    功能：抓取、打印和绘图投资组合portfolio的可持续性发展数据，演示用
    输入参数：
    企业最新的可持续性发展数据，数据框    
    """
    #解构投资组合
    _,_,stocklist,_=decompose_portfolio(portfolio)
    
    #抓取数据
    try:
        sust=get_esg2(stocklist)
    except:
        print("  #Error(portfolio_esg): fail to get ESG data for",stocklist)
        return None
    if sust is None:
        #print("#Error(portfolio_esg), fail to get ESG data for",stocklist)
        return None
        
    #处理小数点
    from pandas.api.types import is_numeric_dtype
    cols=list(sust)    
    for c in cols:
        if is_numeric_dtype(sust[c]):
            sust[c]=round(sust[c],2)        
            
    #显示结果
    print(texttranslate("\n===== 投资组合的可持续发展风险 ====="))
    print(texttranslate("投资组合:"),stocklist)
    #显示各个成分股的ESG分数
    sust['Stock']=sust.index
    esgdf=sust[['Stock','ESGscore','EPscore','CSRscore','CGscore']]
    print(esgdf.to_string(index=False))
    
    print("\n"+texttranslate("ESG评估分数:"))
    #木桶短板：EPScore
    esg_ep=esgdf.sort_values(['EPscore'], ascending = True)
    p_ep=esg_ep['EPscore'][-1]
    p_ep_stock=esg_ep.index[-1]   
    str_ep=texttranslate("   EP分数(基于")+str(p_ep_stock)+codetranslate(str(p_ep_stock))+")"
    len_ep=hzlen(str_ep)

    #木桶短板：CSRScore
    esg_csr=esgdf.sort_values(['CSRscore'], ascending = True)
    p_csr=esg_csr['CSRscore'][-1]
    p_csr_stock=esg_csr.index[-1] 
    str_csr=texttranslate("   CSR分数(基于")+str(p_csr_stock)+codetranslate(str(p_csr_stock))+")"
    len_csr=hzlen(str_csr)
    
    #木桶短板：CGScore
    esg_cg=esgdf.sort_values(['CGscore'], ascending = True)
    p_cg=esg_cg['CGscore'][-1]
    p_cg_stock=esg_cg.index[-1]     
    str_cg=texttranslate("   CG分数(基于")+str(p_cg_stock)+codetranslate(str(p_cg_stock))+")"
    len_cg=hzlen(str_cg)

    str_esg=texttranslate("   ESG总评分数")
    len_esg=hzlen(str_esg)
    
    #计算对齐冒号中间需要的空格数目
    len_max=max(len_ep,len_csr,len_cg,len_esg)
    str_ep=str_ep+' '*(len_max-len_ep+1)+':'
    str_csr=str_csr+' '*(len_max-len_csr+1)+':'
    str_cg=str_cg+' '*(len_max-len_cg+1)+':'
    str_esg=str_esg+' '*(len_max-len_esg+1)+':'
    
    #对齐打印
    print(str_ep,p_ep)
    print(str_csr,p_csr)    
    print(str_cg,p_cg)      
    #计算投资组合的ESG综合风险
    p_esg=round(p_ep+p_csr+p_cg,2)
    print(str_esg,p_esg)

    import datetime as dt; today=dt.date.today()
    footnote=texttranslate("注：分数越高, 风险越高.")+"\n"+texttranslate("数据来源：雅虎，")+str(today)
    print(footnote)
    
    return p_esg

if __name__ =="__main__":
    #market={'Market':('China','^HSI')}
    market={'Market':('US','^GSPC')}
    #stocks={'0939.HK':2,'1398.HK':1,'3988.HK':3}
    stocks={'VIPS':3,'JD':2,'BABA':1}
    portfolio=dict(market,**stocks)
    esg=portfolio_esg(portfolio)
#==============================================================================

#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================   
def fix_mac_hanzi_plt():
    """
    功能：修复MacOSX中matplotlib绘图时汉字的乱码问题，安装SimHei.ttf字体
    注意：本函数未经测试，弃用
    """
    #判断当前的操作系统
    import platform
    pltf=platform.platform()
    os=pltf[0:5]    
    if not (os == "macOS"):
        print("#Warning(fix_mac_hanzi_plt): This command is only valid for MacOSX.")    
        return

    #查找模块的安装路径
    import os
    import imp
    dir1=imp.find_module('siat')[1]        
    dir2=imp.find_module('matplotlib')[1]

    #查找matplotlib的字体地址
    pltttf=dir2+'/mpl-data/fonts/ttf'    

    #复制字体文件
    cpcmd="cp -r "+dir1+"/SimHei.ttf "+pltttf
    result=os.popen(cpcmd)    

    #修改配置文件内容
    import matplotlib
    pltrc=matplotlib.matplotlib_fname()

    line1='\nfont.family : sans-serif\n'
    line2='font.sans-serif : SimHei,DejaVu Sans,Bitstream Vera Sans,Lucida Grande,Verdana,Geneva,Lucid,Arial,Helvetica,Avant Garde,sans-serif\n'
    line3='axes.unicode_minus : False\n'

    filehandler=open(pltrc,'a')
    filehandler.write(line1)
    filehandler.write(line2)
    filehandler.write(line3)
    filehandler.close()

    from matplotlib.font_manager import _rebuild
    _rebuild()
    print("  Fixed Mac Hanzi problems for matplotlib graphics!")
    print("  Please RESTART Python kernel to make it effective!")
    
    return



















