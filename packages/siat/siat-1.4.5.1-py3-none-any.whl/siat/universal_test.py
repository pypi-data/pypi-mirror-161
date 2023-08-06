# -*- coding: utf-8 -*-

"""
本地测试的简单方法：
1、卸载siat插件: pip uninstall siat
2、import os; os.chdir("S:/siat")
3、from siat import *
"""

import os; os.chdir("S:/siat")
from siat import *
#=====================================================================
df=oef_trend_china('050111','2021-7-1','2021-8-31',trend_type='排名',twinx=True)



#=====================================================================
compare_stock("MSFT", ["Open", "Close"], "2020-3-16", "2020-3-31")
prices = compare_stock(["DAI.DE","BMW.DE"], "Close", "2020-1-1", "2020-3-31")
compare_stock("7203.T", ["High", "Low"], "2020-3-1", "2020-3-31")
info=candlestick("00700.HK","2020-2-1","2020-3-31", mav=2, volume=True, style='blueskies')
compare_stock("IBM", ["Annual Ret%", "Daily Ret%"], "2019-1-1", "2019-12-31")
compare_stock(["JD", "AMZN"], "Exp Ret%", "2019-1-1", "2020-12-31")
compare_security(["FRI","^RUT"],"Exp Ret%","2010-1-1","2020-6-30")

compare_security(["GCZ25.CMX","GCZ24.CMX"],"Close","2020-1-1","2020-6-30")

compare_security(['^HSI','000001.SS'],"Close","1991-1-1","2021-2-28", twinx=True)
compare_security(['^TWII','000001.SS'],"Close","1997-1-1","2021-2-28", twinx=True)
compare_security(['^KS11','000001.SS'],"Close","1997-1-1","2021-2-28", twinx=True)
compare_security(['^BSESN','000001.SS'],"Close","1997-1-1","2021-2-28", twinx=True)
compare_security(['^FTSE','000001.SS'],"Close","1991-1-1","2021-2-28", twinx=True)

tickers=['AMZN','EBAY','SHOP','MELI','BABA','JD','VIPS','PDD']
roa=compare_snapshot(tickers,'ROA')

tat=compare_history(['AMZN','JD'],'Total Asset Turnover')

tickers=['600519.SS','000858.SZ','600779.SS','000596.SZ','603589.SS']
df=compare_dupont(tickers,fsdate='2020-12-31',scale1 = 10,scale2 = 10)

Market={'Market':('US','^GSPC')}
Stocks={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09,'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
portfolio=dict(Market,**Stocks)
pf_info=portfolio_cumret(portfolio,'2019-12-31')

beta=capm_beta('600000.SS','000001.SS','2011-1-1','2020-12-31')

members=['IBM','AAPL','MSFT']
shares=[1, 1, 3]
yearlist=gen_yearlist('2010','2020')
df=capm_beta_portfolio_yearly(members, shares,'^GSPC',yearlist)

yearlist=gen_yearlist('2011','2020')
betas_sw=get_beta_SW('4452.T','^N225', yearlist)

yearlist=gen_yearlist('2011','2019')
betas_sw= get_beta_SW('HMI.F','^FCHI', yearlist)
betas_sw=get_beta_SW('DIO.F','^FCHI', yearlist)

ff3_betas=reg_ff3_betas('BILI','2018-1-1','2019-4-30','US')

ff3_betas=reg_ff3_betas('AEM','2018-3-1','2019-8-31','US')

vix=security_price("^VIX", "2021-1-1", "2021-3-31",power=10)

var,ratio=stock_VaR_normal_standard('BABA',1000,'2019-8-8',1,0.99)

plot_rets_curve('01166.HK','2015-1-1','2015-3-31')

var, ratio=stock_VaR_normal_standard('ZM',1000,'2020-5-1',1,0.99)

var, r=stock_VaR_historical_grouping('00992.HK',1000,'2020-5-1',1,0.99, pastyears=3)

var, ratio=get_VaR_allmodels('01810.HK',1000,'2020-7-20',5,0.99)

pf_sohu={'Market':('US','^GSPC'),'SOHU':1.0}
rs15=roll_spread_portfolio(pf_sohu,'2015-1-1','2015-12-31')

portfolio={'Market':('US','^GSPC'),'DPW':0.4,'RIOT':0.3,'MARA':0.2,'NCTY':0.1}
sr,rp=rar_ratio_portfolio(portfolio,'2018-1-1','2020-12-31',ratio_name='sortino')








#=====================================================================
#=====================================================================
#=====================================================================
#=====================================================================

df_all=oef_rank_china(info_type='单位净值',fund_type='全部类型',rank=15)

df_z=oef_rank_china(info_type='单位净值',fund_type='债券型')
df_g=oef_rank_china('单位净值','股票型',rank=5)
df_e=etf_rank_china(info_type='单位净值',fund_type='全部类型',rank=10)
#=====================================================================
