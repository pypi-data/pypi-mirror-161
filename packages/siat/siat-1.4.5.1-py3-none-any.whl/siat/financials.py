# -*- coding: utf-8 -*-
"""
本模块功能：计算财务报表比例，应用层
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2020年9月8日
最新修订日期：2020年9月15日
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
#==============================================================================
#本模块的公共引用
from siat.common import *
from siat.translate import *
from siat.financial_statements import *
from siat.grafix import *
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

#设置绘图风格：网格虚线
plt.rcParams['axes.grid']=True
plt.rcParams['grid.color']='steelblue'
plt.rcParams['grid.linestyle']='dashed'
plt.rcParams['grid.linewidth']=0.5
plt.rcParams['axes.facecolor']='whitesmoke'

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
if __name__ == '__main__':
    tickers=['AAPL','MSFT']
    items=['Current Ratio','Quick Ratio']
    datatag=False
    power=0
    zeroline=False
    twinx=False

def compare_history(tickers,items, \
                    datatag=False,power=0,zeroline=False,twinx=False, \
                        loc1='best',loc2='best'):
    """
    功能：比较多个股票的时序数据，绘制折线图
    datatag=False: 不将数值标记在图形旁
    zeroline=False：不绘制水平零线
    twinx=False：单纵轴
    """
    #检查power的范围是否合理
    if not (power in range(0,10)):
        print("  #Error(compare_history): invalid parameter, power =",power)
        return None
    
    #检查股票个数
    ticker_num=1
    if isinstance(tickers,list): 
        if len(tickers) >= 1: ticker1=tickers[0]
        if len(tickers) >= 2: 
            ticker2=tickers[1]
            ticker_num=2
        if len(tickers) == 0: 
            print("  #Error(): no stock code found",tickers)
            return None,None
    else:
        ticker1=tickers

    #检查指标个数
    item_num=1
    if isinstance(items,list): 
        if len(items) >= 1: item1=items[0]
        if len(items) >= 2: 
            item2=items[1]
            item_num=2
        if len(items) == 0: 
            print("  #Error(): no analytical item found",items)
            return None,None
    else:
        item1=items
    
    #判断比较模式
    if (ticker_num == 1) and (item_num == 1): mode='T1I1'
    if (ticker_num == 1) and (item_num == 2): mode='T1I2'
    if (ticker_num == 2): mode='T2I1'
    
    #检查指标是否支持
    itemlist=[
        #短期偿债能力
        'Current Ratio','Quick Ratio','Cash Ratio','Cash Flow Ratio', \
        #长期偿债能力
        'Debt to Asset','Equity to Asset','Equity Multiplier','Debt to Equity', \
        'Debt to Tangible Net Asset','Debt Service Coverage','Times Interest Earned', \
        #营运能力
        'Inventory Turnover','Receivable Turnover','Current Asset Turnover', \
        'Fixed Asset Turnover','Total Asset Turnover', \
        #盈利能力
        'Operating Margin','Gross Margin','Profit Margin', \
        'Net Profit on Costs','ROA','ROIC','ROE', \
        #股东持股
        'Payout Ratio','Cashflow per Share','CFPS','Dividend per Share','DPS', \
        'Net Asset per Share','BasicEPS','DilutedEPS', \
        #发展潜力
        'Revenue Growth','Capital Accumulation','Total Asset Growth','PPE Residual' \
        ]
    
    if item1 not in itemlist:
        print("  #Error(compare_history): unsupported item for",item1)
        print("  Supported items are as follows:\n",itemlist)
        return None,None    
    if mode=='T1I2':
        if item2 not in itemlist:
            print("  #Error(compare_history): unsupported item for",item2)
            print("  Supported items are as follows:\n",itemlist)
            return None,None    
    
    #抓取数据
    info1=get_financial_rates(ticker1)
    if info1 is None:
        print("  #Error(compare_history): failed to retrieved info for",ticker1)
        return None,None
    
    cols1=['ticker','endDate','periodType',item1]
    df1=info1[cols1]
    df1['date']=df1['endDate']
    df1.set_index('date',inplace=True)    
    
    if mode == 'T1I2':
        ticker2=ticker1
        cols2=['ticker','endDate','periodType',item2]
        df2=info1[cols2]
        df2['date']=df2['endDate']
        df2.set_index('date',inplace=True)           
    
    if mode == 'T2I1':
        item2=item1
        info2=get_financial_rates(ticker2)
        if info2 is None:
            print("  #Error(compare_history): failed to retrieved info for",ticker2)
            return None,None        
        
        df2=info2[cols1]
        df2['date']=df2['endDate']
        df2.set_index('date',inplace=True)           

    import datetime; today=datetime.date.today()
    #绘图：T1I1，单折线
    if mode == 'T1I1':
        df=df1
        colname=item1
        collabel=ectranslate(item1)
        ylabeltxt=''
        titletxt=codetranslate(ticker1)+texttranslate(": 基于年(季)报的业绩历史")
        footnote=texttranslate("数据来源: 雅虎财经,")+' '+str(today)
        
        plot_line(df,colname,collabel,ylabeltxt,titletxt,footnote, \
                  datatag=datatag,power=power,zeroline=zeroline,resample_freq='3M', \
                      loc=loc1)
        return df1,None

    #绘图：T1I2，单股票双折线
    if mode == 'T1I2':
        colname1=item1
        label1=ectranslate(item1)
        colname2=item2
        label2=ectranslate(item2)
        ylabeltxt=''
        titletxt=codetranslate(ticker1)+texttranslate(": 基于年(季)报的业绩历史对比")
        footnote=texttranslate("数据来源: 雅虎财经,")+' '+str(today)
        
        plot_line2(df1,ticker1,colname1,label1, \
               df2,ticker2,colname2,label2, \
               ylabeltxt,titletxt,footnote, \
               power=power,zeroline=zeroline,twinx=twinx,resample_freq='3M', \
                   loc1=loc1,loc2=loc2)
        return df1,df2

    #绘图：T2I1，双股票双折线
    if mode == 'T2I1':
        df1=df1.fillna(method='ffill').fillna(method='bfill')
        df2=df2.fillna(method='ffill').fillna(method='bfill')
        """
        #日期可能不一致，并表
        import pandas as pd
        df=pd.merge(df1,df2,how="outer",on="endDate")
        #df=df.fillna(method='ffill').fillna(method='bfill')
        df.dropna(inplace=True)
        dfx=df[['ticker_x','endDate','periodType_x',item1+'_x']]
        dfx=dfx.rename(columns={'ticker_x':'ticker','periodType_x':'periodType',item1+'_x':item1})
        dfx['date']=dfx['endDate']
        dfx.set_index('date',inplace=True)
        
        dfy=df[['ticker_y','endDate','periodType_y',item1+'_y']]
        dfy=dfy.rename(columns={'ticker_y':'ticker','periodType_y':'periodType',item1+'_y':item1})
        dfy['date']=dfy['endDate']
        dfy.set_index('date',inplace=True)
        """
        
        colname1=item1
        label1=ectranslate(item1)
        colname2=item2
        label2=ectranslate(item2)
        ylabeltxt=''
        titletxt=codetranslate(ticker1)+" vs "+codetranslate(ticker2)+texttranslate(": 基于年(季)报的业绩历史对比")
        footnote=texttranslate("数据来源: 雅虎财经,")+' '+str(today)
        
        plot_line2(df1,ticker1,colname1,label1, \
               df2,ticker2,colname2,label2, \
               ylabeltxt,titletxt,footnote, \
               power=power,zeroline=zeroline,twinx=twinx,resample_freq='3M', \
                   loc1=loc1,loc2=loc2)    
    
        return df1,df2    
    
if __name__ == '__main__':
    df1,df2=compare_history(tickers,items)
    
#==============================================================================
if __name__ == '__main__':
    tickers=['AAPL','MSFT','WMT']
    itemk='Current Ratio'
    itemk='Employees'
    
    multicolor=False
    
    tickers=['AMZN','EBAY']
    itemk='IGR'
    datatag=True
    tag_offset=0.01
    graph=True
    axisamp=1.3
    
    
    itemk='IGR'

def compare_snapshot(tickers,itemk,datatag=True,tag_offset=0.01,graph=True,axisamp=1.2,multicolor=True):
    """
    功能：比较多个股票的快照数据，绘制水平柱状图
    itemk需要通过对照表转换为内部的item
    datatag=True: 将数值标记在图形旁
    tag_offset=0.01：标记的数值距离图形的距离，若不理想可以手动调节，可为最大值1%-5%
    """
    #检查股票代码列表
    if not isinstance(tickers,list): 
        print("  #Error(compare_snapshot): need more stock codes in",tickers)
        return None
    if len(tickers) < 2:
        print("  #Error(compare_snapshot): need more stock codes in",tickers)
        return None
    
    #检查指标
    if isinstance(itemk,list): 
        print("  #Error(compare_snapshot): only 1 item allowed here",itemk)
        return None    
    
    itemdict={
        #员工与ESG
        'Employees':'fullTimeEmployees', \
        'Total ESG':'totalEsg','Environment Score':'environmentScore', \
        'Social Score':'socialScore','Governance Score':'governanceScore', \
        #偿债能力
        'Current Ratio':'currentRatio','Quick Ratio':'quickRatio', \
        'Debt to Equity':'debtToEquity', \
        #盈利能力
        'EBITDA Margin':'ebitdaMargins','Operating Margin':'operatingMargins', \
        'Gross Margin':'grossMargins','Profit Margin':'profitMargins', \
        'ROA':'returnOnAssets','ROE':'returnOnEquity', \
        #股东持股
        'Held Percent Insiders':'heldPercentInsiders', \
        'Held Percent Institutions':'heldPercentInstitutions', \
        #股东回报
        'Payout Ratio':'payoutRatio','Revenue per Share':'revenuePerShare', \
        'Cashflow per Share':'totalCashPerShare', \
        'Dividend Rate':'dividendRate','TTM Dividend Rate':'trailingAnnualDividendRate', \
        'Dividend Yield':'dividendYield', \
        'TTM Dividend Yield':'trailingAnnualDividendYield', \
        '5-Year Avg Dividend Yield':'fiveYearAvgDividendYield', \
        'Trailing EPS':'trailingEps','Forward EPS':'forwardEps', \
        #发展潜力
        'Revenue Growth':'revenueGrowth','Earnings Growth':'earningsGrowth', \
        'Earnings Quarterly Growth':'earningsQuarterlyGrowth', \
        'EV to Revenue':'enterpriseToRevenue','EV to EBITDA':'enterpriseToEbitda', \
        #市场看法
        'Current Price':'currentPrice','Price to Book':'priceToBook', \
        'TTM Price to Sales':'priceToSalesTrailing12Months', \
        'beta':'beta','52-Week Change':'52WeekChange', \
        'Trailing PE':'trailingPE','Forward PE':'forwardPE', \
        'PEG':'pegRatio',
        #'IGR':'IGR','SGR':'SGR',
        }
    itemlist=list(itemdict.keys())
    if itemk not in itemlist:
        print("  #Error(compare_snapshot): unsupported rate for",itemk)
        print("  Supported rates are as follows:\n",itemlist)
        return None

    item=itemdict[itemk]
    import pandas as pd
    df=pd.DataFrame(columns=('ticker','item','value','name'))
    proxydict={'trailingPE':'forwardPE','forwardPE':'trailingPE', \
               'trailingEps':'forwardEps','forwardEps':'trailingEps',}
    
    for t in tickers:
        try:
            info=stock_info(t)
        except:
            print("  #Error(compare_snapshot): stock info not available for",t)
            continue
        if (info is None) or (len(info)==0):
            print("  #Error(compare_snapshot): failed to get info for",t,"\b, try later!")
            continue
        try:
            value=info[info.index == item]['Value'][0]
        except:
            try:
                itemp=proxydict[item]
                value=info[info.index == itemp]['Value'][0]
                print("  #Warning(compare_snapshot):",item,"unavailable for",t,'\b, using proxy',itemp)
            except:
                print("  #Error(compare_snapshot): failed to get info of",item,"for",t)
                continue
            
        name=codetranslate(t)
        row=pd.Series({'ticker':t,'item':item,'value':value,'name':name})
        df=df.append(row,ignore_index=True)         
    
    if len(df) == 0:
        print("  #Error(compare_snapshot): stock info not found in",tickers)
        return None
    
    #处理小数点
    try:
        df['value']=round(df['value'],3)    
    except:
        pass
    df.sort_values(by='value',ascending=False,inplace=True)
    df['key']=df['name']
    df.set_index('key',inplace=True)    
    
    #绘图
    if graph:
        print("\n...Calculating and drawing graph, please wait ...")
        colname='value'
        
        lang=check_language()
        if lang == 'Chinese':
            titletxt="企业横向对比: 业绩快照"
            notestxt="注：若是财务指标，则为TTM数值\n"
        else:
            titletxt="Company Snapshot Comparison"
            notestxt="Note: TTM values for financial ratios\n"
            
        import datetime; today=datetime.date.today()
        footnote=ectranslate(itemk)+" -->\n"+notestxt+texttranslate("数据来源: 雅虎财经,")+' '+str(today)
        
        if multicolor:
            plot_barh(df,colname,titletxt,footnote,datatag=datatag,tag_offset=tag_offset,axisamp=axisamp)
        else:
            #在Spyder中可能无法显示
            plot_barh2(df,colname,titletxt,footnote)
    
    return df

if __name__ == '__main__':
    df=compare_snapshot(tickers,itemk)
    
#==============================================================================
def compare_snapshot2(tickers,itemk):
    """
    功能：比较多个股票的快照数据，绘制水平柱状图
    itemk需要通过对照表转换为内部的item
    """
    #检查股票代码列表
    if not isinstance(tickers,list): 
        print("  #Error(compare_snapshot2): need more stock codes in",tickers)
        return None
    if len(tickers) < 2:
        print("  #Error(compare_snapshot2): need more stock codes in",tickers)
        return None
    
    #检查指标
    if isinstance(itemk,list): 
        print("  #Error(compare_snapshot2): only 1 item allowed here",itemk)
        return None    
    
    itemdict={
        #员工与ESG
        'Employees':'fullTimeEmployees', \
        'Total ESG':'totalEsg','Environment Score':'environmentScore', \
        'Social Score':'socialScore','Governance Score':'governanceScore', \
        #偿债能力
        'Current Ratio':'currentRatio','Quick Ratio':'quickRatio', \
        'Debt to Equity':'debtToEquity', \
        #盈利能力
        'EBITDA Margin':'ebitdaMargins','Operating Margin':'operatingMargins', \
        'Gross Margin':'grossMargins','Profit Margin':'profitMargins', \
        'ROA':'returnOnAssets','ROE':'returnOnEquity', \
        #股东持股
        'Held Percent Insiders':'heldPercentInsiders', \
        'Held Percent Institutions':'heldPercentInstitutions', \
        #股东回报
        'Payout Ratio':'payoutRatio','Revenue per Share':'revenuePerShare', \
        'Cashflow per Share':'totalCashPerShare', \
        'Dividend Rate':'dividendRate','TTM Dividend Rate':'trailingAnnualDividendRate', \
        'Dividend Yield':'dividendYield', \
        'TTM Dividend Yield':'trailingAnnualDividendYield', \
        '5-Year Avg Dividend Yield':'fiveYearAvgDividendYield', \
        'Trailing EPS':'trailingEps','Forward EPS':'forwardEps', \
        #发展潜力
        'Revenue Growth':'revenueGrowth','Earnings Growth':'earningsGrowth', \
        'Earnings Quarterly Growth':'earningsQuarterlyGrowth', \
        'EV to Revenue':'enterpriseToRevenue','EV to EBITDA':'enterpriseToEbitda', \
        #市场看法
        'Current Price':'currentPrice','Price to Book':'priceToBook', \
        'TTM Price to Sales':'priceToSalesTrailing12Months', \
        'beta':'beta','52-Week Change':'52WeekChange', \
        'Trailing PE':'trailingPE','Forward PE':'forwardPE', \
        'PEG':'pegRatio',
        #'IGR':'IGR','SGR':'SGR'
        }
    itemlist=list(itemdict.keys())
    if itemk not in itemlist:
        print("  #Error(compare_snapshot): unsupported rate for",itemk)
        print("  Supported rates are as follows:\n",itemlist)
        return None

    item=itemdict[itemk]
    import pandas as pd
    #import siat.stock_base as sb
    df=pd.DataFrame(columns=('ticker','item','value','name'))
    for t in tickers:
        try:
            info=stock_info(t)
        except:
            print("  #Error(compare_snapshot): stock info not available for",t)
            continue
        if (info is None) or (len(info)==0):
            print("  #Error(compare_snapshot): failed to get info for",t,"\b, try later!")
            continue
        try:
            value=info[info.index == item]['Value'][0]
        except:
            print("  #Error(compare_snapshot): failed to get info of",item,"for",t)
            continue
        """
        name=info[info.index == 'shortName']['Value'][0]
        name1=name.split(' ',1)[0]  #取空格分隔字符串的第一个单词
        name2=name1.split(',',1)[0]
        name3=name2.split('.',1)[0]
        """
        name=codetranslate(t)
        row=pd.Series({'ticker':t,'item':item,'value':value,'name':name})
        df=df.append(row,ignore_index=True)         
    
    if len(df) == 0:
        print("  #Error(compare_snapshot): stock info not found in",tickers)
        return None
    
    #处理小数点
    try:
        df['value']=round(df['value'],3)    
    except:
        pass
    df.sort_values(by='value',ascending=False,inplace=True)
    df['key']=df['name']
    df.set_index('key',inplace=True)    
    
    #绘图
    print("...Calculating and drawing graph, please wait ...")
    colname='value'
    titletxt="企业横向对比: "+ectranslate(itemk)+"（TTM）"
    import datetime; today=datetime.date.today()
    footnote="数据来源: 雅虎财经, "+str(today)
    plot_barh2(df,colname,titletxt,footnote)
    
    return df

if __name__ == '__main__':
    df=compare_snapshot(tickers,itemk)
    
#==============================================================================

if __name__ == '__main__':
    tickers=["0883.HK","0857.HK","0386.HK",'XOM','2222.SR','OXY','BP','RDSA.AS']
    graph=True
    
def compare_tax(tickers,graph=True,axisamp=1.3):
    """
    功能：比较公司最新的实际所得税率
    """
    #检查股票代码列表
    if not isinstance(tickers,list): 
        print("  #Error(compare_tax): need more stock codes in",tickers)
        return None
    if len(tickers) < 2:
        print("  #Error(compare_tax): need more stock codes in",tickers)
        return None 
    
    import siat.beta_adjustment as badj
    import pandas as pd
    df=pd.DataFrame(columns=('ticker','name','date','tax rate%'))
    for t in tickers:
        try:
            df0=badj.prepare_hamada_yahoo(t)
        except:
            print("  #Warning(compare_tax): stock info not available for",t)
            continue
        df1=df0.tail(1)
        name=codetranslate(t)
        reportdate=df1.index[0]
        taxrate=df1['tax rate'][0]
        row=pd.Series({'ticker':t,'name':name,'date':reportdate,'tax rate%':round(taxrate*100,2)})
        df=df.append(row,ignore_index=True)        
    
    df.sort_values(by='tax rate%',ascending=False,inplace=True)
    df['key']=df['name']
    df.set_index('key',inplace=True)      
    #绘图
    if graph:
        print("...Calculating and drawing graph, please wait ...")
        lang=check_language()
        colname='tax rate%'
        if lang == 'Chinese':
            titletxt="企业横向对比: 平均税率"
            itemk="实际所得税率%"
            source_txt="数据来源: 雅虎财经,"
        else:
            titletxt=texttranslate("企业横向对比: 实际税率")
            itemk=texttranslate("实际所得税率%")
            source_txt=texttranslate("数据来源: 雅虎财经,")
                
        import datetime; today=datetime.date.today()
        footnote=itemk+" -->\n"+ \
            source_txt+" "+str(today)
        plot_barh(df,colname,titletxt,footnote,axisamp=axisamp)   
        
    return df
#==============================================================================
if __name__ == '__main__':
   ticker='EBAY'
   
def calc_igr_sgr(ticker):

    
    import siat.stock as stk
    sub_info=stk.get_stock_profile(ticker,info_type='fin_rates',graph=False)
    """
    #应对各种出错情形：执行出错，返回NoneType，返回空值
    try:
        info=stk.stock_info(ticker)
    except:
        print("  #Warning(calc_igr_sgr): failed to retrieve info of",ticker,"\b, recovering...")
        import time; time.sleep(5)
        try:
            info=stock_info(ticker)
        except:
            print("  #Error(calc_igr_sgr): failed to retrieve info of",ticker)
            return None
    if info is None:
        print("  #Error(calc_igr_sgr): retrieved none info of",ticker)
        return None
    if len(info) == 0:
        print("  #Error(calc_igr_sgr): retrieved empty info of",ticker)
        return None    
    sub_info=stock_fin_rates(info)
    """
    if sub_info is None:
        return None,None
    
    roa=list(sub_info[sub_info.index=='returnOnAssets']['Value'])[0]
    roe=list(sub_info[sub_info.index=='returnOnEquity']['Value'])[0]
    try:
        b=1-list(sub_info[sub_info.index=='payoutRatio']['Value'])[0]
    except:
        b=1-0

    igr=round(roa*b/(1-roa*b),4)
    sgr=round(roe*b/(1-roe*b),4)
    
    return igr,sgr

def compare_igr_sgr(tickers,graph=True,axisamp=1.0):
    """
    功能：比较公司TTM的IGR和SGR
    """
    #检查股票代码列表
    if not isinstance(tickers,list): 
        print("  #Error(compare_igr_sgr): need more stock codes in",tickers)
        return None
    if len(tickers) < 2:
        print("  #Error(compare_igr_sgr): need more stock codes in",tickers)
        return None 
    
    import pandas as pd
    df=pd.DataFrame(columns=('ticker','name','date','IGR%','SGR%'))
    for t in tickers:
        try:
            igr,sgr=calc_igr_sgr(t)
        except:
            print("  #Warning(compare_igr_sgr): stock info not available for",t)
            continue
        if igr is None or sgr is None: 
            print("  #Warning(compare_igr_sgr): stock info not available for",t)
            continue
        name=codetranslate(t)
        row=pd.Series({'ticker':t,'name':name,'IGR%':round(igr*100,2),'SGR%':round(sgr*100,2)})
        df=df.append(row,ignore_index=True)        
    
    #绘制IGR
    df.sort_values(by='IGR%',ascending=False,inplace=True)
    df['key']=df['name']
    df.set_index('key',inplace=True)      
    #绘图
    lang=check_language()
    if graph:
        print("\n...Calculating and drawing graph, please wait ...")
        
        colname='IGR%'
        if lang == "Chinese":
            titletxt="企业横向对比: 内部增长率TTM"
            itemk="内部增长率(IGR)%"
            source_txt="数据来源: 雅虎财经,"
        else:
            titletxt="Company Internal Growth Rate (IGR TTM)"
            itemk="Internal growth rate %"
            source_txt="Source: Yahoo Finance,"
        
        import datetime; today=datetime.date.today()
        footnote=ectranslate(itemk)+" -->\n"+ \
                source_txt+" "+str(today)
            
        plot_barh(df,colname,titletxt,footnote,axisamp=axisamp)   
    
    #绘制SGR
    df.sort_values(by='SGR%',ascending=False,inplace=True)
    df['key']=df['name']
    df.set_index('key',inplace=True)      
    #绘图
    if graph:
        colname='SGR%'
        if lang == 'Chinese':
            titletxt="企业横向对比: 可持续增长率TTM"
            itemk="可持续增长率(SGR)%"
        else:
            titletxt="Company Sustainable Growth Rate (SGR TTM)"
            itemk="Sustainable growth rate%"
            
        footnote=ectranslate(itemk)+" -->\n"+ \
            source_txt+" "+str(today)
        plot_barh(df,colname,titletxt,footnote,axisamp=axisamp)   
        
    return df


#==============================================================================
if __name__ == '__main__':
    fsdf=get_financial_statements('AAPL')
    fst=fsdf.T  #查看科目名称更加方便

def get_PE(fsdf):
    """
    功能：计算PE
    """
    dateymd=lambda x:x.strftime('%Y-%m-%d') 
    fsdf['endDate']=fsdf['asOfDate'].apply(dateymd)
    
    #获得各个报表的日期范围，适当扩大日期范围以规避非交易日
    start=min(list(fsdf['endDate']))
    fromdate=date_adjust(start,adjust=-30)
    end=max(list(fsdf['endDate']))
    todate=date_adjust(end,adjust=30)

    #获取股价
    ticker=list(fsdf['ticker'])[0]
    import siat.security_prices as ssp
    prices=ssp.get_price(ticker, fromdate, todate)
    if prices is None:
        print("#Error(get_PE): retrieving stock price failed for",ticker,fromdate,todate,"\b, recovering...")
        import time; time.sleep(5)
        prices=ssp.get_price(ticker, fromdate, todate)
        if prices is None: 
            print("#Error(get_PE): failed retrieving stock price, retrying stopped")
            import numpy as np
            fsdf['BasicPE']=np.nan
            fsdf['DilutedPE']=np.nan
            return fsdf
    
    prices['datedt']=prices.index.date
    datecvt=lambda x: str(x)[0:10]
    prices['Date']=prices['datedt'].apply(datecvt)

    #报表日期列表
    datelist_fs=list(fsdf['endDate'])
    #价格日期列表    
    datelist_price=list(prices['Date'])
    date_price_min=min(datelist_price)
    date_price_max=max(datelist_price)
    
    #股价列表
    pricelist=list(prices['Close'])
    
    import pandas as pd
    pricedf=pd.DataFrame(columns=('endDate','actualDate','Price'))
    for d in datelist_fs:
        found=False
        d1=d
        if d in datelist_price:
            found=True
            pos=datelist_price.index(d)
            p=pricelist[pos]
        else:
            while (d1 >= date_price_min) and not found:
                d1=date_adjust(d1,adjust=-1)
                if d1 in datelist_price:
                    found=True
                    pos=datelist_price.index(d1)
                    p=pricelist[pos]
            while (d1 <= date_price_max) and not found:
                d1=date_adjust(d1,adjust=1)
                if d1 in datelist_price:
                    found=True
                    pos=datelist_price.index(d1)
                    p=pricelist[pos]            
        #记录股价
        row=pd.Series({'endDate':d,'actualDate':d1,'Price':p})
        pricedf=pricedf.append(row,ignore_index=True)

    #合成表
    fsdf1=pd.merge(fsdf,pricedf,on='endDate')
    fsdf1['BasicPE']=fsdf1['Price']/fsdf1['BasicEPS']
    fsdf1['DilutedPE']=fsdf1['Price']/fsdf1['DilutedEPS']

    return fsdf1

if __name__ == '__main__':
    fsdf1=get_PE(fsdf)

#==============================================================================
if __name__ == '__main__':
    fsdf=get_financial_statements('AAPL')
    fst=fsdf.T  #查看科目名称更加方便

def calc_DebtToAsset(fsdf):
    """
    功能：计算资产负债率
    """
    
    fsdf1=fsdf.copy()
    
    #计算Debt to Asset
    try:
        fsdf1['Debt to Asset']=round(fsdf1['TotalLiabilities']/fsdf1['TotalAssets'],4)
    except:
        print("#Error(get_DebtToAsset): failed in calculating DebtToAsset")
    
    #计算Debt to Equity
    try:
        fsdf1['Debt to Equity']=round(fsdf1['TotalLiabilities']/fsdf1['TotalEquities'],4)    
    except:
        print("#Error(get_DebtToAsset): failed in calculating DebtToEquity")    
    
    return fsdf1

if __name__ == '__main__':
    fsdf1=get_DebtToAsset(fsdf)


#==============================================================================
if __name__ == '__main__':
    fsdf=get_financial_statements('AAPL')
    fst=fsdf.T  #查看科目名称更加方便

def calc_fin_rates(fsdf):
    """
    功能：基于财报计算各种指标
    """
    #####前后填充缺失值
    if fsdf is None: return None
    fs = fsdf.fillna(method='ffill').fillna(method='bfill')
    
    """
    #期初期末平均数
    fs['avgInventory']=(fs['Inventory']+fs['Inventory'].shift(1))/2.0 
    fs['avgReceivables']=(fs['AccountsReceivable']+fs['AccountsReceivable'].shift(1))/2.0 
    fs['avgCurrentAsset']=(fs['CurrentAssets']+fs['CurrentAssets'].shift(1))/2.0 
    fs['avgPPE']=(fs['NetPPE']+fs['NetPPE'].shift(1))/2.0  
    fs['avgTotalAsset']=(fs['TotalAssets']+fs['TotalAssets'].shift(1))/2.0  
    fs['avgNetPPE']=(fs['NetPPE']+fs['NetPPE'].shift(1))/2.0
    fs['avgGrossPPE']=(fs['GrossPPE']+fs['GrossPPE'].shift(1))/2.0
    fs['avgTotalEquity']=(fs['TotalEquities']+fs['TotalEquities'].shift(1))/2.0  
    """
    
    #短期偿债能力指标
    #流动比率：流动资产 / 流动负债
    fs['Current Ratio']=fs['CurrentAssets']/fs['CurrentLiabilities']
    #速动比率：（流动资产-存货） / 流动负债
    fs['Quick Ratio']=(fs['CurrentAssets']-fs['Inventory'])/fs['CurrentLiabilities']
    #现金比率: （现金+现金等价物） / 流动负债
    fs['Cash Ratio']=fs['CashAndCashEquivalents']/fs['CurrentLiabilities']
    #现金流量比率：经营活动现金流量 / 流动负债
    fs['Cash Flow Ratio']=fs['OperatingCashFlow']/fs['CurrentLiabilities']
    
    #####长期偿债能力指标
    #资产负债率：负债总额 / 资产总额
    fs['Debt to Asset']=fs['TotalLiabilities']/fs['TotalAssets']
    #股东权益比率：股东权益总额 / 资产总额
    fs['Equity to Asset']=fs['TotalEquities']/fs['TotalAssets']
    #权益乘数：资产总额 / 股东权益总额
    fs['Equity Multiplier']=fs['TotalAssets']/fs['TotalEquities']
    #fs['Equity Multiplier']=fs['avgTotalAsset']/fs['avgTotalEquity']
    #负债股权比率：负债总额 / 股东权益总额
    fs['Debt to Equity']=fs['TotalLiabilities']/fs['TotalEquities']
    #有形净值债务率：负债总额 / （股东权益-无形资产净额）
    fs['netIntangibleAsset']=fs['TotalAssets']-fs['NetTangibleAssets']
    fs['Debt to Tangible Net Asset']=fs['TotalLiabilities']/(fs['TotalEquities']-fs['netIntangibleAsset'])
    #偿债保障比率：负债总额 / 经营活动现金净流量
    fs['Debt Service Coverage']=fs['TotalLiabilities']/fs['OperatingCashFlow']
    #利息保障倍数：（税前利润+利息费用）/ 利息费用
    fs['Times Interest Earned']=fs['PretaxIncome']/fs['InterestExpense']+1
    
    #营运能力指标
    #存货周转率：销售成本 / 平均存货     
    #fs['Inventory Turnover']=fs['CostOfRevenue']/fs['avgInventory']
    fs['Inventory Turnover']=fs['CostOfRevenue']/fs['Inventory']
    #应收账款周转率：赊销收入净额 / 平均应收账款余额         
    #fs['Receivable Turnover']=fs['TotalRevenue']/fs['avgReceivables']
    fs['Receivable Turnover']=fs['TotalRevenue']/fs['AccountsReceivable']
    #流动资产周转率：销售收入 / 平均流动资产余额     
    #fs['Current Asset Turnover']=fs['TotalRevenue']/fs['avgCurrentAsset']
    fs['Current Asset Turnover']=fs['TotalRevenue']/fs['CurrentAssets']
    #固定资产周转率：销售收入 / 平均固定资产净额    
    #fs['Fixed Asset Turnover']=fs['TotalRevenue']/fs['avgPPE']
    fs['Fixed Asset Turnover']=fs['TotalRevenue']/fs['NetPPE']
    #总资产周转率：销售收入 / 平均资产总额    
    #fs['Total Asset Turnover']=fs['TotalRevenue']/fs['avgTotalAsset']
    fs['Total Asset Turnover']=fs['TotalRevenue']/fs['TotalAssets']
    
    #主营业务利润率=主营业务利润/主营业务收入
    fs['Operating Margin']=fs['OperatingIncome']/fs['OperatingRevenue']
    
    #发展潜力指标
    #营业收入增长率：本期营业收入增长额 / 上年同期营业收入总额
    fs['Revenue Growth']=fs['OperatingRevenue'].pct_change()
    #资本积累率：本期所有者权益增长额 / 年初所有者权益
    fs['Capital Accumulation']=fs['TotalEquities'].pct_change()
    #总资产增长率：本期总资产增长额 / 年初资产总额    
    fs['Total Asset Growth']=fs['TotalAssets'].pct_change()
    #固定资产成新率：平均固定资产净值 / 平均固定资产原值。又称“固定资产净值率”或“有用系数”
    #fs['PPE Residual']=fs['avgNetPPE']/fs['avgGrossPPE']
    fs['PPE Residual']=fs['NetPPE']/fs['GrossPPE']
    
    #其他指标
    #盈利能力指标
    #资产报酬率（息前税后）：利润总额+利息支出 / 平均资产总额        
    #fs['Return on Asset']=(fs['NetIncome']+fs['InterestExpense'])/fs['avgTotalAsset']
    fs['Return on Asset']=(fs['NetIncome']+fs['InterestExpense'])/fs['TotalAssets']
    fs['ROA']=fs['Return on Asset']
    #（投入）资本回报率（Return on Invested Capital，简称ROIC）
    #ROIC=NOPLAT(息前税后经营利润)/IC(投入资本)
    #NOPLAT=EBIT×(1－T)=(营业利润+财务费用－非经常性投资损益) ×(1－所得税率)
    #IC=有息负债+净资产－超额现金－非经营性资产
    fs['Return on Invested Capital']=(fs['OperatingIncome']+fs['InterestExpense'])*(1-fs['TaxRateForCalcs'])/fs['InvestedCapital']
    fs['Return on Invested Capital']=fs['Return on Invested Capital']
    fs['ROIC']=fs['Return on Invested Capital']
    #净资产报酬率：净利润 / 平均净资产    
    #fs['Return on Net Asset']=fs['NetIncome']/fs['avgTotalEquity']
    fs['Return on Net Asset']=fs['NetIncome']/fs['TotalEquities']
    #股东权益报酬率：净利润 / 平均股东权益总额
    fs['Return on Equity']=fs['Return on Net Asset']
    fs['ROE']=fs['Return on Equity']
    #毛利率：销售毛利 / 销售收入净额    
    fs['Gross Margin']=fs['GrossProfit']/fs['TotalRevenue']
    #销售净利率：净利润 / 销售收入净额
    fs['Profit Margin']=fs['NetIncome']/fs['TotalRevenue']
    #成本费用净利率：净利润 / 成本费用总额
    fs['Net Profit on Costs']=fs['NetIncome']/fs['CostOfRevenue']
    #股利发放率：每股股利 / 每股利润   
    fs['Payout Ratio']=fs['CashDividendsPaid']/fs['NetIncome']

    ###每股指标，受EPS可用性影响    
    #每股利润：（净利润-优先股股利） / 加权流通在外股数。基本EPS
    #注意：流通股股数=期初commonStock-treasuryStock,加本年增加的股数issuanceOfStock*月份占比-本年减少的股数repurchaseOfStock*月份占比
    import numpy as np
    fs['outstandingStock']=np.floor(fs['NetIncomeCommonStockholders']/fs['BasicEPS'])
    #每股现金流量：（经营活动现金净流量-优先股股利） / 流通在外股数
    fs['Cashflow per Share']=fs['OperatingCashFlow']/fs['outstandingStock']
    fs['CFPS']=fs['Cashflow per Share']
    #每股股利：（现金股利总额-优先股股利） /流通在外股数    
    fs['Dividend per Share']=fs['CashDividendsPaid']/fs['outstandingStock']
    fs['DPS']=fs['Dividend per Share']
    #每股净资产：股东权益总额 / 流通在外股数  
    fs['Net Asset per Share']=fs['CommonStockEquity']/fs['outstandingStock']
    
    #市盈率：每股市价 / 每股利润，依赖EPS反推出的流通股数量
    #fs=get_PE(fs)
    dateymd=lambda x:x.strftime('%Y-%m-%d') 
    fs['endDate']=fs['asOfDate'].apply(dateymd)
    
    fs['date']=fs['endDate']
    fs.set_index('date',inplace=True)    
    
    return fs
    
    
if __name__ == '__main__':
    fs=calc_fin_rates(fsdf)

#==============================================================================
if __name__ == '__main__':
    ticker='AAPL'

def get_financial_rates(ticker):
    """
    功能：获得股票的财务报表和财务比率
    财务报表：资产负债表，利润表，现金流量表
    财务比率：短期还债能力，长期还债能力，营运能力，盈利能力，发展能力
    返回：报表+比率    
    """
    print("\nAnalyzing financial rates of",ticker,"\b, it may take time......")
    
    #抓取股票的财务报表
    try:
        fsdf=get_financial_statements(ticker)
    except:
        print("......Failed to get financial statements of",ticker,"\b, recovering")
        import time; time.sleep(5)
        try:
            fsdf=get_financial_statements(ticker)
        except:
            print("......Failed to get financial statements of",ticker,"\b!")
            print("......If the stock code",ticker,"\b is correct, please try a few minutes later.")
        return None
        
    #抓取股票的稀释后EPS，计算财务比率
    fsr=calc_fin_rates(fsdf)
    if fsr is None: return None
    """
    try:
        fsr=calc_fin_rates(fsdf)
    except:
        print("......Failed to calculate some financial rates of",ticker,"\b!")
        return None
    """
    #整理列名：将股票代码、截止日期、报表类型排在开头
    cols=list(fsr)
    cols.remove('endDate')
    cols.remove('ticker')
    cols.remove('periodType')
    fsr2=fsr[['ticker','endDate','periodType']+cols]
    
    return fsr2

"""
短期偿债能力分析：
1、流动比率，计算公式： 流动资产 / 流动负债
2、速动比率，计算公式： （流动资产-存货） / 流动负债
3、现金比率，计算公式： （现金+现金等价物） / 流动负债
4、现金流量比率，计算公式： 经营活动现金流量 / 流动负债

