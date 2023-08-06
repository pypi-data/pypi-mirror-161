# -*- coding: utf-8 -*-

import os; os.chdir("S:/siat")
from siat.stock_china import *

#==============================================================================
import akshare as ak
l1=ticker[0]; market='sh'
if l1 in ['0','2','3']: market='sz'
df = ak.stock_individual_fund_flow(stock=ticker, market=market)
df.to_excel("D:/BFSU WORK/600519MFI.xlsx",index=False,encoding='utf-8',sheet_name='Sheet1')

if __name__=='__main__':
    ticker='600519'
    dfp=get_money_flowin(ticker)

    X,ydf=make_sample(dfp,ndays=1,preCumTimes=1)
    
    scaler_X1=preproc(X,preproctype='min-max')
    scaler_X2=preproc(X,preproctype='0-1')
    scaler_X3=preproc(X,preproctype='log')


#==============================================================================
ticker='600519'

forecast_direction_knn(ticker,ndays=5,max_neighbours=2,max_RS=2)

if __name__=='__main__':
    df=get_money_flowin(ticker)
    df=price_price_knn('600519',df,ndays=1,max_neighbours=3,max_RS=2)

forecast_price_knn(ticker,ndays=1,max_neighbours=2,max_RS=2)


forecast_direction_knn(ticker,ndays=5,max_neighbours=10,max_RS=10)
forecast_price_knn(ticker,ndays=5,max_neighbours=10,max_RS=10)
#==============================================================================