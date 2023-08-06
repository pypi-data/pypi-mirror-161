# -*- coding: utf-8 -*-
"""
本模块功能：证券投资组合理论计算函数包
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2020年7月1日
最新修订日期：2020年7月29日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
作者邮件：wdehong2000@163.com
版权所有：王德宏
用途限制：仅限研究与教学使用，不可商用！商用需要额外授权。
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""
#==============================================================================
#统一屏蔽一般性警告
import warnings; warnings.filterwarnings("ignore")   
#==============================================================================
  
from siat.common import *
from siat.translate import *
from siat.security_prices import *

import pandas as pd
import datetime
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
#==============================================================================
def portfolio_config(tickerlist,sharelist):
    """
    将股票列表tickerlist和份额列表sharelist合成为一个字典
    """
    #整理sharelist的小数点
    ratiolist=[]
    for s in sharelist:
        ss=round(s,4); ratiolist=ratiolist+[ss]
    #合成字典
    new_dict=dict(zip(tickerlist,ratiolist))
    return new_dict

#==============================================================================
def ratiolist_round(sharelist,num=4):
    """
    将股票份额列表sharelist中的数值四舍五入
    """
    #整理sharelist的小数点
    ratiolist=[]
    for s in sharelist:
        ss=round(s,num); ratiolist=ratiolist+[ss]
    return ratiolist

#==============================================================================
def varname(p):
    """
    功能：获得变量的名字本身。
    """
    import inspect
    import re    
    for line in inspect.getframeinfo(inspect.currentframe().f_back)[3]:
        m = re.search(r'\bvarname\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)', line)
        if m:
            return m.group(1)    

#==============================================================================
def get_start_date(end_date,pastyears=1):
    """
    输入参数：一个日期，年数
    输出参数：几年前的日期
    start_date, end_date是datetime类型
    """
    import pandas as pd
    try:
        end_date=pd.to_datetime(end_date)
    except:
        print("#Error(): invalid date,",end_date)
        return None
    
    from datetime import datetime,timedelta
    start_date=datetime(end_date.year-pastyears,end_date.month,end_date.day)
    start_date=start_date-timedelta(days=1)
    # 日期-1是为了保证计算收益率时得到足够的样本数量
    return start_date

#==============================================================================
if __name__=='__main__':
    retgroup=StockReturns

def cumulative_returns_plot(retgroup,name_list,titletxt,ylabeltxt,xlabeltxt, \
                            label_list=[]):
    """
    功能：基于传入的name_list绘制多条累计收益率曲线，并从label_list中取出曲线标记
    注意：最多绘制四条曲线，否则在黑白印刷时无法区分曲线
    """
    if len(label_list) < len(name_list):
        label_list=name_list
    
    # 累积收益曲线绘制函数
    lslist=['-','--',':','-.']
    for name in name_list:
        pos=name_list.index(name)
        rlabel=label_list[pos]
        if pos < 4: thisls=lslist[pos]        
        else: thisls=(45,(55,20))
            
        CumulativeReturns = ((1+retgroup[name]).cumprod()-1)*100.0
        CumulativeReturns.plot(label=ectranslate(rlabel),ls=thisls)
    #plt.axhline(y=0,ls=":",c="red")
    plt.legend(loc='best')
    plt.title(titletxt); plt.ylabel(ylabeltxt); plt.xlabel(xlabeltxt)
    plt.show()
    
    return

if __name__=='__main__':
    retgroup=StockReturns
    cumulative_returns_plot(retgroup,name_list,titletxt,ylabeltxt,xlabeltxt, \
                            label_list=[])
#==============================================================================
if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks={'BABA':.7,'JD':.3}
    portfolio=dict(Market,**Stocks)
    
    today='2021-1-28'
    pastyears=1

def portfolio_cumret(portfolio,today,pastyears=1):
    """
    功能：绘制投资组合的累计收益率趋势图，并与等权和市值加权组合比较
    """
    print("\n  Searching for portfolio info, which may take time ...")
    # 解构投资组合
    _,_,tickerlist,sharelist=decompose_portfolio(portfolio)
    pname=portfolio_name(portfolio)

    totalshares=round(sum(sharelist),4)
    if totalshares != 1.0:
        print("\n  #Error(portfolio_cumret): total weights is",totalshares,", it requires 1.0 here")
        return None       
    
    # 计算历史数据的开始日期
    start=get_start_date(today,pastyears)
    
    # 抓取投资组合股价
    """
    StockReturns=get_portfolio_prices(portfolio,start,today)
    """
    prices=get_prices(tickerlist,start,today)
    if prices is None:
        print("\n  #Error(portfolio_cumret): failed to get portfolio prices",pname)
        return None
    if len(prices) == 0:
        print("\n  #Error(portfolio_cumret): retrieved empty prices for",pname)
        return None
    
    # 复权后收盘价
    aclose=prices['Close']    
    #print(aclose.head())
    # 计算每日收益率，并丢弃缺失值
    StockReturns = aclose.pct_change().dropna()
    if len(StockReturns) == 0:
        print("\n  #Error(portfolio_cumret): retrieved empty returns for",pname)
        return None
    #print(StockReturns.head())
    # 将收益率数据拷贝到新的变量 stock_return 中，为了后续调用的方便
    stock_return = StockReturns.copy()
    #..........................................................................
    
    # 设置组合权重，存储为numpy数组类型
    import numpy as np
    portfolio_weights = np.array(sharelist)
    # 计算portfolio的股票收益
    WeightedReturns = stock_return.mul(portfolio_weights, axis=1)
    # 计算投资组合的收益
    StockReturns['Portfolio'] = WeightedReturns.sum(axis=1)
    
    # 绘制portfolio随时间变化的图
    #仅用于绘图，以便使用收益率%来显示
    plotsr = StockReturns['Portfolio']*100.0
    #plotsr = StockReturns['Ret%']
    #plotsr.plot(label='Portfolio')
    plotsr.plot(label=pname)
    plt.axhline(y=0,ls=":",c="red")
    
    plt.title("投资组合: 日收益率的变化趋势")
    plt.ylabel("日收益率%")
    
    stoday = datetime.date.today()
    plt.xlabel("数据来源: 新浪/stooq/FRED, "+str(stoday))
    plt.legend()
    plt.show()
    #..........................................................................
    
    # 计算持有收益率的组合收益，并绘图
    name_list=["Portfolio"]
    label_list=[pname]
    titletxt="投资组合: 持有收益率的变化趋势"
    ylabeltxt="持有收益率%"
    stoday = datetime.date.today()
    xlabeltxt="数据来源: 新浪/stooq/FRED, "+str(stoday)
    #由函数去处理百分号放大
    cumulative_returns_plot(StockReturns,name_list,titletxt,ylabeltxt,xlabeltxt,label_list)
    #..........................................................................
    
    # 构造等权重组合Portfolio_EW
    numstocks = len(tickerlist)
    # 平均分配每一项的权重
    portfolio_weights_ew = np.repeat(1/numstocks, numstocks)
    # 计算等权重组合的收益
    StockReturns['Portfolio_EW']=stock_return.mul(portfolio_weights_ew,axis=1).sum(axis=1)
    #StockReturns['Portfolio_name']=pname
    #name_list=['Portfolio','Portfolio_EW']
    #cumulative_returns_plot(StockReturns,name_list,titletxt,ylabeltxt,xlabeltxt)
    #..........................................................................
    
    # 创建流动性组合：按照成交金额计算流动性
    MCap=prices['Close']*prices['Volume']
    #MCaplist=MCap.iloc[-1]
    MCaplist=MCap.mean(axis=0)    #求列的均值
    market_capitalizations = np.array(MCaplist)
    # 计算成交金额权重
    mcap_weights = market_capitalizations / np.sum(market_capitalizations)
    # 计算成交金额加权的组合收益
    StockReturns['Portfolio_LW'] = stock_return.mul(mcap_weights, axis=1).sum(axis=1)

    #绘制累计收益率对比曲线
    name_list=['Portfolio', 'Portfolio_EW', 'Portfolio_LW']
    label_list=[pname, '等权重组合', '流动性组合']
    titletxt="投资组合: 不同组合策略的持有收益率对比"
    cumulative_returns_plot(StockReturns,name_list,titletxt,ylabeltxt,xlabeltxt,label_list)

    return [tickerlist,sharelist,StockReturns,stock_return,today, \
            [portfolio_weights,portfolio_weights_ew,mcap_weights]]

if __name__=='__main__':
    X=portfolio_cumret(portfolio,'2021-1-28')

if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    pf_info=portfolio_cumret(portfolio,'2019-12-31')


def portfolio_expret(portfolio,today,pastyears=1):
    """
    功能：绘制投资组合的持有期收益率趋势图，并与等权和市值加权组合比较
    套壳原来的portfolio_cumret函数，以维持兼容性
    expret: expanding return，以维持与前述章节名词的一致性
    hpr: holding period return, 持有（期）收益率
    """
    [tickerlist,sharelist,StockReturns,stock_return,today, \
            [portfolio_weights,portfolio_weights_ew,mcap_weights]] = \
                portfolio_cumret(portfolio,today,pastyears)

    return [tickerlist,sharelist,StockReturns,stock_return,today, \
            [portfolio_weights,portfolio_weights_ew,mcap_weights]]

if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    
    pf_info=portfolio_expret(portfolio,'2019-12-31')


#==============================================================================
def portfolio_corr(pf_info):
    """
    功能：绘制投资组合成分股之间相关关系的热力图
    """
    [_,_,StockReturns,stock_return,today,_]=pf_info
    pname=StockReturns['Portfolio_name'].values[0]
        
    sr=stock_return.copy()
    collist=list(sr)
    for col in collist:
        sr.rename(columns={col:codetranslate(col)},inplace=True)

    # 计算相关矩阵
    #correlation_matrix = stock_return.corr()
    correlation_matrix = sr.corr()
    
    # 导入seaborn
    import seaborn as sns
    # 创建热图
    sns.heatmap(correlation_matrix,annot=True,cmap="YlGnBu",linewidths=0.3,
            annot_kws={"size": 8})
    plt.title(pname+": 成分股收益率之间的相关系数")
    plt.ylabel("成分股票")
    import datetime as dt; stoday=dt.date.today()    
    plt.xlabel("数据来源：新浪/EM/stooq，"+str(stoday))
    plt.xticks(rotation=90); plt.yticks(rotation=0) 
    plt.show()

    return    

if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    pf_info=portfolio_expret(portfolio,'2019-12-31')
    
    portfolio_corr(pf_info)
#==============================================================================
def portfolio_covar(pf_info):
    """
    功能：计算投资组合成分股之间的协方差
    """
    [_,_,StockReturns,stock_return,today,_]=pf_info
    pname=StockReturns['Portfolio_name'].values[0]

    # 计算协方差矩阵
    cov_mat = stock_return.cov()
    # 年化协方差矩阵，252个交易日
    cov_mat_annual = cov_mat * 252
    
    # 导入seaborn
    import seaborn as sns
    # 创建热图
    sns.heatmap(cov_mat_annual,annot=True,cmap="YlGnBu",linewidths=0.3,
            annot_kws={"size": 8})
    plt.title(pname+": 成分股之间的协方差")
    plt.ylabel("成分股票")
    
    import datetime as dt; stoday=dt.date.today()    
    plt.xlabel("数据来源：新浪/EM/stooq，"+str(stoday))
    plt.xticks(rotation=90)
    plt.yticks(rotation=0) 
    plt.show()

    return 

#==============================================================================
def portfolio_expectation(pf_info):
    """
    功能：计算投资组合的标准差
    """
    [tickerlist,sharelist,StockReturns,stock_return,today,[portfolio_weights,_,_]]=pf_info
    pname=StockReturns['Portfolio_name'].values[0]
    
    #取出观察期
    hstart0=StockReturns.index[0]
    hstart=str(hstart0.date())
    hend0=StockReturns.index[-1]
    hend=str(hend0.date())

    mean_return=stock_return.mul(portfolio_weights,axis=1).sum(axis=1).mean()
    annual_return = (1 + mean_return)**252 - 1
    
    # 计算协方差矩阵
    cov_mat = stock_return.cov()
    # 年化协方差矩阵
    cov_mat_annual = cov_mat * 252

    # 计算投资组合的标准差
    import numpy as np
    portfolio_volatility = np.sqrt(np.dot(portfolio_weights.T, 
                                      np.dot(cov_mat_annual, portfolio_weights)))
    print("\n  ===== 投资组合的预期收益与预期风险 =====")
    print("  投资组合:",pname)
    #print("  成分股：",codetranslate(tickerlist))
    #print("  权重:",sharelist)
    print("  观察期  :",hstart+'至'+hend)
    print("  预期收益:",round(annual_return,4))
    print("  预期风险:",round(portfolio_volatility,4))
    
    import datetime as dt; stoday=dt.date.today()    
    print("  *数据来源：新浪/EM/stooq，"+str(stoday))

    return 

if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    pf_info=portfolio_expret(portfolio,'2019-12-31')
    
    portfolio_expectation(pf_info)
#==============================================================================
if __name__=='__main__':
    simulation=1000

def portfolio_es(pf_info,simulation=1000):
    """
    功能：计算投资组合的标准差，绘制投资组合的有效集
    """
    [tickerlist,_,StockReturns,stock_return,today,_]=pf_info
    pname=StockReturns['Portfolio_name'].values[0]
    #通过列名列表获得成分股个数
    numstocks=len(tickerlist)

    # 计算协方差矩阵
    cov_mat = stock_return.cov()
    # 年化协方差矩阵
    cov_mat_annual = cov_mat * 252

    # 设置模拟的次数
    number = simulation
    # 设置空的numpy数组，用于存储每次模拟得到的成分股权重、组合的收益率和标准差
    import numpy as np
    random_p = np.empty((number,numstocks+2))
    # 设置随机数种子，这里是为了结果可重复
    np.random.seed(123)

    # 循环模拟n次随机的投资组合
    print("\n  Calculating possible portfolio combinations, please wait ...")    
    for i in range(number):
        # 生成numstocks个随机数，并归一化，得到一组随机的权重数据
        random9 = np.random.random(numstocks)
        random_weight = random9 / np.sum(random9)
    
        # 计算年化平均收益率
        mean_return=stock_return.mul(random_weight,axis=1).sum(axis=1).mean()
        annual_return = (1 + mean_return)**252 - 1

        # 计算年化的标准差，也称为波动率
        random_volatility=np.sqrt(np.dot(random_weight.T, 
                                np.dot(cov_mat_annual,random_weight)))

        # 将上面生成的权重，和计算得到的收益率、标准差存入数组random_p中
        random_p[i][:numstocks] = random_weight
        random_p[i][numstocks] = annual_return
        random_p[i][numstocks+1] = random_volatility
    
    # 将numpy数组转化成DataFrame数据框
    import pandas as pd
    RandomPortfolios = pd.DataFrame(random_p)
    # 设置数据框RandomPortfolios每一列的名称
    RandomPortfolios.columns = [ticker + "_weight" for ticker in tickerlist]  \
                         + ['Returns', 'Volatility']

    # 绘制散点图
    RandomPortfolios.plot('Volatility','Returns',kind='scatter',color='y',edgecolors='k')
    """
    plt.style.use('seaborn-dark')
    RandomPortfolios.plot.scatter(x='Volatility', y='Returns', c='Returns',
                cmap='RdYlGn', edgecolors='black')
    """
    plt.title("投资组合: 马科维茨可行集")
    plt.ylabel("预期收益")
    
    import datetime as dt; stoday=dt.date.today()
    footnote1="预期风险-->"
    footnote2="\n基于"+pname+"之成分股构造，共"+str(simulation)+"个"
    footnote3="\n数据来源: 新浪/EM/stooq, "+str(stoday)
    plt.xlabel(footnote1+footnote2+footnote3)
    plt.show()

    return [pf_info,RandomPortfolios]

if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    pf_info=portfolio_expret(portfolio,'2019-12-31')
    
    es_info=portfolio_es(pf_info,simulation=50000)
#==============================================================================
def portfolio_GMV(es_info):
    """
    功能：计算投资组合的最小风险组合
    GMV=Global Minimium Variance
    """
    [[tickerlist,sharelist,StockReturns,stock_return,today, \
          [portfolio_weights,portfolio_weights_ew,mcap_weights]], \
          RandomPortfolios]=es_info
    pname=StockReturns['Portfolio_name'].values[0]
    numstocks=len(tickerlist)
    
    #取出观察期
    hstart0=StockReturns.index[0]
    hstart=str(hstart0.date())
    hend0=StockReturns.index[-1]
    hend=str(hend0.date())
        
    # 绘制散点图
    RandomPortfolios.plot('Volatility','Returns',kind='scatter',color='y',edgecolors='k')

    # 找到标准差最小数据的索引值
    min_index = RandomPortfolios.Volatility.idxmin()
    # 在收益-风险散点图中突出风险最小的点
    x = RandomPortfolios.loc[min_index,'Volatility']
    y = RandomPortfolios.loc[min_index,'Returns']
    plt.scatter(x, y, color='m',marker='8',s=100,label="GMV Point",edgecolors='r')   

    plt.title("投资组合: GMV点的位置")
    plt.ylabel("预期收益")
    plt.xlabel("预期风险-->\nGMV表示风险最低的组合方式(Global Minimium Variance). \
               \n数据来源: 新浪/stooq, "+str(today))
    plt.legend()
    plt.show()

    # 提取最小波动组合对应的权重, 并转换成Numpy数组
    import numpy as np
    GMV_weights = np.array(RandomPortfolios.iloc[min_index, 0:numstocks])
    # 计算GMV投资组合收益
    StockReturns['Portfolio_GMV'] = stock_return.mul(GMV_weights, axis=1).sum(axis=1)
    # 绘制累积收益曲线
    namelist=['Portfolio_GMV', 'Portfolio']
    titletxt="投资组合: 累计收益率的比较"
    ylabeltxt="累计收益率"
    xlabeltxt="数据来源: 新浪/stooq, "+str(today)    
    cumulative_returns_plot(StockReturns,namelist,titletxt,ylabeltxt,xlabeltxt)

    #输出GMV投资组合构成比例
    print("\n===== GMV组合方式: 构造风险最低的投资组合 =====")
    print("成分股：",codetranslate(tickerlist))
    GMV_weights_new=ratiolist_round(GMV_weights,num=3)
    print("权重：",GMV_weights_new)
    print("观察期:",hstart+'至'+hend)
    print("预期收益:",round(y,4))
    print("预期风险:",round(x,4))

    import datetime as dt; today=dt.date.today()    
    print("*数据来源：新浪/stooq，"+str(today))

    return

#==============================================================================




def portfolio_MSR_GMV(es_info,RF=0):
    """
    功能：计算投资组合的最高夏普比率组合
    MSR: Maximium Sharpe Rate, 最高夏普指数方案
    GMV: Global Minimum Volatility, 全局最小波动方案
    """
    [[tickerlist,sharelist,StockReturns,stock_return,today, \
          [portfolio_weights,portfolio_weights_ew,mcap_weights]], \
          RandomPortfolios]=es_info
    numstocks=len(tickerlist)  
    pname=StockReturns['Portfolio_name'].values[0]
    
    #取出观察期
    hstart0=StockReturns.index[0]
    hstart=str(hstart0.date())
    hend0=StockReturns.index[-1]
    hend=str(hend0.date())
    
    # 设置无风险回报率
    risk_free = RF
    # 计算每项资产的夏普比率
    RandomPortfolios['Sharpe'] = (RandomPortfolios.Returns - risk_free)   \
                            / RandomPortfolios.Volatility

    # 绘制收益-标准差的散点图，并用颜色描绘夏普比率
    # 绘制散点图
    RandomPortfolios.plot('Volatility','Returns',kind='scatter',alpha=0.3)
    plt.scatter(RandomPortfolios.Volatility, RandomPortfolios.Returns, 
            c=RandomPortfolios.Sharpe)
    plt.colorbar(label='Colored in Sharpe Ratio')
    plt.title("投资组合: 马科维茨可行集的夏普比率分布")
    plt.ylabel("预期收益")
    plt.xlabel("预期风险-->"+ \
               "\n观察期："+hstart+"至"+hend+ \
               "\n数据来源: 新浪/stooq, "+str(today))     
    plt.show()

    #绘制有效集
    RandomPortfolios.plot('Volatility','Returns',kind='scatter',color='y',edgecolors='k')

    # 找到夏普比率最大数据对应的索引值
    max_index = RandomPortfolios.Sharpe.idxmax()
    # 在收益-风险散点图中突出夏普比率最大的点
    MSR_x = RandomPortfolios.loc[max_index,'Volatility']
    MSR_y = RandomPortfolios.loc[max_index,'Returns']
    plt.scatter(MSR_x, MSR_y, color='red',marker='*',s=150,label="MSR Point")  
    # 提取最大夏普比率组合对应的权重，并转化为numpy数组
    import numpy as np    
    MSR_weights = np.array(RandomPortfolios.iloc[max_index, 0:numstocks])
    # 计算MSR组合的收益
    StockReturns['Portfolio_MSR'] = stock_return.mul(MSR_weights, axis=1).sum(axis=1)
    
    # 找到标准差最小数据的索引值
    min_index = RandomPortfolios.Volatility.idxmin()
    # 提取最小波动组合对应的权重, 并转换成Numpy数组
    # 在收益-风险散点图中突出风险最小的点
    GMV_x = RandomPortfolios.loc[min_index,'Volatility']
    GMV_y = RandomPortfolios.loc[min_index,'Returns']
    plt.scatter(GMV_x, GMV_y, color='m',marker='8',s=100,label="GMV Point") 
    # 提取最小风险组合对应的权重，并转化为numpy数组
    GMV_weights = np.array(RandomPortfolios.iloc[min_index, 0:numstocks])
    # 计算GMV投资组合收益
    StockReturns['Portfolio_GMV'] = stock_return.mul(GMV_weights, axis=1).sum(axis=1)

    plt.title("投资组合: MSR点和GMV点的位置")
    plt.ylabel("预期收益")
    plt.xlabel("预期风险-->"+ \
               "\n观察期："+hstart+"至"+hend+ \
               "\n数据来源: 新浪/stooq, "+str(today))    
    plt.legend()
    plt.show()

    # 绘制累积收益曲线
    namelist=['Portfolio_MSR','Portfolio_GMV','Portfolio']
    titletxt="投资组合: 累计收益率的比较"
    ylabeltxt="累计收益率"
    xlabeltxt="观察期："+hstart+"至"+hend+ \
              "\n数据来源: 新浪/stooq, "+str(today)      
    cumulative_returns_plot(StockReturns,namelist,titletxt,ylabeltxt,xlabeltxt)    

    #输出MSR投资组合构成比例
    print("\n===== 投资组合的构造方式: 最高夏普比率(MSR) =====")
    print("成分股：",codetranslate(tickerlist))
    MSR_weights_new=ratiolist_round(MSR_weights,3)
    print("权重：",MSR_weights_new)
    print("观察期:",hstart+"至"+hend)
    print("预期收益:",round(MSR_y*100.0,2),'\b%')
    print("预期风险:",round(MSR_x*100.0,2),'\b%')

    #import datetime as dt; today=dt.date.today()    
    print("*数据来源：新浪/stooq，"+str(today))

    #输出GMV投资组合构成比例
    print("\n===== 投资组合的构造方式: 风险最小化(GMV) =====")
    print("成分股：",codetranslate(tickerlist))
    GMV_weights_new=ratiolist_round(GMV_weights,3)
    print("权重：",GMV_weights_new)
    print("观察期:",hstart+"至"+hend)
    print("预期收益:",round(GMV_y*100.0,2),'\b%')
    print("预期风险:",round(GMV_x*100.0,2),'\b%')    
    print("*数据来源：新浪/stooq，"+str(today))
    
    return StockReturns

#==============================================================================
def translate_tickerlist(tickerlist):
    newlist=[]
    for t in tickerlist:
        name=codetranslate(t)
        newlist=newlist+[name]
        
    return newlist
#==============================================================================
# 绘制马科维茨有效边界
#==============================================================================
def ret_monthly(ticker,prices): 
    """
    功能：
    """
    price=prices['Adj Close'][ticker]
    
    import numpy as np
    div=price.pct_change()+1
    logret=np.log(div)
    import pandas as pd
    lrdf=pd.DataFrame(logret)
    lrdf['ymd']=lrdf.index.astype("str")
    lrdf['ym']=lrdf['ymd'].apply(lambda x:x[0:7])
    lrdf.dropna(inplace=True)
    
    mret=lrdf.groupby(by=['ym'])[ticker].sum()
    
    return mret

if __name__=='__main__':
    ticker='MSFT'
    fromdate,todate='2019-1-1','2020-8-1'

#==============================================================================
def objFunction(W,R,target_ret):
    
    import numpy as np
    stock_mean=np.mean(R,axis=0)
    port_mean=np.dot(W,stock_mean) # portfolio mean
    
    cov=np.cov(R.T) # var-cov matrix
    port_var=np.dot(np.dot(W,cov),W.T) # portfolio variance
    penalty = 2000*abs(port_mean-target_ret)# penalty 4 deviation
    
    objfunc=np.sqrt(port_var) + penalty # objective function 
    
    return objfunc   

#==============================================================================
def portfolio_ef_0(stocks,fromdate,todate):
    """
    功能：绘制马科维茨有效前沿，不区分上半沿和下半沿
    """
    #Code for getting stock prices
    prices=get_prices(stocks,fromdate,todate)
    
    #Code for generating a return matrix R
    R0=ret_monthly(stocks[0],prices) # starting from 1st stock
    n_stock=len(stocks) # number of stocks
    import pandas as pd
    import numpy as np
    for i in range(1,n_stock): # merge with other stocks
        x=ret_monthly(stocks[i],prices)
        R0=pd.merge(R0,x,left_index=True,right_index=True)
        R=np.array(R0)    

    #Code for estimating optimal portfolios for a given return
    out_mean,out_std,out_weight=[],[],[]
    import numpy as np
    stockMean=np.mean(R,axis=0)
    
    from scipy.optimize import minimize
    for r in np.linspace(np.min(stockMean),np.max(stockMean),num=100):
        W = np.ones([n_stock])/n_stock # starting from equal weights
        b_ = [(0,1) for i in range(n_stock)] # bounds, here no short
        c_ = ({'type':'eq', 'fun': lambda W: sum(W)-1. }) #constraint
        result=minimize(objFunction,W,(R,r),method='SLSQP'
                                    ,constraints=c_, bounds=b_)
        if not result.success: # handle error raise    
            BaseException(result.message)
        
        out_mean.append(round(r,4)) # 4 decimal places
        std_=round(np.std(np.sum(R*result.x,axis=1)),6)
        out_std.append(std_)
        out_weight.append(result.x)

    #Code for plotting the efficient frontier
    
    plt.title('Efficient Frontier of Portfolio')
    plt.xlabel('Standard Deviation of portfolio (Risk))')
    plt.ylabel('Return of portfolio')
    
    out_std_min=min(out_std)
    pos=out_std.index(out_std_min)
    out_mean_min=out_mean[pos]
    x_left=out_std_min+0.25
    y_left=out_mean_min+0.5
    
    #plt.figtext(x_left,y_left,str(n_stock)+' stock are used: ')
    plt.figtext(x_left,y_left,"投资组合由"+str(n_stock)+'种证券构成: ')
    plt.figtext(x_left,y_left-0.05,' '+str(stocks))
    plt.figtext(x_left,y_left-0.1,'观察期间：'+str(fromdate)+'至'+str(todate))
    plt.plot(out_std,out_mean,color='r',ls=':',lw=4)
    plt.show()    
    
    return

if __name__=='__main__':
    stocks=['IBM','WMT','AAPL','C','MSFT']
    fromdate,todate='2019-1-1','2020-8-1'    

#==============================================================================
def portfolio_ef(stocks,fromdate,todate):
    """
    功能：多只股票的马科维茨有效边界，区分上半沿和下半沿，标记风险极小点
    """
    print("\n...Searching for portfolio information, please wait...")
    #Code for getting stock prices
    prices=get_prices(stocks,fromdate,todate)
    
    #Code for generating a return matrix R
    R0=ret_monthly(stocks[0],prices) # starting from 1st stock
    n_stock=len(stocks) # number of stocks
    
    import pandas as pd
    import numpy as np
    for i in range(1,n_stock): # merge with other stocks
        x=ret_monthly(stocks[i],prices)
        R0=pd.merge(R0,x,left_index=True,right_index=True)
        R=np.array(R0)    

    #Code for estimating optimal portfolios for a given return
    out_mean,out_std,out_weight=[],[],[]
    stockMean=np.mean(R,axis=0)
    
    from scipy.optimize import minimize
    for r in np.linspace(np.min(stockMean),np.max(stockMean),num=100):
        W = np.ones([n_stock])/n_stock # starting from equal weights
        b_ = [(0,1) for i in range(n_stock)] # bounds, here no short
        c_ = ({'type':'eq', 'fun': lambda W: sum(W)-1. }) #constraint
        result=minimize(objFunction,W,(R,r),method='SLSQP'
                                    ,constraints=c_, bounds=b_)
        if not result.success: # handle error raise    
            BaseException(result.message)
        
        out_mean.append(round(r,4)) # 4 decimal places
        std_=round(np.std(np.sum(R*result.x,axis=1)),6)
        out_std.append(std_)
        out_weight.append(result.x)

    #Code for positioning
    out_std_min=min(out_std)
    pos=out_std.index(out_std_min)
    out_mean_min=out_mean[pos]
    x_left=out_std_min+0.25
    y_left=out_mean_min+0.5
    
    import pandas as pd
    out_df=pd.DataFrame(out_mean,out_std,columns=['mean'])
    out_df_ef=out_df[out_df['mean']>=out_mean_min]
    out_df_ief=out_df[out_df['mean']<out_mean_min]

    #Code for plotting the efficient frontier
    
    plt.title('投资组合：马科维茨有效边界')
    
    import datetime as dt; today=dt.date.today()    
    plt.xlabel('预期风险-->'+"\n数据来源：新浪/stooq, "+str(today))
    plt.ylabel('预期收益')
    
    plt.figtext(x_left,y_left,"投资组合由"+str(n_stock)+'种证券构成: ')
    plt.figtext(x_left,y_left-0.05,' '+str(stocks))
    plt.figtext(x_left,y_left-0.1,'观察期间：'+str(fromdate)+'至'+str(todate))
    plt.plot(out_df_ef.index,out_df_ef['mean'],color='r',ls='--',lw=2,label='有效边界')
    plt.plot(out_df_ief.index,out_df_ief['mean'],color='k',ls=':',lw=2,label='无效边界')
    plt.plot(out_std_min,out_mean_min,'g*-',markersize=16,label='风险最低点')
    
    plt.legend(loc='best')
    plt.show()    
    
    return out_df

if __name__=='__main__':
    stocks=['IBM','WMT','AAPL','C','MSFT']
    fromdate,todate='2019-1-1','2020-8-1'    


































