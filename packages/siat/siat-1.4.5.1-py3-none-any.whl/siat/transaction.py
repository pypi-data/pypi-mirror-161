# -*- coding: utf-8 -*-
"""
本模块功能：为维持兼容性，套壳stock的模块
"""
#==============================================================================
#屏蔽所有警告性信息
import warnings; warnings.filterwarnings('ignore')
#==============================================================================
from siat.common import *
from siat.translate import *
from siat.grafix import *
from siat.security_prices import *

# 复制股票分析函数
from siat.stock import *
#==============================================================================
#==============================================================================
#==============================================================================
# 功能：灵活比较证券指标：先获取收盘价，再行计算、比较和绘图
# 特点1：比compare_security更灵活，可处理债券指数与股票指数的比较
# 特点2：可处理短期国债与长期国债的收益率，模拟短期和长期无风险收益率
#==============================================================================
if __name__=='__main__':
    df1=get_prices('000300.SS','2018-1-1','2020-12-31')

    from siat.bond import *
    df2=bond_prices_china('中债-综合指数','2018-1-1','2020-12-31',graph=False)    
    
    indicator='Annual Ret%'
    fromdate='2019-7-1'
    todate='2020-6-30'
    graph=True
    power=0
    zeroline=True
    twinx=False

def compare_indicator(df1,df2,indicator,fromdate,todate, \
                      graph=True,power=0,zeroline=True, \
                      twinx=False,loc1='upper left',loc2='lower left'):
    """
    功能：基于两个数据表df1/df2中的列Close/Adj Close计算指标indicator，绘图比较
    输入要求：数据表df1/df2中需要，索引为datetime，Close， Adj Close，ticker和footnote
    当footnote为空时不需要显示
    """
    #检查日期期间
    result,start,end=check_period(fromdate,todate)
    if not result:
        print("  Error(compare_indicator): invalid date period from",fromdate,'to',todate)
        if graph: return      
        else: return None
    
    #检查是否支持该indicator
    indlist=['Close','Adj Close','Daily Ret','Daily Ret%','Daily Adj Ret','Daily Adj Ret%',
             'log(Daily Ret)','log(Daily Adj Ret)','Weekly Ret','Weekly Ret%',
             'Weekly Adj Ret','Weekly Adj Ret%','Monthly Ret','Monthly Ret%',
             'Monthly Adj Ret','Monthly Adj Ret%','Quarterly Ret','Quarterly Ret%',
             'Quarterly Adj Ret','Quarterly Adj Ret%','Annual Ret','Annual Ret%',
             'Annual Adj Ret','Annual Adj Ret%','Exp Ret','Exp Ret%','Exp Adj Ret',
             'Exp Adj Ret%','Weekly Price Volatility','Weekly Adj Price Volatility',
             'Monthly Price Volatility','Monthly Adj Price Volatility',
             'Quarterly Price Volatility','Quarterly Adj Price Volatility',
             'Annual Price Volatility','Annual Adj Price Volatility',
             'Exp Price Volatility','Exp Adj Price Volatility',
             'Weekly Ret Volatility','Weekly Ret Volatility%',
             'Weekly Adj Ret Volatility','Weekly Adj Ret Volatility%',
             'Monthly Ret Volatility', 'Monthly Ret Volatility%',
             'Monthly Adj Ret Volatility', 'Monthly Adj Ret Volatility%',
             'Quarterly Ret Volatility', 'Quarterly Ret Volatility%',
             'Quarterly Adj Ret Volatility', 'Quarterly Adj Ret Volatility%',
             'Annual Ret Volatility', 'Annual Ret Volatility%',
             'Annual Adj Ret Volatility', 'Annual Adj Ret Volatility%',
             'Exp Ret Volatility', 'Exp Ret Volatility%', 'Exp Adj Ret Volatility',
             'Exp Adj Ret Volatility%', 'Weekly Ret LPSD', 'Weekly Ret LPSD%',
             'Weekly Adj Ret LPSD', 'Weekly Adj Ret LPSD%', 'Monthly Ret LPSD',
             'Monthly Ret LPSD%', 'Monthly Adj Ret LPSD', 'Monthly Adj Ret LPSD%',
             'Quarterly Ret LPSD', 'Quarterly Ret LPSD%', 'Quarterly Adj Ret LPSD',
             'Quarterly Adj Ret LPSD%', 'Annual Ret LPSD', 'Annual Ret LPSD%',
             'Annual Adj Ret LPSD', 'Annual Adj Ret LPSD%', 'Exp Ret LPSD',
             'Exp Ret LPSD%', 'Exp Adj Ret LPSD', 'Exp Adj Ret LPSD%']
    if indicator not in indlist:
        print("  Error(compare_indicator): unsupported indicator",indicator)
        print("  Supported indicators:",indlist)
        if graph: return      
        else: return None   
    
    print("  Calculating indicators ......")
    #计算df1中的indicator
    df1i=calc_indicators(df1,indicator)   
    df1i1=df1i[df1i.index >=start]
    df1i2=df1i1[df1i1.index <= end]
    
    #计算df2中的indicator
    df2i=calc_indicators(df2,indicator)
    df2i1=df2i[df2i.index >=start]
    df2i2=df2i1[df2i1.index <= end]    
    
    #绘图
    ticker1=codetranslate(df1i2['ticker'][0])
    colname1=indicator
    label1=ectranslate(indicator)

    ticker2=codetranslate(df2i2['ticker'][0])
    colname2=indicator
    label2=ectranslate(indicator)
    
    ylabeltxt=label1
    titletxt="证券指标走势比较"
    
    note=''
    note1=df1i2['footnote'][0]
    if note1 != '':
        note="证券1："+note1
    note2=df2i2['footnote'][0]
    if note2 != '':
        note=note+"证券2："+note2
    if note != '':
        note=note+'\n'
    
    source1=df1i2['source'][0]
    source2=df2i2['source'][0]
    if source1 == source2:
        source=source1
    else:
        source=source1+'，'+source2
    
    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")
    source="数据来源："+source+'，'+today    
    
    footnote=''
    if note != '':
        footnote=note+source
    else:
        footnote=source
    
    plot_line2(df1i2,ticker1,colname1,label1, \
               df2i2,ticker2,colname2,label2, \
               ylabeltxt,titletxt,footnote, \
               power=power,zeroline=zeroline, \
               twinx=twinx,loc1=loc1,loc2=loc2)

    if graph: return      
    else: return df1i2,df2i2  

