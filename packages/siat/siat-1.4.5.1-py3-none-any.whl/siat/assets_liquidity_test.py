# -*- coding: utf-8 -*-

import os; os.chdir("S:\siat")
from siat import *
#==============================================================================
hn_cn={'Market':('China','000001.SS'),'601633.SS':1,'600104.SS':1,'002594.SZ':1}
rsp=roll_spread_portfolio(hn_cn,'2020-1-1','2021-11-30')
hb_cn={'Market':('China','000001.SS'),'600135.SS':2,'600559.SS':3,'600340.SS':1}
compare_liquidity_rolling(hn_cn,hb_cn,'2021-7-1','2021-11-30','roll_spread',30)

#==============================================================================
from siat.assets_liquidity import *

portfolio={'Market':('China','000001.SS'),'600011.SS':1}
start='2020-1-1'
end='2020-6-30'
liquidity_type='roll_spread'
l=liquidity_rolling(portfolio,start,end,liquidity_type,30)

ticker=['600011.SS']
start='2020-1-1'
end='2020-6-30'
pak=get_prices_ak(ticker,start,end)

pyf=get_price_yf(ticker,start,end)

pyh=p=get_prices_yahoo(ticker,start,end)

p=get_prices(ticker,start,end)

tickerlist=['600011.SS']
sharelist=[1]
p1=get_price_portfolio(tickerlist,sharelist,start,end)


if __name__=='__main__':
    tickerlist=['INTC','MSFT']
    sharelist=[0.6,0.4]
    fromdate='2020-11-1'
    todate='2021-1-31'

p2=get_prices_portfolio(tickerlist,sharelist,fromdate,todate)


