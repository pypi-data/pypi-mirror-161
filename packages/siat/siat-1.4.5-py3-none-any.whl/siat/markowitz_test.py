# -*- coding: utf-8 -*-

#==============================================================================
import os; os.chdir("S:/siat"); from siat import *
#==============================================================================

#定义投资组合：我的组合001
Market={'Market':('US','^GSPC','自选组合1号')}
Stocks1={'AAPL':.02,'MSFT':.01,'AMZN':.03,'FB':.04,'GOOG':.05}
Stocks2={'XOM':.2,'JNJ':.24,'JPM':.05,'TSLA':.06,'SBUX':.3}
portfolio=dict(Market,**Stocks1,**Stocks2)

#比较业绩表现：我的组合001，等权重组合，流动性组合
pf_info=portfolio_expret(portfolio,'2019-12-31')
pf_info_noRF=portfolio_expret(portfolio,'2019-12-31',RF=False)

#观察投资组合成分股收益率之间的相关性
portfolio_corr(pf_info)
portfolio_corr(pf_info_noRF)

#观察马科维茨可行集：收益率-标准差，接近椭圆形，可用于解释有效边界（左上沿）
es=portfolio_es(pf_info,simulation=50000)
#------------------------------------------------------------------------------

portfolio_optimize_strategy(pf_info,ratio='sharpe',simulation=1000)
portfolio_optimize_strategy(pf_info,ratio='sharpe',simulation=1000,RF=False)

portfolio_optimize_strategy(pf_info,ratio='sortino',simulation=1000)
portfolio_optimize_strategy(pf_info,ratio='sortino',simulation=1000,RF=False)

portfolio_optimize_strategy(pf_info,ratio='alpha',simulation=1000)
portfolio_optimize_strategy(pf_info,ratio='alpha',simulation=1000,RF=False)

portfolio_optimize_strategy(pf_info,ratio='treynor',simulation=1000)
portfolio_optimize_strategy(pf_info,ratio='treynor',simulation=1000,RF=False)


#------------------------------------------------------------------------------
#详细过程

#观察马科维茨可行集：风险溢价-标准差，用于夏普比率优化
es_sharpe=portfolio_es_sharpe(pf_info,simulation=50000)
[[portfolio,_,_,_],_]=pf_info
pname=portfolio_name(portfolio)

#寻找夏普比率最优点：最大夏普比率策略MSR和最小风险策略GMV
MSR_weights,GMVS_weights,portfolio_returns_sharpe=portfolio_optimize_sharpe(es_sharpe)

#现有投资组合的排名
portfolio_ranks(portfolio_returns_sharpe)

#打印业绩表现：MSR组合和GMV组合
portfolio_expectation2('MSR组合',pf_info,MSR_weights)
portfolio_expectation2('GMVS组合',pf_info,GMV_weights)

#绘制投资组合策略业绩比较曲线
name_list=[pname,'MSR组合','GMVS组合']
portfolio_expret_plot(portfolio_returns_sharpe,name_list)

#------------------------------------------------------------------------------
#观察马科维茨可行集：索替诺比率优化
es_sortino=portfolio_es_sortino(pf_info,simulation=50000)

#寻找比率最优点：
MSO_weights,GML_weights,portfolio_returns_sortino=portfolio_optimize_sortino(es_sortino)

#现有投资组合的排名
portfolio_ranks(portfolio_returns_sortino)

#打印业绩表现：MSO组合和GML组合
portfolio_expectation2('MSO组合',pf_info,MSO_weights)
portfolio_expectation2('GML组合',pf_info,GML_weights)

#绘制投资组合策略业绩比较曲线
portfolio_expret_plot(portfolio_returns_sortino)

#------------------------------------------------------------------------------
#观察马科维茨可行集：阿尔法优化
es_alpha=portfolio_es_alpha(pf_info,simulation=50000)

#寻找比率最优点：
MAR_weights,GMBA_weights,portfolio_returns_alpha=portfolio_optimize_alpha(es_alpha)

#现有投资组合的排名
portfolio_ranks(portfolio_returns_alpha)

#打印业绩表现：MAR组合和GMB组合
portfolio_expectation2('MAR组合',pf_info,MAR_weights)
portfolio_expectation2('GMBA组合',pf_info,GMB_weights)

#绘制投资组合策略业绩比较曲线
portfolio_expret_plot(portfolio_returns_alpha)

#------------------------------------------------------------------------------
#观察马科维茨可行集：特雷诺比率优化
es_treynor=portfolio_es_treynor(pf_info,simulation=50000)

#寻找比率最优点：
MTR_weights,GMBT_weights,portfolio_returns_treynor=portfolio_optimize_treynor(es_treynor)

#现有投资组合的排名
portfolio_ranks(portfolio_returns_treynor)

#打印业绩表现：MTR组合和GMB2组合
portfolio_expectation2('MTR组合',pf_info,MTR_weights)
portfolio_expectation2('GMBT组合',pf_info,GMB2_weights)

#绘制投资组合策略业绩比较曲线
portfolio_expret_plot(portfolio_returns_treynor)





#==============================================================================
import os; os.chdir("S:/siat")
from siat.markowitz import *

Market={'Market':('US','^GSPC')}
Stocks={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09,'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
portfolio=dict(Market,**Stocks)

pf_info=portfolio_cumret(portfolio,'2019-12-31')
portfolio_covar(pf_info)
portfolio_corr(pf_info)
portfolio_expectation(pf_info)

es_info=portfolio_es(pf_info,simulation=50000)

df=portfolio_MSR_GMV(es_info)

stocks=['IBM','WMT','AAPL','C','MSFT']
ef=portfolio_ef(stocks,'2019-1-1','2020-8-1')





_,_,tickerlist,sharelist=decompose_portfolio(portfolio)

today='2020-12-31'
pastyears=1

pf_info=portfolio_cumret(portfolio,'2020-12-31')

portfolio_covar(pf_info)

portfolio_corr(pf_info)


#定义投资组合
Market={'Market':('US','^GSPC')}
Stocks={'BABA':.4,'JD':.3,'PDD':.2,'VIPS':.1}
portfolio=dict(Market,**Stocks)

#搜寻该投资组合中所有成分股的价格信息，默认观察期为一年，pastyears=1
pf_info=portfolio_cumret(portfolio,'2020-11-30',pastyears=1)

#生成了投资组合的可行集
es_info=portfolio_es(pf_info,simulation=50000)
es_info10=portfolio_es(pf_info,simulation=100000)

#寻找投资组合的MSR优化策略点和GMV优化策略点
psr=portfolio_MSR_GMV(es_info)
