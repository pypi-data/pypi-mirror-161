# -*- coding: utf-8 -*-
"""
本模块功能：证券资产的流动性风险与溢价
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2019年6月18日
最新修订日期：2020年7月16日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
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

def calc_roll_spread(pfdf):
    """
    功能：从给定的股票或投资组合portfolio的数据集df中按期间计算罗尔价差
    投资组合的结构：{'Market':('US','^GSPC'),'AAPL':0.5,'MSFT':0.3,'IBM':0.2}
    输入：投资组合价格df，单一数据集有利于计算滚动指数
    输出：罗尔价差%
    注意：不包括爬虫部分
    """
    sp=pfdf.copy()
    #计算价格序列的价差
    sp['dP']=sp['Close'].diff()
    sp['dP_1']=sp['dP'].shift(1)
    sp2=sp[['Close','dP','dP_1']].copy()      
    sp2.dropna(inplace=True)
    if len(sp2) == 0: return None

    #计算指标，注意cov函数的结果是一个矩阵
    import numpy as np
    rs_cov=abs(np.cov(sp2['dP'],sp2['dP_1'])[0,1])    
    #计算价格均值
    p_mean=sp2['Close'].mean()    
    rs=2*np.sqrt(rs_cov)/p_mean 

    rs_pct=round(rs*100.0,4)
    return rs_pct

if __name__=='__main__':
    pf={'Market':('US','^GSPC'),'AAPL':1.0}
    start='2020-1-1'; end='2020-3-31'
    pfdf=get_portfolio_prices(pf,start,end)
    rs=calc_roll_spread(pfdf)

#==============================================================================    
def roll_spread_portfolio(portfolio,start,end,printout=True):
    """
    功能：按期间计算一个投资组合的罗尔价差，并输出结果
    投资组合的结构：{'Market':('US','^GSPC'),'AAPL':0.5,'MSFT':0.3,'IBM':0.2}
    输入：投资组合，开始日期，结束日期，是否打印结果(默认打印)
    输出：罗尔价差%
    注意：含爬虫部分，调用其他函数
    """

    #仅为测试用
    #portfolio={'Market':('US','^GSPC'),'EDU':0.7,'TAL':0.3}
    #start='2019-06-01'
    #end  ='2019-06-30'

    #检查日期和期间的合理性
    flag,start2,end2=check_period(start,end)
    if not flag:
        print("  #Error(roll_spread_portfolio): invalid period for,", start, end)
        return None
    
    #抓取股票价格，构建投资组合价格
    sp=get_portfolio_prices(portfolio,start2,end2)
    if sp is None:
        print("  #Error(roll_spread_portfolio): portfolio info not available.")
        return None    

    #计算罗尔价差指标
    rs_pct=calc_roll_spread(sp)
    
    #打印报告
    if printout == True:
        date_start=str(sp.index[0].year)+'-'+str(sp.index[0].month)+ \
            '-'+str(sp.index[0].day)
        date_end=str(sp.index[-1].year)+'-'+str(sp.index[-1].month)+ \
            '-'+str(sp.index[-1].day)            
        print("\n===== 投资组合的流动性风险 =====")
        
        _,_,tickerlist,sharelist=decompose_portfolio(portfolio)
        if len(tickerlist)==1:
            product=str(codetranslate(tickerlist))
        else:
            product=str(codetranslate(tickerlist))+' by '+str(sharelist)
        print("投资组合:",product)        
        print("计算期间:",date_start,"to",date_end, \
                  "(可用日期)")
        print("罗尔价差%:",rs_pct)
    
    return rs_pct

if __name__=='__main__':
    pf_aapl={'Market':('US','^GSPC'),'AAPL':1.0}
    rs_aapl=roll_spread_portfolio(pf_aapl,'2019-01-01','2019-01-31')    
    
    pfA={'Market':('US','^GSPC'),'AAPL':0.5,'MSFT':0.3,'IBM':0.2}
    rsA=roll_spread_portfolio(pfA,'2019-01-01','2019-01-31')    
    
#==============================================================================        
def calc_amihud_illiquidity(pfdf):
    """
    功能：从给定的投资组合pfdf中计算阿米胡德非流动性
    投资组合的结构：{'Market':('US','^GSPC'),'AAPL':0.5,'MSFT':0.3,'IBM':0.2}
    输入：投资组合价格pfdf
    输出：阿米胡德非流动性
    注意：不包括爬虫部分
    """
    sp=pfdf.copy()
    #计算阿米胡德非流动性
    sp2=sp[['Ret%','Amount']]
    sp2=sp2.dropna()
    if len(sp2) == 0: return None
    
    import numpy as np
    sp2['Ret/Amt']=np.abs(sp2['Ret%'])/np.log10(sp2['Amount'])
    amihud=round(sp2['Ret/Amt'].mean(),4)
    
    return amihud

if __name__=='__main__':
    pf={'Market':('US','^GSPC'),'AAPL':1.0}
    start='2020-1-1'; end='2020-3-31'
    pfdf=get_portfolio_prices(pf,start,end)
    amihud=calc_amihud_illiquidity(pfdf)

#==============================================================================    
def amihud_illiquidity_portfolio(portfolio,start,end,printout=True):
    """
    功能：按天计算一个投资组合的阿米胡德非流动性指数
    投资组合的结构：{'Market':('US','^GSPC'),'AAPL':0.5,'MSFT':0.3,'IBM':0.2}
    输入：投资组合，开始日期，结束日期，是否打印结果
    输出：阿米胡德非流动性指数
    注意：含爬虫部分，调用其他函数
    """

    #仅为测试用
    #portfolio={'Market':('US','^GSPC'),'EDU':0.7,'TAL':0.3}
    #start='2019-06-01'
    #end  ='2019-06-30'

    #检查日期和期间的合理性
    flag,start2,end2=check_period(start,end)
    if not flag:
        print("  #Error(amihud_illiquidity_portfolio): invalid period for,", start, end)
        return None

    #抓取股票价格，构建投资组合价格
    sp=get_portfolio_prices(portfolio,start2,end2)

    #计算指标
    amihud=calc_amihud_illiquidity(sp)
    
    #打印报告
    if printout == True:
        date_start=str(sp.index[0].year)+'-'+str(sp.index[0].month)+ \
            '-'+str(sp.index[0].day)
        date_end=str(sp.index[-1].year)+'-'+str(sp.index[-1].month)+ \
            '-'+str(sp.index[-1].day)            
        print("\n===== 投资组合的流动性风险 =====")
        
        _,_,tickerlist,sharelist=decompose_portfolio(portfolio)
        if len(tickerlist)==1:
            product=str(codetranslate(tickerlist))
        else:
            product=str(codetranslate(tickerlist))+' by '+str(sharelist)
        print("投资组合:",product)        
        print("计算期间:",date_start,"至",date_end, \
                  "(可用日期)")
        print("阿米胡德非流动性:",amihud,"(对数算法)")
    
    return amihud

if __name__=='__main__':
    pf_aapl={'Market':('US','^GSPC'),'AAPL':1.0}
    amihud_aapl=amihud_illiquidity_portfolio(pf_aapl,'2019-01-01','2019-01-31')    

#==============================================================================        
def calc_ps_liquidity(pfdf):
    """
    功能：从给定的投资组合pfdf中计算帕斯托-斯坦堡流动性，原始公式
    投资组合的结构：{'Market':('US','^GSPC'),'AAPL':0.5,'MSFT':0.3,'IBM':0.2}
    输入：投资组合价格df
    输出：帕斯托-斯坦堡流动性
    注意：不包括爬虫部分
    """
    reg=pfdf.copy()
    
    reg['Ret-RF']=reg['Ret%']-reg['RF']
    reg['Ret-RF_1']=reg['Ret-RF'].shift(1)
    reg['Mkt']=reg['Mkt-RF']+reg['RF']
    reg['Mkt_1']=reg['Mkt'].shift(1)
    reg['Amount_1']=reg['Amount'].shift(1)
    
    import numpy as np
    reg1=reg[['Ret-RF','Mkt_1','Ret-RF_1','Amount_1']]
    reg1=reg1.dropna()
    if len(reg1) == 0: return None
    reg1['signAmt_1']=np.sign(reg1['Ret-RF_1'])*np.log10(reg1['Amount_1'])
    reg2=reg1[['Ret-RF','Mkt_1','signAmt_1']].copy()
    
    #回归前彻底删除带有NaN和inf等无效值的样本，否则回归中可能出错
    reg2=reg2[~reg2.isin([np.nan, np.inf, -np.inf]).any(1)].dropna()
    if len(reg2) == 0: return None
    
    ##计算帕斯托-斯坦堡流动性PSL
    import statsmodels.api as sm
    y=reg2['Ret-RF']
    X=reg2[['Mkt_1','signAmt_1']]
    X1=sm.add_constant(X)
    results=sm.OLS(y,X1).fit() 
    try:
        [alpha,beta,psl]=results.params
    except:
        print("  #Error(calc_ps_liquidity): failed to extract reg parms",results.params)
        return None
    
    return round(psl,4)

if __name__=='__main__':
    pf={'Market':('US','^GSPC'),'AAPL':1.0}
    start='2020-1-1'; end='2020-3-31'
    pfdf=get_portfolio_prices(pf,start,end)
    psl=calc_ps_liquidity(pfdf)

#==============================================================================        
def calc_ps_liquidity_modified(pfdf):
    """
    功能：从给定的投资组合pfdf中计算修正的帕斯托-斯坦堡流动性
    投资组合的结构：{'Market':('US','^GSPC'),'AAPL':0.5,'MSFT':0.3,'IBM':0.2}
    输入：投资组合价格df
    输出：修正的帕斯托-斯坦堡流动性，符号内含
    注意：不包括爬虫部分
    """
    reg=pfdf.copy()
    
    reg['Ret-RF']=reg['Ret%']-reg['RF']
    reg['Ret-RF_1']=reg['Ret-RF'].shift(1)
    reg['Mkt']=reg['Mkt-RF']+reg['RF']
    reg['Mkt_1']=reg['Mkt'].shift(1)
    reg['Amount_1']=reg['Amount'].shift(1)
    
    import numpy as np
    reg1=reg[['Ret-RF','Mkt_1','Ret-RF_1','Amount_1']]
    reg1=reg1.dropna()
    if len(reg1) == 0: return None
    
    #修正psl，符号内含
    #reg1['signAmt_1']=np.sign(reg1['Ret-RF_1'])*np.log10(reg1['Amount_1'])
    reg1['signAmt_1']=np.log10(reg1['Amount_1'])
    reg2=reg1[['Ret-RF','Mkt_1','signAmt_1']].copy()
    
    #回归前彻底删除带有NaN和inf等无效值的样本，否则回归中可能出错
    reg2=reg2[~reg2.isin([np.nan, np.inf, -np.inf]).any(1)].dropna()
    if len(reg2) == 0: return None
    
    ##计算帕斯托-斯坦堡流动性PSL
    import statsmodels.api as sm
    y=reg2['Ret-RF']
    X=reg2[['Mkt_1','signAmt_1']]
    X1=sm.add_constant(X)
    results=sm.OLS(y,X1).fit() 
    [alpha,beta,psl]=results.params
    
    return round(psl,4)

if __name__=='__main__':
    pf={'Market':('US','^GSPC'),'AAPL':1.0}
    start='2020-1-1'; end='2020-3-31'
    pfdf=get_portfolio_prices(pf,start,end)
    psl=calc_ps_liquidity_modified(pfdf)

#==============================================================================    
def ps_liquidity_portfolio(portfolio,start,end,printout=True):
    """
    功能：按天计算一个投资组合的帕斯托-斯坦堡流动性
    投资组合的结构：{'Market':('US','^GSPC'),'AAPL':0.5,'MSFT':0.3,'IBM':0.2}
    输入：投资组合，开始日期，结束日期，是否打印结果
    输出：帕斯托-斯坦堡流动性
    注意：含爬虫部分，调用其他函数
    """

    #仅为测试用
    #portfolio={'Market':('US','^GSPC'),'EDU':0.7,'TAL':0.3}
    #start='2019-06-01'
    #end  ='2019-06-30'

    #检查日期和期间的合理性
    flag,start2,end2=check_period(start,end)
    if not flag:
        print("  #Error(amihud_illiquidity_portfolio): invalid period for,", start, end)
        return None

    #抓取股票价格，构建投资组合价格
    sp=get_portfolio_prices(portfolio,start2,end2)

    #计算帕斯托-斯坦堡流动性
    psl=calc_ps_liquidity(sp)
    
    #打印报告
    if printout == True:
        date_start=str(sp.index[0].year)+'-'+str(sp.index[0].month)+ \
            '-'+str(sp.index[0].day)
        date_end=str(sp.index[-1].year)+'-'+str(sp.index[-1].month)+ \
            '-'+str(sp.index[-1].day)            
        print("\n===== 投资组合的流动性风险 =====")
        
        _,_,tickerlist,sharelist=decompose_portfolio(portfolio)
        if len(tickerlist)==1:
            product=str(codetranslate(tickerlist))
        else:
            product=str(codetranslate(tickerlist))+' by '+str(sharelist)
        print("投资组合:",product)
        print("计算期间:",date_start,"to",date_end, \
                  "(可用日期)")
        print("Pastor-Stambaugh流动性:",psl,"(对数算法)")
    
    return psl

if __name__=='__main__':
    pf_aapl={'Market':('US','^GSPC'),'AAPL':1.0}
    psl_aapl=ps_liquidity_portfolio(pf_aapl,'2019-01-01','2019-01-31')    

    
#==============================================================================
#==============================================================================
def plot_liquidity_monthly(portfolio,start,end,liquidity_type):
    """
    功能：将资产流动性指标逐月绘图对比
    输入：投资组合，开始/结束日期，流动性指标类别
    输出：流动性指标的逐月数据框
    显示：按月绘图投资组合的流动性指标
    """
    #仅为测试用
    #portfolio={'Market':('US','^GSPC'),'JD':0.3,'BABA':0.7}
    #start='2019-01-01'
    #end='2019-03-31'
    #liquidity_type='roll_spread'    

    #检查日期和期间的合理性
    flag,start2,end2=check_period(start,end)
    if not flag:
        print("  #Error(plot_liquidity_monthly): invalid period for,", start, end)
        return None

    #检查：支持的liquidity_type
    liquidity_list=['roll_spread','amihud_illiquidity','ps_liquidity']
    if liquidity_type not in liquidity_list:
        print("  #Error(plot_liquidity_monthly): not supported liquidity type")
        print("  Supported liquidity type:",liquidity_list)              
        return None         

    #抓取投资组合信息
    print("\n  Searching for portfolio information ...")
    df=get_portfolio_prices(portfolio,start,end)

    #拆分start/end之间的各个年份和月份
    mdlist=calc_monthly_date_range(start,end)
    if len(mdlist) == 0:
        print("  #Error(plot_liquidity_monthly): start/end dates inappropriate")
        return None          

    #用于保存流动性指标
    import pandas as pd
    print("  Calculating monthly",liquidity_type,"...")
    rarfunc='calc_'+liquidity_type
    rars=pd.DataFrame(columns=('YM','rar'))
    zeroline=False
    for i in range(0,len(mdlist)):
        startym=mdlist[i][0]
        YM=startym.strftime("%Y-%m")
        #print(YM,end=' ')
        endym=mdlist[i][1]
        pfdf=sample_selection(df,startym,endym)
        rar=eval(rarfunc)(pfdf)
        if rar is None: continue
        
        if rar < 0: zeroline=True
        row=pd.Series({'YM':YM,'rar':rar})
        rars=rars.append(row,ignore_index=True)         
    #print("completed.")
    rars.set_index('YM',inplace=True)    
    
    #绘图
    colname='rar'
    collabel=ectranslate(liquidity_type)
    ylabeltxt=ectranslate(liquidity_type)
    titletxt="证券流动性风险的月度指标"
    
    _,_,tickerlist,sharelist=decompose_portfolio(portfolio)
    if len(tickerlist)==1:
        product=str(codetranslate(tickerlist))
    else:
        product=str(codetranslate(tickerlist))+' by '+str(sharelist)
    import datetime as dt; today=dt.date.today()
    footnote="证券="+product+"\n数据来源：新浪/stooq, "+str(today)
    datatag=False
    power=4
    plot_line(rars,colname,collabel,ylabeltxt,titletxt,footnote,datatag, \
              power,zeroline)

    return rars


if __name__=='__main__':
    portfolio={'Market':('US','^GSPC'),'AAPL':1.0}
    start='2019-01-01'; end='2020-6-30'
    liquidity_type='roll_spread'
    liq1=plot_liquidity_monthly(portfolio,start,end,liquidity_type)       
    liquidity_type='amihud_illiquidity'
    liq2=plot_liquidity_monthly(portfolio,start,end,liquidity_type) 
    liquidity_type='ps_liquidity'
    liq3=plot_liquidity_monthly(portfolio,start,end,liquidity_type) 

    pf1={'Market':('US','^GSPC'),'VIPS':0.1,'PDD':0.2,'JD':0.3,'BABA':0.4}
    al1=plot_liquidity_monthly(pf1,start,end,'roll_spread') 

    pf2={'Market':('US','^GSPC'),'^GSPC':1.0}
    al2=plot_liquidity_monthly(pf2,start,end,'roll_spread')
    al3=plot_liquidity_monthly(pf2,start,end,'amihud_illiquidity')
    al4=plot_liquidity_monthly(pf2,start,end,'ps_liquidity')

#==============================================================================
def plot_liquidity_annual(portfolio,start,end,liquidity_type):
    """
    功能：将流动性指标逐年绘图对比
    输入：投资组合，开始/结束日期，流动性指标类别
    输出：流动性指标的逐年数据框
    显示：按年绘图投资组合的流动性指标
    """
    #仅为测试用
    #portfolio={'Market':('US','^GSPC'),'TSLA':1.0}
    #start='2009-07-01'
    #end='2019-06-30'
    #liquidity_type='roll_spread'    

    #检查日期和期间的合理性
    flag,start2,end2=check_period(start,end)
    if not flag:
        print("  #Error(plot_liquidity_annual): invalid period for,", start, end)
        return None

    #检查：支持的liquidity_type
    liquidity_list=['roll_spread','amihud_illiquidity','ps_liquidity']
    if liquidity_type not in liquidity_list:
        print("  #Error(plot_liquidity_annual): not supported liquidity type")
        print("  Supported liquidity type:",liquidity_list)              
        return None         

    #抓取投资组合信息
    print("\n  Searching for portfolio information ...")
    df=get_portfolio_prices(portfolio,start,end)

    #拆分start/end之间的各个年份和月份
    mdlist=calc_yearly_date_range(start,end)
    if len(mdlist) == 0:
        print("  #Error(plot_liquidity_annual): start/end dates inappropriate")
        return None          

    #用于保存指标
    print("  Calculating annual",liquidity_type,"...")
    rarfunc='calc_'+liquidity_type
    import pandas as pd
    rars=pd.DataFrame(columns=('YR','liquidity'))
    zeroline=False   
    for i in range(0,len(mdlist)):
        startyr=mdlist[i][0]
        YR=startyr.strftime("%Y")
        #print(YR,end=' ')
        endyr=mdlist[i][1]
        pfdf=sample_selection(df,startyr,endyr)
        rar=eval(rarfunc)(pfdf)        
        if rar is not None:     
            if rar < 0: zeroline=True
            row=pd.Series({'YR':YR,'liquidity':rar})
            rars=rars.append(row,ignore_index=True)         
    rars.set_index('YR',inplace=True)    
    
    #绘图
    colname='liquidity'
    collabel=ectranslate(liquidity_type)
    ylabeltxt=ectranslate(liquidity_type)
    titletxt="证券流动性风险的年度指标"

    _,_,tickerlist,sharelist=decompose_portfolio(portfolio)
    if len(tickerlist)==1:
        product=str(codetranslate(tickerlist))
    else:
        product=str(codetranslate(tickerlist))+' by '+str(sharelist)
    
    import datetime as dt; today=dt.date.today()
    footnote="证券="+product+"\n数据来源：雅虎财经, "+str(today)    
    datatag=False
    power=4
    plot_line(rars,colname,collabel,ylabeltxt,titletxt,footnote,datatag, \
              power,zeroline)

    return rars


if __name__=='__main__':
    portfolio={'Market':('US','^GSPC'),'AAPL':1.0}
    start='2010-01-01'
    end='2019-12-31'
    liquidity_type='roll_spread'
    al1=plot_liquidity_annual(portfolio,start,end,liquidity_type)  
    
    portfolio={'Market':('US','^GSPC'),'VIPS':0.1,'PDD':0.2,'JD':0.3,'BABA':0.4}
    start='2013-01-01'
    end='2019-06-30'    
    al2=plot_liquidity_annual(portfolio,start,end,liquidity_type) 


#==============================================================================
def draw_liquidity(liqs):
    """
    功能：绘制滚动窗口曲线
    输入：滚动数据df，内含投资组合Portfolio和指数名称Type
    """
    
    plt.figure(figsize=(8,5))

    portfolio=liqs['Portfolio'][0]
    colname='Ratio'
    collabel=ectranslate(liqs['Type'][0])
    ylabeltxt=ectranslate(liqs['Type'][0])
    titletxt="证券流动性风险的滚动趋势"
    
    _,_,tickerlist,sharelist=decompose_portfolio(portfolio)
    if len(tickerlist)==1:
        product=str(codetranslate(tickerlist))
    else:
        product=str(codetranslate(tickerlist))+' by '+str(sharelist)
    
    import datetime as dt; today=dt.date.today()
    footnote="证券="+product+"\n数据来源：新浪/stooq, "+str(today)    
    datatag=False
    power=4
    
    zeroline=False
    neg_liqs=liqs[liqs['Ratio'] < 0]
    if len(neg_liqs) > 0: zeroline=True
    
    plot_line(liqs,colname,collabel,ylabeltxt,titletxt,footnote,datatag, \
              power,zeroline)

    return

#==============================================================================
def liquidity_rolling(portfolio,start,end,liquidity_type, \
                      window=30,graph=True):
    """
    功能：滚动计算一个投资组合的流动性风险
    投资组合的结构：{'Market':('US','^GSPC'),'AAPL':0.5,'MSFT':0.3,'IBM':0.2}
    输入：投资组合，开始日期，结束日期，指数名称，滚动窗口宽度(天数)
    输出：流动性风险
    注意：因需要滚动计算，开始和结束日期之间需要拉开距离
    """

    #检查日期和期间的合理性
    flag,start2,end2=check_period(start,end)
    if not flag:
        print("  #Error(liquidity_rolling): invalid period for,", start, end)
        return None

    #检查：支持的liquidity_type
    liquidity_list=['roll_spread','amihud_illiquidity','ps_liquidity']
    if liquidity_type not in liquidity_list:
        print("  #Error(liquidity_rolling): not supported liquidity type")
        print("  Supported liquidity type:",liquidity_list)              
        return None         

    #抓取投资组合信息
    print("\n  Searching information for portfolio:",portfolio)
    reg=get_portfolio_prices(portfolio,start,end)
    if reg is None:
        print("  #Error(liquidity_rolling): failed to get portfolio info")              
        return None          
    
    #滚动计算
    print("  Calculating its rolling ratios:",liquidity_type)
    import pandas as pd; import numpy as np
    datelist=reg.index.to_list()
    calc_func='calc_'+liquidity_type
    
    liqs=pd.DataFrame(columns=('Portfolio','Date','Ratio','Type')) 
    for i in np.arange(0,len(reg)):
        i1=i+window
        if i1 >= len(reg): break
        
        #构造滚动窗口
        windf=reg[reg.index >= datelist[i]]
        windf=windf[windf.index < datelist[i1]]
        #print(i,datelist[i],i1,datelist[i1],len(windf))
        
        #使用滚动窗口计算
        liq=eval(calc_func)(windf)
        if liq is None: continue
        
        #记录计算结果
        row=pd.Series({'Portfolio':portfolio,'Date':datelist[i1-1],'Ratio':liq,'Type':liquidity_type})
        liqs=liqs.append(row,ignore_index=True)        
    
    liqs.set_index(['Date'],inplace=True) 
    
    #第6步：绘图
    if graph == True:
        draw_liquidity(liqs)
    
    return liqs


if __name__=='__main__':
    portfolio={'Market':('US','^GSPC'),'AAPL':0.5,'MSFT':0.3,'IBM':0.2}
    start='2019-1-1'
    end='2019-6-30'
    window=30
    graph=True    
    liquidity_type='roll_spread'
    liqs=liquidity_rolling(portfolio,start,end,liquidity_type)


#==============================================================================
#==============================================================================



def compare_liquidity_rolling(portfolio1,portfolio2,start,end,liquidity_type,window=30):
    """
    功能：比较两个投资组合portfolio1和portfolio2在start至end期间的流动性指标liquidity_type
    """
    #投资组合1
    liqs1=liquidity_rolling(portfolio1,start,end,liquidity_type, \
                      window=window,graph=False)
    if liqs1 is None:
        print("  #Error(compare_liquidity_rolling): portfolio info inaccesible for",portfolio1)
        return 
    
    colname1='Ratio'
    label1=ectranslate(liquidity_type)
    datatag1=False
    
    zeroline=False
    neg_liqs1=liqs1[liqs1['Ratio'] < 0]
    if len(neg_liqs1) > 0: zeroline=True
   
    #投资组合2
    liqs2=liquidity_rolling(portfolio2,start,end,liquidity_type, \
                      window=window,graph=False)
    if liqs2 is None:
        print("  #Error(compare_liquidity_rolling): portfolio info inaccesible for",portfolio2)
        return     
    
    colname2='Ratio'
    label2=ectranslate(liquidity_type)
    datatag2=False
    
    zeroline=False
    neg_liqs2=liqs2[liqs2['Ratio'] < 0]
    if len(neg_liqs2) > 0: zeroline=True

    #绘图    
    ylabeltxt=ectranslate(liquidity_type)
    titletxt="证券流动性风险的滚动趋势比较"
    
    _,_,tickerlist1,sharelist1=decompose_portfolio(portfolio1)
    if len(tickerlist1)==1:
        product1=str(codetranslate(tickerlist1))
    else:
        product1=str(codetranslate(tickerlist1))+'，持仓'+str(sharelist1)    
    _,_,tickerlist2,sharelist2=decompose_portfolio(portfolio2)
    if len(tickerlist2)==1:
        product2=str(codetranslate(tickerlist2))
    else:
        product2=str(codetranslate(tickerlist2))+'，持仓'+str(sharelist2)     
    
    import datetime as dt; today=dt.date.today()
    footnote="证券1="+product1+"\n证券2="+product2+ \
            "\n数据来源：新浪/stooq, "+str(today)
    power=0 #不绘制趋势线

    plot_line2_coaxial(liqs1,"证券1",colname1,label1, \
                       liqs2,"证券2",colname2,label2, \
                ylabeltxt,titletxt,footnote,power,datatag1,datatag2,zeroline)
    return
    
    

if __name__ =="__main__":
    portfolio1={'Market':('US','^GSPC'),'PDD':1.0}
    portfolio2={'Market':('US','^GSPC'),'BILI':1.0}
    start='2020-1-01'
    end='2020-6-30'
    window=21
    graph=False
    liquidity_type='roll_spread'   
    compare_liquidity_rolling(portfolio1,portfolio2,start,end,liquidity_type)

    liquidity_type='amihud_illiquidity'   
    compare_liquidity_rolling(portfolio1,portfolio2,start,end,liquidity_type)    

    liquidity_type='ps_liquidity'   
    compare_liquidity_rolling(portfolio1,portfolio2,start,end,liquidity_type)    
#==============================================================================
#==============================================================================