if __name__=='__main__':
    compare_indicator(df1,df2,'Annual Ret%','2019-7-1','2020-6-30')
    compare_indicator(df1,df2,'Annual Ret Volatility%','2019-7-1','2020-6-30')
    
    from siat.bond import *
    search_bond_index_china(keystr='国债',printout=True)
    df1=bond_index_china('中债-0-1年国债指数','2018-1-1','2020-12-31',graph=False)
    df2=bond_index_china('中债-10年期国债指数','2018-1-1','2020-12-31',graph=False)
    compare_indicator(df1,df2,'Annual Ret%','2019-7-1','2020-6-30')
    compare_indicator(df1,df2,'Annual Ret Volatility%','2019-7-1','2020-6-30')
    compare_indicator(df1,df2,'Exp Ret%','2019-7-1','2020-6-30')
    
    
#==============================================================================
if __name__=='__main__':
    from siat.bond import *
    search_bond_index_china(keystr='国债',printout=True)
    df1=bond_index_china('中债-10年期国债指数','2018-1-1','2020-12-31',graph=False)
    
    indicator='Annual Ret%'
    fromdate='2019-7-1'
    todate='2020-6-30'
    graph=True
    power=0
    zeroline=True
    twinx=False

def draw_indicator(df1,indicator,fromdate,todate, \
                      graph=True,power=0,zeroline=True):
    """
    功能：基于单个数据表df1中的列Close/Adj Close计算指标indicator，绘图
    输入要求：数据表df1中需要，索引为datetime，Close， Adj Close，ticker和footnote
    当footnote为空时不需要显示
    """
    #检查日期期间
    result,start,end=check_period(fromdate,todate)
    if not result:
        print("  Error(calc_indicator): invalid date period from",fromdate,'to',todate)
        if graph: return      
        else: return None
    
    #检查是否支持该indicator
    indlist=['Close','Adj Close','Daily Ret','Daily Ret%','Daily Adj Ret','Daily Adj Ret%',
             'log(Daily Ret)','log(Daily Adj Ret)','Weekly Ret','Weekly Ret%',
             'Weekly Adj Ret','Weekly Adj Ret%','Monthly Ret','Monthly Ret%',
             'Monthly Adj Ret','Monthly Adj Ret%','Quarterly Ret','Quarterly Ret%',
             'Quarterly Adj Ret','Quarterly Adj Ret%','Annual Ret','Annual Ret%',
             'Annual Adj Ret','Annual Adj Ret%','Exp Ret','Exp Ret%','Exp Adj Ret',
             'Exp Adj Ret%','Weekly Price Volatility','Weekly Adj Price Volatility',
             'Monthly Price Volatility','Monthly Adj Price Volatility',
             'Quarterly Price Volatility','Quarterly Adj Price Volatility',
             'Annual Price Volatility','Annual Adj Price Volatility',
             'Exp Price Volatility','Exp Adj Price Volatility',
             'Weekly Ret Volatility','Weekly Ret Volatility%',
             'Weekly Adj Ret Volatility','Weekly Adj Ret Volatility%',
             'Monthly Ret Volatility', 'Monthly Ret Volatility%',
             'Monthly Adj Ret Volatility', 'Monthly Adj Ret Volatility%',
             'Quarterly Ret Volatility', 'Quarterly Ret Volatility%',
             'Quarterly Adj Ret Volatility', 'Quarterly Adj Ret Volatility%',
             'Annual Ret Volatility', 'Annual Ret Volatility%',
             'Annual Adj Ret Volatility', 'Annual Adj Ret Volatility%',
             'Exp Ret Volatility', 'Exp Ret Volatility%', 'Exp Adj Ret Volatility',
             'Exp Adj Ret Volatility%', 'Weekly Ret LPSD', 'Weekly Ret LPSD%',
             'Weekly Adj Ret LPSD', 'Weekly Adj Ret LPSD%', 'Monthly Ret LPSD',
             'Monthly Ret LPSD%', 'Monthly Adj Ret LPSD', 'Monthly Adj Ret LPSD%',
             'Quarterly Ret LPSD', 'Quarterly Ret LPSD%', 'Quarterly Adj Ret LPSD',
             'Quarterly Adj Ret LPSD%', 'Annual Ret LPSD', 'Annual Ret LPSD%',
             'Annual Adj Ret LPSD', 'Annual Adj Ret LPSD%', 'Exp Ret LPSD',
             'Exp Ret LPSD%', 'Exp Adj Ret LPSD', 'Exp Adj Ret LPSD%']
    if indicator not in indlist:
        print("  Error(calc_indicator): unsupported indicator",indicator)
        print("  Supported indicators:",indlist)
        if graph: return      
        else: return None   
    
    print("  Calculating indicators ......")
    #计算df1中的indicator
    df1i=calc_indicators(df1,indicator)   
    df1i1=df1i[df1i.index >=start]
    df1i2=df1i1[df1i1.index <= end]
    
    
    #绘图
    ticker1=codetranslate(df1i2['ticker'][0])
    colname1=indicator
    label1=ectranslate(indicator)

    ylabeltxt=label1
    titletxt="证券指标走势："+ticker1
    
    note=''
    note1=df1i2['footnote'][0]
    if note1 != '':
        note="证券1："+note1
    if note != '':
        note=note+'\n'
    
    source1=df1i2['source'][0]
    source=source1
    
    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")
    source="数据来源："+source+'，'+today    
    
    footnote=''
    if note != '':
        footnote=note+source
    else:
        footnote=source
    
    plot_line(df1i2,colname1,label1,ylabeltxt,titletxt,footnote, \
              power=power,zeroline=zeroline)
    #print("power=",power,"zeroline=",zeroline)

    if graph: return      
    else: return df1i2