长期偿债能力分析：
1、资产负债率，计算公式： 负债总额 / 资产总额
2、股东权益比率，计算公式： 股东权益总额 / 资产总额
3、权益乘数，计算公式： 资产总额 / 股东权益总额
4、负债股权比率，计算公式： 负债总额 / 股东权益总额
5、有形净值债务率，计算公式： 负债总额 / （股东权益-无形资产净额）
6、偿债保障比率，计算公式： 负债总额 / 经营活动现金净流量
7、利息保障倍数，计算公式： （税前利润+利息费用）/ 利息费用

营运分析
1、存货周转率，计算公式： 销售成本 / 平均存货
2、应收账款周转率，计算公式： 赊销收入净额 / 平均应收账款余额
3、流动资产周转率，计算公式： 销售收入 / 平均流动资产余额
4、固定资产周转率，计算公式： 销售收入 / 平均固定资产净额
5、总资产周转率，计算公式： 销售收入 / 平均资产总额

盈利分析
1、资产报酬率，计算公式： 利润总额+利息支出 / 平均资产总额
2、净资产报酬率，计算公式： 净利润 / 平均净资产
3、股东权益报酬率，计算公式： 净利润 / 平均股东权益总额
4、毛利率，计算公式： 销售毛利 / 销售收入净额
5、销售净利率，计算公式： 净利润 / 销售收入净额
6、成本费用净利率，计算公式： 净利润 / 成本费用总额
7、每股利润，计算公式： （净利润-优先股股利） / 流通在外股数
8、每股现金流量，计算公式： （经营活动现金净流量-优先股股利） / 流通在外股数
9、每股股利，计算公式： （现金股利总额-优先股股利） /流通在外股数
10、股利发放率，计算公式： 每股股利 / 每股利润
11、每股净资产，计算公式： 股东权益总额 / 流通在外股数
12、市盈率，计算公式： 每股市价 / 每股利润
13、主营业务利润率=主营业务利润/主营业务收入*100%

