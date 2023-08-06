# -*- coding: utf-8 -*-


import os; os.chdir("S:/siat")
from siat import *

portfolio={'Market':('China','000001.SS'),'000661.SZ':2,'603392.SS':3,'300601.SZ':4}
backtest_VaR_portfolio(portfolio,'2020-7-20',1, model="montecarlo")


vl,rl=get_VaR_portfolio(portfolio,'2020-7-20',1,0.99,model='all')


stock_quotes=get_stock_quotes('BABA','2021-11-1','2021-11-10')

df=get_prices('BABA','2021-11-1','2021-11-10')
get_prices('BABA','2021-11-1','2021-11-10')

var,ratio=stock_VaR_normal_standard('BABA',1000,'2019-8-8',1,0.99)

tlcps=series_VaR_tlcp(['GOOG','MSFT','AAPL'],'2020-7-20',0.99,model='montecarlo')

backtest_VaR(['AAPL'],[1000],'2020-7-20',1,model="normal_standard")





ticker=['000661.SZ', '603392.SS', '300601.SZ']
get_prices(ticker,'2019-7-19','2020-7-20')

prices=get_portfolio_prices(portfolio,'2019-7-19','2020-7-20')


var,ratio=stock_VaR_normal_standard('BABA',1000,'2019-8-8',1,0.99)


#==============================================================================
import os; os.chdir("S:/siat")
from siat import *

var,ratio=stock_VaR_normal_standard('BABA',1000,'2019-8-8',1,0.99)

tickerlist=['BABA','PDD','JD']
datelist=['2019-1-1','2019-2-1','2019-3-1','2019-4-1','2019-5-1','2019-6-1','2019-7-1']
compare_VaR_normal_standard(tickerlist,10000, datelist,1,0.99)

var, ratio=stock_VaR_normal_standard('BIDU',1000,'2020-7-1',1,0.99)
var,ratio=stock_VaR_normal_modified('BIDU',1000,'2020-7-1',1,0.99)

test=stock_ret_Normality_SW('BIDU','2020-1-1','2020-6-30')

plot_rets_curve('BIDU','2020-1-1','2020-6-30')

plot_rets_curve('1166.HK','2015-1-1','2015-3-31')

plot_rets_curve('0273.HK', '2011-4-1', '2011-6-30')

var, ratio=stock_VaR_normal_standard('ZM',1000,'2020-5-1',1,0.99)

var, ratio=stock_VaR_normal_modified('ZM',1000,'2020-5-1',1,0.99)
var, ratio=stock_VaR_historical_1d('ZM',1000,'2020-5-1',0.99)
test=stock_ret_Normality_SW('ZM','2020-1-1','2020-4-30', siglevel=0.05)
plot_rets_curve('ZM','2020-1-1','2020-4-30')

var, ratio=stock_VaR_historical_grouping('0992.HK',1000,'2020-5-1',1,0.99, pastyears=3)
var, ratio=stock_VaR_historical_grouping('0992.HK',1000,'2020-5-1',5,0.99, pastyears=3)
var, ratio=stock_VaR_historical_grouping('0992.HK',1000,'2020-5-1',10,0.99,pastyears=3)
var, ratio=stock_VaR_historical_grouping('0992.HK',1000,'2020-5-1',15,0.99,pastyears=3)

var, ratio=stock_VaR_montecarlo('1810.HK',1000,'2018-8-1',1,0.99)
var, ratio=stock_VaR_montecarlo('1810.HK',1000,'2018-8-1',5,0.99)

var, ratio=stock_VaR_montecarlo('1810.HK',1000,'2018-8-1',1,0.99,mctype='oversampling')
var, ratio=stock_VaR_montecarlo('1810.HK',1000,'2018-8-1',5,0.99,mctype='oversampling')
var, ratio=get_VaR_allmodels('1810.HK',1000,'2020-7-20',5,0.99)

test=stock_ret_Normality_SW('1810.HK','2020-4-20','2020-7-20')
backtest_VaR(['AAPL'], [1000],'2020-7-20',1, model="normal_standard")
backtest_VaR(['AAPL'], [1000],'2020-7-20',1, model="normal_modified")
backtest_VaR(['AAPL'], [1000],'2020-7-20',1, model="historical")
backtest_VaR(['AAPL'], [1000],'2020-7-20',1, model="montecarlo")

var, var_ratio=stock_VaR_normal_standard('JD',1000,'2019-8-9',1)
es, es_ratio=stock_ES_normal_standard('JD',1000,'2019-8-9',1)

portfolio={'Market':('China','000001.SS'),'000661.SZ':2,'603392.SS':3,'300601.SZ':4}
vl, rl=get_VaR_portfolio(portfolio,'2020-7-20',1,0.99, model='all')

portfolio_rets_curve(portfolio,'2019-7-20','2020-7-20')

portfolio={'Market':('China','000001.SS'),'300782.SZ':2,'300661.SZ':3,'688019.SS':4}
portfolio_rets_curve(portfolio,'2019-7-20','2020-7-20')

v, r=get_VaR_portfolio(portfolio,'2020-7-20',5,0.99, model='historical')
e, r=get_ES_portfolio(portfolio,'2020-7-20',5,0.99, model='historical')
