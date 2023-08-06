# -*- coding: utf-8 -*-

#==============================================================================
import os; os.chdir("S:/siat"); from siat import *
#==============================================================================

#启用Python的证券爬虫和分析工具
from siat import *

#定义投资组合：银行概念基金1号
Market={'Market':('China','000300.SS','银行概念基金1号')}
Stocks1={'601939.SS':.3,'601398.SS':.2,'601288.SS':.15,'601988.SS':.1}
Stocks2={'601328.SS':.1,'000001.SZ':.05,'601168.SS':.05,'601229.SS':.05}
portfolio=dict(Market,**Stocks1,**Stocks2)

#比较业绩表现：银行概念基金1号，等权重组合，流动性组合
pf_info=portfolio_expret(portfolio,'2021-12-3')

#观察投资组合成分股收益率之间的相关性
portfolio_corr(pf_info)

#观察马科维茨可行集：收益率-标准差，接近椭圆形，可用于解释有效边界（左上沿）
es=portfolio_es(pf_info,simulation=5000)
#------------------------------------------------------------------------------

portfolio_optimize_strategy(pf_info,ratio='sharpe',simulation=1000)

portfolio_optimize_strategy(pf_info,ratio='sortino',simulation=1000)
portfolio_optimize_strategy(pf_info,ratio='sortino',simulation=1000,RF=False)

portfolio_optimize_strategy(pf_info,ratio='alpha',simulation=1000)
portfolio_optimize_strategy(pf_info,ratio='alpha',simulation=1000,RF=False)

portfolio_optimize_strategy(pf_info,ratio='treynor',simulation=1000)
portfolio_optimize_strategy(pf_info,ratio='treynor',simulation=1000,RF=False)