发展分析
1、营业增长率，计算公式： 本期营业增长额 / 上年同期营业收入总额
2、资本积累率，计算公式： 本期所有者权益增长额 / 年初所有者权益
3、总资产增长率，计算公式： 本期总资产增长额 / 年初资产总额
4、固定资产成新率，计算公式： 平均固定资产净值 / 平均固定资产原值
"""
#==============================================================================
#==============================================================================
#==============================================================================
#####以上的指标为时间序列；以下的指标为非时间序列，类似于快照信息
#==============================================================================
if __name__=='__main__':
    symbol='AAPL'
    symbol='BABA'
    symbol='2883.HK'
    symbol='EBAY'

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
    adict=stock.asset_profile
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
    adict=stock.esg_scores
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
    adict=stock.financial_data
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
    adict=stock.key_stats
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
    adict=stock.price
    keylist=list(adict[symbol].keys())
    aframe=pd.DataFrame.from_dict(adict, orient='index', columns=keylist)
    ainfo=aframe.T
    info=pd.concat([info,ainfo]) 
    

    """
    Quote Type:
    exchange, firstTradeDateEpocUtc(上市日期), longName, quoteType(证券类型：股票), 
    shortName, symbol(当前代码), timeZoneFullName, timeZoneShortName, underlyingSymbol(原始代码), 
    """
    adict=stock.quote_type
    keylist=list(adict[symbol].keys())
    aframe=pd.DataFrame.from_dict(adict, orient='index', columns=keylist)
    ainfo=aframe.T
    info=pd.concat([info,ainfo]) 
    

    """
    Share Purchase Activity
    period(6m), totalInsiderShares
    """
    adict=stock.share_purchase_activity
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
    adict=stock.summary_detail
    keylist=list(adict[symbol].keys())
    aframe=pd.DataFrame.from_dict(adict, orient='index', columns=keylist)
    ainfo=aframe.T
    info=pd.concat([info,ainfo]) 

    
    """
    summary_profile
    address/city/country/zip, phone/fax, sector/industry, website/longBusinessSummary, 
    fullTimeEmployees, 
    """
    adict=stock.summary_profile
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
       
    infot=info.T
    #有的股票信息中缺失returnOnAssets或payoutRatio
    try:       
        #增加IGR
        infot['IGR']=infot['returnOnAssets']*(1-infot['payoutRatio'])/(1-infot['returnOnAssets']*(1-infot['payoutRatio']))
    except:
        pass
    
    #增加SGR
    try:
        infot['SGR']=infot['returnOnEquity']*(1-infot['payoutRatio'])/(1-infot['returnOnEquity']*(1-infot['payoutRatio']))
    except:
        pass
    
    infott=infot.T   
    
    return infott


if __name__=='__main__':
    info=stock_info('AAPL')
    info=stock_info('BABA')

#==============================================================================
if __name__=='__main__':
    info=stock_info('AAPL')

def stock_basic(info):
    
    wishlist=['symbol','shortName','sector','industry', \
              
              #公司名称，业务
              'underlyingSymbol','longName', \
              
              #公司地址，网站
              'address1','address2','city','state','country','zip','phone','fax', \
              'timeZoneShortName','timeZoneFullName','website', \
              
              #员工人数
              'fullTimeEmployees', \
              
              #上市与交易所
              'exchange','exchangeName','quoteType', \
              
              #其他
              'beta','currency','currentPrice','marketCap','trailingPE', \
                  
              'ratingYear','ratingMonth']
        
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
    
    wishlist=['symbol','shortName','sector','industry', \
              
              #公司高管
              'currency','companyOfficers', \
              
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
    
    wishlist=['symbol','shortName','sector','industry', \
              
              'overallRisk','boardRisk','compensationRisk', \
              'shareHolderRightsRisk','auditRisk', \
                  
              'ratingYear','ratingMonth']
        
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
    
    wishlist=['symbol','shortName','sector','industry', \
            
              'totalEsg','esgPerformance','peerEsgScorePerformance', \
              'environmentScore','peerEnvironmentPerformance', \
              'socialScore','peerSocialPerformance', \
              'governanceScore','peerGovernancePerformance', \
              'peerGroup','relatedControversy','peerCount','percentile', \
                
              'ratingYear','ratingMonth']
        
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
    
    wishlist=['symbol','shortName','sector','industry', \
              
              'financialCurrency', \
              
              #偿债能力
              'currentRatio','quickRatio','debtToEquity', \
                  
              #盈利能力
              'ebitdaMargins','operatingMargins','grossMargins','profitMargins', \
                  
              #股东回报率
              'returnOnAssets','returnOnEquity', \
              'dividendRate','trailingAnnualDividendRate','trailingEps', \
              'payoutRatio','revenuePerShare','totalCashPerShare', \
              
              #业务发展能力
              'revenueGrowth','earningsGrowth','earningsQuarterlyGrowth', \
              'enterpriseToRevenue','enterpriseToEbitda', \
                
              'ratingYear','ratingMonth']
        
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
    
    wishlist=['symbol','shortName','sector','industry', \
              
              'financialCurrency','lastFiscalYearEnd','mostRecentQuarter','nextFiscalYearEnd', \
              
              #资产负债
              'enterpriseValue','totalDebt','marketCap', \
                  
              #利润表
              'totalRevenue','grossProfits','ebitda','netIncomeToCommon', \
                  
              #现金流量
              'operatingCashflow','freeCashflow','totalCash', \
              
              #股票数量
              'sharesOutstanding','floatShares','totalInsiderShares', \
                
              'ratingYear','ratingMonth']
        
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
    fin_statements=stock_fin_statements(info) 

#==============================================================================
def stock_market_rates(info):
    
    wishlist=['symbol','shortName','sector','industry', \
              
              'currency','currencySymbol', \
              
              #市场观察
              'priceToBook','priceToSalesTrailing12Months','recommendationKey', \
              
              #市场风险与收益
              'beta','52WeekChange','SandP52WeekChange', \
              'trailingEps','forwardEps','trailingPE','forwardPE','pegRatio', \
              
              #分红
              'dividendYield','fiveYearAvgDividendYield','trailingAnnualDividendYield', \
                  
              #持股
              'heldPercentInsiders','heldPercentInstitutions', \
              
              #股票流通
              'sharesOutstanding','totalInsiderShares','floatShares', \
              'sharesPercentSharesOut','shortPercentOfFloat','shortRatio', \
                
              'ratingYear','ratingMonth']
        
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

    info=stock_info(ticker)
    if not graph: return info
    
    name=info.T['shortName'][0]
    if info_type in ['basic','all']:
        sub_info=stock_basic(info)
        titletxt="***** "+name+": Basic Information *****"        
        printdf(sub_info,titletxt)
    
    if info_type in ['officers','all']:
        sub_info=stock_officers(info)
        titletxt="***** "+name+": Company Senior Management *****"        
        printdf(sub_info,titletxt)    
    
    if info_type in ['fin_rates','all']:
        sub_info=stock_fin_rates(info)
        titletxt="***** "+name+": Fundamental Rates *****"        
        printdf(sub_info,titletxt)
    
    if info_type in ['fin_statements','all']:
        sub_info=stock_fin_statements(info)
        titletxt="***** "+name+": Financial Statements *****"        
        printdf(sub_info,titletxt)
    
    if info_type in ['market_rates','all']:
        sub_info=stock_market_rates(info)
        titletxt="***** "+name+": Market Rates *****"        
        printdf(sub_info,titletxt)
    
    if info_type in ['risk_general','all']:
        sub_info=stock_risk_general(info)
        titletxt="***** "+name+": Risk General *****"+ \
            "\n(Bigger number means higher risk)"
        printdf(sub_info,titletxt)
    
    if info_type in ['risk_esg','all']:
        sub_info=stock_risk_esg(info)
        if len(sub_info)==0:
            print("#Error(get_stock_profile): esg info not available for",ticker)
        else:
            titletxt="***** "+name+": Sustainability Risk *****"+ \
                "\n(Smaller number means less risky)"
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
    sub_info=stock_officers(info)
    titletxt="***** "+ticker+": Snr Management *****"

def printdf(sub_info,titletxt):
    """
    功能：整齐显示股票信息快照
    """
    print("\n"+titletxt)
    
    maxlen=0
    for index,row in sub_info.iterrows():
        if len(row['Item']) > maxlen: maxlen=len(row['Item'])

    for index,row in sub_info.iterrows():
        
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

        thislen=maxlen-len(row['Item'])
        print(row['Item'],'.'*thislen,'\b:',row['Value'])
    
    import datetime
    today=datetime.date.today()
    print("*** Source: Yahoo Finance,",today)
    
    return

if __name__=='__main__':
    printdf(sub_info,titletxt)

#==============================================================================
if __name__=='__main__':
    info=stock_info('AAPL')
    sub_info=stock_officers(info)

def print_companyOfficers(sub_info):
    """
    功能：打印公司高管信息
    """
    item='companyOfficers'
    itemtxt='Company officers:'
    key1='name'
    key2='title'
    key3='yearBorn'
    key4='age'
    key6='totalPay'
    key7='fiscalYear'
    currency=list(sub_info[sub_info['Item'] == 'currency']['Value'])[0]
    alist=list(sub_info[sub_info['Item'] == item]['Value'])[0]
    
    print(itemtxt)
    for i in alist:
        print(' '*4,i[key1])
        print(' '*8,i[key2],'\b,',i[key4],'years old (born',i[key3],'\b)')
        print(' '*8,'Total paid',currency+str(format(i[key6],',')),'@'+str(i[key7]))
        
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
    maxlen=0
    for index,row in sub_info.iterrows():
        if len(row['Item']) > maxlen: maxlen=len(row['Item'])
    thislen=maxlen-len(item)+2
    itemtxt=item+'.'*thislen+'\b:'
    
    key1='min'
    key2='avg'
    key3='max'
    i=list(sub_info[sub_info['Item'] == item]['Value'])[0]
    
    print(itemtxt)
    print(' '*4,key1+':',i[key1],'\b,',key2+':',round(i[key2],2),'\b,',key3+':',i[key3])
        
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
    maxlen=0
    for index,row in sub_info.iterrows():
        if len(row['Item']) > maxlen: maxlen=len(row['Item'])
    thislen=maxlen-len(item)+2
    itemtxt=item+'.'*thislen+'\b:'
    
    alist=list(sub_info[sub_info['Item'] == item]['Value'])[0]
    
    print(itemtxt)
    for i in alist:
        print(' '*4,i)
        
    return

if __name__=='__main__':
    print_controversy(sub_info,item)

#==============================================================================
def calc_dupont(ticker):
    """
    功能：计算股票ticker的杜邦分析项目
    """
    fsr2=get_financial_rates(ticker)
    if fsr2 is None:
        print("  #Error(calc_dupont): failed to retrieved info for",ticker)
        return None   
    
    dpidf=fsr2[['ticker','endDate','periodType','ROE','Profit Margin','Total Asset Turnover','Equity Multiplier']]    
    dpidf['pROE']=dpidf['Profit Margin']*dpidf['Total Asset Turnover']*dpidf['Equity Multiplier']
    
    return dpidf
#==============================================================================
if __name__=='__main__':
    tickerlist=['AAPL','MSFT','FB']
    fsdate='latest'
    scale1 = 10
    scale2 = 10
    hatchlist=['.', 'o', '\\']

def compare_dupont(tickerlist,fsdate='latest',scale1 = 10,scale2 = 10,hatchlist=['.', 'o', '\\']):
    """
    功能：获得tickerlist中每只股票的杜邦分析项目，绘制柱状叠加比较图
    tickerlist：股票代码列表，建议在10只以内
    fsdate：财报日期，默认为最新一期季报/年报，也可规定具体日期，格式：YYYY-MM-DD
    scale1：用于放大销售净利率，避免与权益乘数数量级不一致导致绘图难看问题，可自行调整
    scale2：用于放大总资产周转率，避免与权益乘数数量级不一致导致绘图难看问题，可自行调整
    hatchlist：绘制柱状图的纹理，用于黑白打印时区分，可自定义，
    可用的符号：'-', '+', 'x', '\\', '*', 'o', 'O', '.'    
    """
    import pandas as pd

    lang=check_language()
    """
        ticker ='Ticker'
        name1 = 'Profit Margin'
        name2 = 'Asset Turnover'
        name3 = 'Equity Multiplier'
        name4 = 'ROE'
        name5 = 'Report Date'
        name6 = 'Report Type'    
    """
    ticker = '公司'
    name1 = '销售净利率'
    name2 = '总资产周转率'
    name3 = '权益乘数'
    name4 = '净资产收益率'
    name5 = '财报日期'
    name6 = '财报类型'    
    
    dpidflist,dpilist,fsdatelist,fstypelist=[],[],[],[]
    name1list,name2list,name3list,name4list,name5list,name6list=[],[],[],[],[],[]
    newtickerlist=[]
    for t in tickerlist:
        try:
            dpidf=calc_dupont(t)
        except:
            print("  #Warning(compare_dupont): lack of some accounting items for",t)
            continue
        if fsdate == 'latest': 
            try:
                dpi=dpidf.tail(1)
            except:
                print("  #Warning(compare_dupont): problem in some accounting items for",t)               
                continue
        else: dpi=dpidf[dpidf['endDate']==fsdate]
        if len(dpi) == 0:
            print("  #Warning(compare_dupont): lack of some accounting items for",t,'@',fsdate)
            continue
        
        newtickerlist=newtickerlist+[t]
        dpidflist=dpidflist+[dpidf]
        dpilist=dpilist+[dpi]
        fsdatelist=fsdatelist+[dpi['endDate'][0]]
        fstypelist=fstypelist+[dpi['periodType'][0]]
        
        name1list=name1list+[dpi['Profit Margin'][0]*scale1]
        name2list=name2list+[dpi['Total Asset Turnover'][0]*scale2]
        name3list=name3list+[dpi['Equity Multiplier'][0]]
        name4list=name4list+[dpi['ROE'][0]]
        name5list=name5list+[dpi['endDate'][0]]
        name6list=name6list+[dpi['periodType'][0]]
    
    tickerlist=newtickerlist
    raw_data = {ticker:tickerlist,
            name1:name1list,
            name2:name2list,
            name3:name3list,
            name4:name4list,
            name5:name5list,
            name6:name6list}

    df = pd.DataFrame(raw_data,columns=[ticker,name1,name2,name3,name4,name5,name6])
    num=len(df['公司'])
    for i in range(num):
        code=df.loc[i,'公司']
        df.loc[i,'公司']=codetranslate(code)
    
    f,ax1 = plt.subplots(1,figsize=(10,5))
    w = 0.75
    x = [i+1 for i in range(len(df[name1]))]
    #tick_pos = [i+(w/2.) for i in x]
    tick_pos = [i for i in x]

    ax1.bar(x,df[name3],width=w,bottom=[i+j for i,j in zip(df[name1],df[name2])], \
            label=ectranslate(name3),alpha=0.5,color='green',hatch=hatchlist[0], \
            edgecolor='black',align='center')
    ax1.bar(x,df[name2],width=w,bottom=df[name1],label=ectranslate(name2),alpha=0.5,color='red', \
            hatch=hatchlist[1], edgecolor='black',align='center')
    ax1.bar(x,df[name1],width=w,label=ectranslate(name1),alpha=0.5,color='blue', \
            hatch=hatchlist[2], edgecolor='black',align='center')

    plt.xticks(tick_pos,df[ticker])
    if lang == 'English':
        plt.ylabel(texttranslate("杜邦分析分解项目"),fontsize=ylabel_txt_size)
    else:
        plt.ylabel("杜邦分析分解项目",fontsize=ylabel_txt_size)
    
    tickernamelist,fstypenamelist=[],[]
    for i in range(num):
        tickernamelist=tickernamelist+[codetranslate(tickerlist[i])]
        if fstypelist[i]=='3M': fsname='季报'
        else: fsname='年报'
        fstypenamelist=fstypenamelist+[fsname]
    
    if lang == 'Chinese':
        footnote='【'+'财报日期及类型'+'】'
    else:
        footnote='【'+texttranslate('财报日期及类型')+'】'
        
    #检查财报类型是否一致
    name5types=len(df.groupby(name5).count())
    if name5types > 1:
        #财报类型不一致
        linenum=0   
        for i in range(num):
            if linenum % 4 == 3:
                footnote=footnote+'\n'
            footnote=footnote+codetranslate(tickerlist[i])+"："+fsdatelist[i]+"，"+fstypenamelist[i]
            if linenum < num -1:
                footnote=footnote+'；'
            linenum=linenum + 1
    else:
        footnote=footnote+fsdatelist[0]+"，"+fstypenamelist[0]
        
    import datetime; today=datetime.date.today()
    #footnote1=footnote+'\n'+"【图示放大比例】"+name1+'：x'+str(scale1)+'，'+name2+'：x'+str(scale2)
    if lang == 'Chinese':
        footnote1="【图示放大比例】"+name1+'：x'+str(scale1)+'，'+name2+'：x'+str(scale2)
        footnote2=footnote1+'\n'+"数据来源：雅虎财经,"+' '+str(today)
    else:
        footnote1=texttranslate("【图示放大比例】")+ectranslate(name1)+'：x'+str(scale1)+'，'+ectranslate(name2)+'：x'+str(scale2)
        footnote2=footnote1+'\n'+texttranslate("数据来源: 雅虎财经,")+' '+str(today)
    plt.xlabel(footnote2,fontsize=xlabel_txt_size)
    
    plt.legend(loc='best',fontsize=legend_txt_size)
    if lang == 'Chinese':
        plt.title("杜邦分析对比图",fontsize=title_txt_size,fontweight='bold')
    else:
        plt.title(texttranslate("杜邦分析对比图"),fontsize=title_txt_size,fontweight='bold')
    plt.xlim([min(tick_pos)-w,max(tick_pos)+w])
    plt.show()    
    
    #设置打印对齐
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)    
    if lang == 'Chinese':
        print("===== "+"杜邦分析分项数据表"+" =====")
    else:
        print("===== "+texttranslate("杜邦分析分项数据表")+" =====")
    df[name1]=df[name1]/scale1
    df[name2]=df[name2]/scale2

    for i in range(num):
        code=df.loc[i,'财报类型']
        if code == '3M': df.loc[i,'财报类型']='季报'
        else: df.loc[i,'财报类型']='年报'
    
    dfcols=list(df)
    dfecols=[]
    for c in dfcols:
        ce=ectranslate(c)
        dfecols=dfecols+[ce]
        df[ce]=df[c]
    df[ectranslate('财报类型')]=df['财报类型'].apply(lambda x:'Quarterly' if x=='季报' else 'Annual')
    dfe=df[dfecols]
    
    if lang == 'Chinese':
        print(df.to_string(index=False))
        print("*** "+"数据来源: 雅虎财经,"+' '+str(today))
    else:
        print(dfe.to_string(index=False))
        print("*** "+texttranslate("数据来源: 雅虎财经,")+' '+str(today))
    
    #合并所有历史记录
    alldf=pd.concat(dpidflist)
    alldf.dropna(inplace=True)
    del alldf['pROE']
    
    """
    allnum=len(alldf)
    for i in range(allnum):
        code=alldf.loc[i,'periodType']
        if code == '3M': alldf.loc[i,'periodType']='Quarterly'
        else: alldf.loc[i,'periodType']='Annual'    
    """
    return alldf

if __name__=='__main__':
    tickerlist=['IBM','DELL','WMT'] 
    df=compare_dupont(tickerlist,fsdate='latest',scale1 = 100,scale2 = 10)   
#==============================================================================
#==============================================================================
#==============================================================================