if __name__=='__main__':
    draw_indicator(df1,'Annual Ret%','2019-7-1','2020-6-30')
#==============================================================================
if __name__=='__main__':
    indicator=''
    df=df1

def calc_indicators(df,indicator):
    """
    功能：基于df中的列Close/Adj Close计算indicator，生成新的列indicator
    """
    
    #计算indicator
    import siat.stock as sst
    #加入日收益率
    df1=sst.calc_daily_return(df)
    df1.dropna(subset=['Daily Ret'],inplace=True)
    fromdate=df1.index[0].strftime("%Y-%m-%d")
    
    #加入滚动收益率
    df1a=sst.calc_rolling_return(df1, "Weekly") 
    df1b=sst.calc_rolling_return(df1a, "Monthly")
    df1c=sst.calc_rolling_return(df1b, "Quarterly")
    df1d=sst.calc_rolling_return(df1c, "Annual")         
    #加入扩展收益率
    df2=sst.calc_expanding_return(df1d,fromdate)    
    collist=list(df2)
    if indicator in collist:
        return df2
    
    #加入滚动价格波动风险
    df2a=sst.rolling_price_volatility(df2, "Weekly") 
    df2b=sst.rolling_price_volatility(df2a, "Monthly")
    df2c=sst.rolling_price_volatility(df2b, "Quarterly")
    df2d=sst.rolling_price_volatility(df2c, "Annual") 
    #加入累计价格波动风险
    df3=sst.expanding_price_volatility(df2d,fromdate)    
    collist=list(df3)
    if indicator in collist:
        return df3
    
    #加入滚动收益率波动风险
    df3a=sst.rolling_ret_volatility(df3, "Weekly") 
    df3b=sst.rolling_ret_volatility(df3a, "Monthly")
    df3c=sst.rolling_ret_volatility(df3b, "Quarterly")
    df3d=sst.rolling_ret_volatility(df3c, "Annual") 
    #加入累计收益率波动风险
    df4=sst.expanding_ret_volatility(df3d,fromdate)    
    collist=list(df4)
    if indicator in collist:
        return df4
    
    #加入滚动收益率下偏标准差
    df4a=sst.rolling_ret_lpsd(df4, "Weekly") 
    df4b=sst.rolling_ret_lpsd(df4a, "Monthly")
    df4c=sst.rolling_ret_lpsd(df4b, "Quarterly")
    df4d=sst.rolling_ret_lpsd(df4c, "Annual") 
    #加入扩展收益率下偏标准差
    df5=sst.expanding_ret_lpsd(df4d,fromdate)    

    return df5

