# -*- coding: utf-8 -*-

import os; os.chdir("S:/siat")
from siat import *
#==============================================================================
portfolio={'Market': ('US','^GSPC'),'AMZN':0.5,'EBAY':0.3,'WMT':0.2}
sr,rp=rar_ratio_portfolio(portfolio,'2021-1-1','2021-12-31',ratio_name='sharpe')




#==============================================================================

portfolio={'Market':('Israel','^TA125.TA'),'FIBI.TA':1.0}
r=rar_ratio_rolling(portfolio,'2021-1-1','2021-10-30',ratio_name='sharpe',window=120)

portfolio={'Market':('Israel','^TA125.TA'),'FIBI.TA':0.3,'TEVA.TA':0.7}
r=rar_ratio_rolling(portfolio,'2021-1-1','2021-10-30',ratio_name='sharpe',window=120)
r=rar_ratio_rolling(portfolio,'2021-1-1','2021-10-30',ratio_name='alpha',window=120)

portfolio={'Market':('US','^DJI'),'TEVA':1.0}
df=get_portfolio_prices(portfolio,'2020-4-1','2021-10-30')

start='2020-4-1'
end='2021-10-30'
portfolio={'Market':('China','^HSI'),'0823.HK':1.0}
r=rar_ratio_rolling(portfolio,'2021-7-1','2021-10-30',ratio_name='alpha',window=60)
r=rar_ratio_rolling(portfolio,'2021-7-1','2021-10-30',ratio_name='sharpe',window=60)
#==============================================================================
portfolio={'Market':('US','^GSPC'),'BABA':10,'PDD':7,'JD':5,'VIPS':1}
r=rar_ratio_rolling(portfolio,'2020-4-1','2021-3-31',ratio_name='treynor',window=60)
r=rar_ratio_rolling(portfolio,'2020-4-1','2021-3-31',ratio_name='sharpe',window=60)
r=rar_ratio_rolling(portfolio,'2020-4-1','2021-3-31',ratio_name='sortino',window=60)
r=rar_ratio_rolling(portfolio,'2020-4-1','2021-3-31',ratio_name='alpha',window=60)



#==============================================================================

portfolio={'Market':('US','^GSPC'),'TSLA':1.0}
#r=rar_ratio_rolling(portfolio,'2019-1-1','2020-12-31',ratio_name='treynor',window=30)
r=rar_ratio_rolling(portfolio,'2019-1-1','2020-12-31',ratio_name='sharpe',window=30)
r=rar_ratio_rolling(portfolio,'2019-1-1','2020-12-31',ratio_name='alpha',window=30)


df4=get_prices_yf(['AAPL','MSFT','IBM'],'2020-1-1','2020-12-31')
df4=get_prices_yf(tickerlist,'2020-1-1','2020-12-31')



pf1={'Market':('US','^GSPC'),'AAPL':1}
rars1=rar_ratio_rolling(pf1,'2019-12-1','2021-1-31',ratio_name='sharpe',window=30,graph=True)

tr1,rp1=rar_ratio_portfolio(pf1,'2019-01-01','2019-01-31',ratio_name='sharpe')


pf1={'Market':('US','^GSPC'),'AAPL':1}
pf2={'Market':('US','^GSPC'),'MSFT':1}    
rars12=compare_rar_portfolio(pf1,pf2,'2019-11-1','2020-11-30')
    
pfA={'Market':('China','000001.SS'),'600519.SS':1}
pfB={'Market':('China','000001.SS'),'000858.SZ':1}
rarsAB=compare_rar_portfolio(pfA,pfB,'2019-11-1','2020-11-30')
    
pfbb={'Market':('US','^GSPC'),'BABA':1}
pfjd={'Market':('US','^GSPC'),'JD':1}  
rarsbj=compare_rar_portfolio(pfbb,pfjd,'2019-11-1','2020-11-30')
    
pfbb={'Market':('US','^GSPC'),'BABA':1}
pfpd={'Market':('US','^GSPC'),'PDD':1}  
rarsbj=compare_rar_portfolio(pfbb,pfpd,'2019-11-1','2020-11-30')    

    
pf01={'Market':('US','^GSPC'),'BABA':0.5,'PDD':0.5}
pf02={'Market':('US','^GSPC'),'JD':0.5,'VIPS':0.5}  
rars12=compare_rar_portfolio(pf01,pf02,'2019-11-1','2020-11-30')      


pf01={'Market':('US','^GSPC'),'BABA':0.2,'VIPS':0.8}
pf02={'Market':('US','^GSPC'),'JD':0.6,'PDD':0.4}  
rars12=compare_rar_portfolio(pf01,pf02,'2019-11-1','2020-11-30')        