if __name__=='__main__':
    df1i=calc_indicators(df1,'')

#==============================================================================
#==============================================================================
#==============================================================================
# 功能：沪深市场概况
#==============================================================================
if __name__=='__main__':
    market='SSE'
    market='SZSE'

def market_profile_china(market='SSE'):
    """
    功能：沪深市场概况
    """
    market1=market.upper()
    mktlist=['SSE','SZSE']
    if market1 not in mktlist:
        print("  #Error(market_profile_china): unsupported market",market)
        print("  Supported market abbreviation:",mktlist)
    import datetime as dt
    today=dt.date.today()
    
    import akshare as ak
    lang=check_language()
    
    if market1 == 'SSE':
        try:
            info=ak.stock_sse_summary()
        except:
            print("  #Error(market_profile_china): failed to retrieve SSE summary info")
            return

        if lang == 'Chinese':       
            print("\n=== 上海证券交易所上市股票概况 ===\n")
        else:
            print("\n    Exchange Stock Summary： Shanghai Stock Exchange\n")
            
        typelist=['股票','主板','科创板']
        typelist2=['Stock overall','Main board','STAR board']
        
        itemlist=['上市股票','总股本','流通股本','总市值','流通市值']
        itemlist2=['上市股票/只','总股本/亿股（份）','流通股本/亿股（份）','总市值/亿元','流通市值/亿元']
        itemlist2e=['Number of stocks','Total shares(100m)','Shares outstanding(100m)','Total capitalization(RMB 100m)','Outstandng capitalization(RMB 100m)']
        
        for t in typelist:
            subdf=info[['项目',t]]
            if lang == 'English':
                pos=typelist.index(t)
                t2=typelist2[pos]
                print('*** '+t2+':')
            else:
                print('*** '+t+':')
                
            lenlist=[]
            for m in itemlist2:
                l=hzlen(m)
                lenlist=lenlist+[l]
            maxlen=max(lenlist)
                
            for i in itemlist:
                
                try:
                    value=list(subdf[subdf['项目']==i][t])[0]
                    pos=itemlist.index(i)
                    
                    if lang == 'Chinese':
                        i2=itemlist2[pos]
                        blanknum=maxlen-hzlen(i2)
                        print('   ',i2+' '*blanknum+'：',end='')
                    else:
                        i2e=itemlist2e[pos]
                        blanknum=maxlen-hzlen(i2e)
                        print('   ',i2e+' '*blanknum+'：',end='')
                except:
                    pos=itemlist.index(i)
                    i2=itemlist2[pos]
                    value=list(subdf[subdf['项目']==i2][t])[0]
                    i2e=itemlist2e[pos]
                    
                    if lang == 'Chinese':
                        blanknum=maxlen-hzlen(i2)
                        print('   ',i2+' '*blanknum+'：',end='')
                    else:
                        blanknum=maxlen-hzlen(i2e)
                        print('   ',i2e+' '*blanknum+'：',end='')
                
                if i in ["上市股票",'上市公司']: #若是字符则转换成数字
                    value2=int(value)
                else:
                    value2=float(value)
                print("{:,}".format(value2))
                
        if lang == 'Chinese':
            #print("    注：部分上市公司同时发行A股和B股")
            print("\n    数据来源：上交所，",today)
        else:
            print("\n    Source: Shanghai Stock Exchange,",today)
            
        
    if market1 == 'SZSE':
        df=ak.stock_szse_summary()  
        df1=df[df['证券类别'].isin(['股票','主板A股','主板B股','中小板','创业板A股'])]
        
        #字段改名
        """
        df1.rename(columns={'证券类别':'type','数量(只)':'上市股票/只', \
            '总股本':'总股本/亿股（份）','总市值':'总市值/亿元', \
            '流通股本':'流通股本/亿股（份）','流通市值':'流通市值/亿元'},inplace=True)
        """
        df1.rename(columns={'证券类别':'type','数量':'上市股票/只', \
            '总市值':'总市值/亿元', \
            '流通市值':'流通市值/亿元'},inplace=True)
        #df1['总股本/亿股（份）']=df1['总股本/亿股（份）'].apply(lambda x:round(x/100000000.0,2))
        df1['总市值/亿元']=df1['总市值/亿元'].apply(lambda x:round(x/100000000.0,2))
        #df1['流通股本/亿股（份）']=df1['流通股本/亿股（份）'].apply(lambda x:round(x/100000000.0,2))
        df1['流通市值/亿元']=df1['流通市值/亿元'].apply(lambda x:round(x/100000000.0,2))
        
        del df1['成交金额']
        #del df1['成交量']
        df1.loc[(df1['type']=='股票'),'type']='总貌'
        df1.loc[(df1['type']=='创业板A股'),'type']='创业板'
        
        #itemlist=['数量','总股本/亿股（份）','流通股本/亿股（份）','总市值/亿元','流通市值/亿元']
        itemlist=['上市股票/只','总市值/亿元','流通市值/亿元']
        itemliste=['Number of stocks','Total capitalization(RMB 100m)','Outstandng capitalization(RMB 100m)']
        
        lenlist=[]
        for m in itemlist:
            l=hzlen(m)
            lenlist=lenlist+[l]
        maxlen=max(lenlist)        
        
        import pandas as pd
        info=pd.DataFrame(columns=('type','item','number'))
        df1s0=df1[df1['type']=='总貌']
        for i in itemlist:
            row=pd.Series({'type':'总貌','item':i,'number':list(df1s0[i])[0]})
            info=info.append(row,ignore_index=True)            
        
        df1s2=df1[df1['type']=='创业板']
        for i in itemlist:
            row=pd.Series({'type':'创业板','item':i,'number':list(df1s2[i])[0]})
            info=info.append(row,ignore_index=True) 

        df2=df1[df1['type'].isin(['主板A股', '主板B股', '中小板'])]
        for i in itemlist:
            row=pd.Series({'type':'主板','item':i,'number':df2[i].sum()})
            info=info.append(row,ignore_index=True)         
        
        if lang == 'Chinese':
            print("\n=== 深圳证券交易所上市股票概况 ===\n")
        else:
             print("\n    Exchange Stock Summary： Shenzhen Stock Exchange\n")
             
        typelist=['总貌','主板','创业板']
        typeliste=['Stock overall','Main board','GEM board']
        
        for t in typelist:
            subdf=info[info['type']==t]
            if lang == 'Chinese':
                print('*** '+t+':')
            else:
                pos=typelist.index(t)
                te=typeliste[pos]
                print('*** '+te+':')
                
            for i in itemlist:
                blanknum=maxlen-hzlen(i)
                value=list(subdf[subdf['item']==i]['number'])[0]
                
                if lang == 'Chinese':
                    print('   ',i+' '*blanknum+'：',end='')
                else:
                    pos=itemlist.index(i)
                    ie=itemliste[pos]
                    print('   ',ie+' '*blanknum+'：',end='')
                    
                print("{:,}".format(value))
        
        if lang == 'Chinese':
            print("\n    注：主板包括了中小板，数据来源：深交所，",today)
        else:
            print("\n    Note: SMB board included in Main board\n    Source: Shenzhen Stock Exchange,",today)
        
        info=df
        
    return info

if __name__=='__main__':
    market_profile_china('SSE')
    market_profile_china('SZSE')

#==============================================================================

    